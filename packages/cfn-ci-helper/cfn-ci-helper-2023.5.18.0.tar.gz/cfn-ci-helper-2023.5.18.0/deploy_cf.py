#!/usr/bin/env python3

"""
Script to Deploy the Specified configuration to the correct places (or specified places)
"""

import logging
import argparse
import sys
import os.path
import importlib.resources
import json

import boto3
import yaml
import texttable
import jinja2


import cfnStack

_region = "us-west-2"
_timeout = 180

if __name__ == "__main__":

    # Let's grab my runtime options

    parser = argparse.ArgumentParser()

    parser.add_argument("-p", "--only_profiles", help="Only deploy to these profiles even if more are configured.", default=[], action="append")
    parser.add_argument("-s", "--stackname", help="Stack Name to Deploy (Default Depoloy all in Category", default=[],
                        action="append")
    parser.add_argument("-C", "--confirm", help="Make Changes", default=False, action="store_true")
    parser.add_argument("-v", "--verbose", action="append_const", help="Verbosity Controls",
                        const=1, default=[])

    # "Live" Deployment Options
    parser.add_argument("--description", help="If using -S what description should go with the stack.",
                        default="No Description Given")
    parser.add_argument("--capabilities", help="If using -S what capabilities should go with the stack", default=[],
                        action="append")
    parser.add_argument("--regions", help="If using -S what regions should this deploy too", default=[],
                        action="append")
    parser.add_argument("--tags", help="If using -S what tags specified as tag:value to use", default=[],
                        action="append")
    parser.add_argument("--parameters", help="Parameters specified as param:value to use.", default=[],
                        action="append")
    parser.add_argument("--profiles", help="If using -S what profiles this should be deployed to.", default=[],
                        action="append")

    parser.add_argument("-D", "--stackdelete", help="Delete the Specified (Stacks)", default=False, action="store_true")

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-d", "--category", help="Which Cateogry to Choose from (directory)", default=None)
    group.add_argument("-c", "--config", help="Specify a Configuration File to Deploy", default=None)
    group.add_argument("-S", "--stack", help="Specify a single Stack file deploy", default=None)

    args = parser.parse_args()

    VERBOSE = len(args.verbose)

    EXTRA_MODULES = ["boto3", "urllib3", "botocore",
                     "botocore.hooks", "botocore.retryhandler"]

    extra_level = logging.ERROR

    if VERBOSE == 0:
        logging.basicConfig(level=logging.ERROR)
    elif VERBOSE == 1:
        logging.basicConfig(level=logging.WARNING)
        extra_level = logging.ERROR
    elif VERBOSE == 2:
        logging.basicConfig(level=logging.INFO)
        extra_level = logging.WARNING
    elif VERBOSE == 3:
        logging.basicConfig(level=logging.DEBUG)
        extra_level = logging.INFO
    elif VERBOSE == 4:
        logging.basicConfig(level=logging.DEBUG)
        extra_level = logging.DEBUG

    for mod in EXTRA_MODULES:
        logging.getLogger(mod).setLevel(extra_level)

    logger = logging.getLogger("deploy_cf")

    if args.category is not None:
        if os.path.isdir(args.category) is False:
            logger.error("Unable to Find Cateogry Directory : {}".format(args.category))
            sys.exit(1)
        else:
            logger.debug("Working in Category: {}".format(args.category))
            config_file = os.path.join(args.category, "config.yaml")

        with open(config_file) as config_fobj:
            category_configs = yaml.safe_load(config_fobj)

    elif args.config is not None:
        if os.path.isfile(args.config) is False:
            logger.error("Unable to Find Configuration File : {}".format(args.category))
            sys.exit(1)
        else:
            logger.debug("Categories not in Usein a direct yaml config : {}.".format(args.config))
            config_file = args.config

        with open(config_file) as config_fobj:
            category_configs = yaml.safe_load(config_fobj)

    elif args.stack is not None:
        if os.path.isfile(args.stack) is False:
            logger.error("Cannot Find Direct Stack Configuration : {}".format(args.stack))
        else:
            logger.debug("Using default configuration for direct stack.")

            render_data = dict(filename=args.stack,
                               description=args.description,
                               capabilities=args.capabilities,
                               parameters=args.parameters,
                               tags=args.tags)

            if len(args.profiles) == 0:
                render_data["profiles"] = ["default"]
            else:
                render_data["profiles"] = args.profiles

            if len(args.regions) == 0:
                render_data["regions"] = [_region]
            else:
                render_data["regions"] = args.regions

            with importlib.resources.path(cfnStack, "default_stack.yaml.jinja") as stack_template_path:
                with open(stack_template_path, "r") as stack_template_fobj:
                    stack_template_str = stack_template_fobj.read()

                    config_template = jinja2.Environment(loader=jinja2.BaseLoader,
                                                         autoescape=jinja2.select_autoescape(
                                                             enabled_extensions=('html', 'xml'),
                                                             default_for_string=False
                                                         )).from_string(stack_template_str)

                    config_rendered = config_template.render(**render_data)

                    logger.debug("Live Rendered: {}".format(config_rendered))

                    category_configs = yaml.safe_load(config_rendered)

                    logger.debug("configs: {}".format(category_configs))

    # Parse Live Add Options
    live_add = dict(parameters={})

    for param in args.parameters:

        param_key, param_val = param.split(":", 1)
        logger.debug("Adding Parameter {}".format(param_key))
        live_add["parameters"][param_key] = param_val


    wanted_stacks = list()
    if len(args.stackname) == 0:
        # Take All Stacks
        wanted_stacks = list(category_configs.keys())
    else:
        wanted_stacks = [stack for stack in args.stackname if stack in category_configs.keys()]

        missing_stacks = [mstack for mstack in args.stackname if mstack not in category_configs.keys()]

        if len(missing_stacks) > 0:
            logger.error(
                "Requested Stack(s) {} not requested configured in category {}".format(",".join(missing_stacks),
                                                                                       args.category))
            logger.debug("Exiting early.")
            sys.exit(2)

    action_tuples = list()

    for wstack in wanted_stacks:

        this_config = category_configs[wstack]

        this_config_file = os.path.join(args.category, this_config["file"])

        with open(this_config_file, "r") as stack_config_file_obj:
            stack_config_json = stack_config_file_obj.read()

        if len(args.only_profiles) == 0:
            # Take all Configured Profiles
            wprofiles = category_configs[wstack]["profiles"]

        else:
            wprofiles = [prof for prof in args.only_profiles if prof in category_configs[wstack]["profiles"]]

            mprofiles = [prof for prof in args.only_profiles if prof not in category_configs[wstack]["profiles"]]

            if len(mprofiles) > 0:
                logger.error("{} missing requested profiles {}.".format(wstack,
                                                                        ",".join(
                                                                            mprofiles)))
                sys.exit(3)

        wregions = this_config.get("regions", [_region])

        if isinstance(wregions, str) and wregions.startswith("all"):
            wregions = [wregions]

        for wprofile in wprofiles:

            this_wregions = wregions

            if len(wregions) == 1 and wregions[0].startswith("all"):
                # Get and Wrap All Regions
                fast_service_name="cloudformation"

                if ":" in wregions[0]:
                    fast_service_name = wregions[0].split(":")[1]

                logger.warning("Deployment requested to all regions for service: {}".format(fast_service_name))
                fast_session = aws_session = boto3.session.Session(profile_name=wprofile)
                this_wregions = fast_session.get_available_regions(service_name=fast_service_name)
                logger.info("Expanding to {} regions for profile {}".format(len(this_wregions), wprofile))
                logger.debug("Wanted Regions for Profile {}, {}".format(wprofile, ", ".join(this_wregions)))
            # else
                # I can use the list of regions

            for wregion in this_wregions:
                action_tuples.append({"stack": wstack,
                                      "stack_cfg": this_config,
                                      "region": wregion,
                                      "profile": wprofile,
                                      "stack_config_json": stack_config_json,
                                      "delete": args.stackdelete})

    logger.info("Requesting Modifications for {} Stacks/Profile Combinations".format(len(action_tuples)))
    # logger.debug("Requested Stack/Profile Combinations.\n{}".format(json.dumps(action_tuples, indent=2)))

    result_table = texttable.Texttable(max_width=160)
    result_table.add_row(["stack", "profile", "region", "aws", "stack_valid", "changes", "action", "f_triggered"])

    should_break = False

    for action_tuple in action_tuples:
        this_result = cfnStack.ProcessStack(action_tuple,
                                            confirm=args.confirm,
                                            live_add=live_add)

        if this_result.return_status["fail"] is True:
            should_break = True

        result_table.add_row(this_result.return_table_row())

    print(result_table.draw())

    if should_break is True:
        logger.error("One or more stacks had an abnormal response.")
        sys.exit(1)
