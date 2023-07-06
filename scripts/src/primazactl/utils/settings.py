import json
import yaml
from primazactl.utils import logger

dry_run = False
output_yaml = False


def set(args):
    global dry_run
    global output_yaml
    if args.output_yaml == "yaml":
        print("set output)")
        output_yaml = True
    if args.dry_run:
        dry_run = True
    logger.log_info(f"Dry run: {dry_run}, Dry run yaml output: {output_yaml}")


def is_dry_run():
    return dry_run


def get_dry_run():
    if dry_run:
        return " (dry run) "
    else:
        return ""


def output(resource):
    if output_yaml:
        print(f"\n{yaml.dump(resource)}")
