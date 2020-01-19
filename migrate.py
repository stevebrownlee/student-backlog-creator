import sys
import os
import query
import argparse
import configparser
from issues import Issues


__location__ = os.path.realpath(os.path.join(
    os.getcwd(), os.path.dirname(__file__)))
default_config_file = os.path.join(__location__, 'config.ini')
config = configparser.RawConfigParser()

def init_config():

    config.add_section('login')
    config.add_section('source')
    config.add_section('target')
    config.add_section('format')
    config.add_section('settings')
    config.add_section('server')

    arg_parser = argparse.ArgumentParser(
        description="Import issues from one GitHub repository into another.")

    config_group = arg_parser.add_mutually_exclusive_group(required=False)
    config_group.add_argument(
        '--config', help="The location of the config file (either absolute, or relative to the current working directory). Defaults to `config.ini` found in the same folder as this script.")
    config_group.add_argument('--no-config', dest='no_config',  action='store_true',
                              help="No config file will be used, and the default `config.ini` will be ignored. Instead, all settings are either passed as arguments, or (where possible) requested from the user as a prompt.")

    arg_parser.add_argument(
        '-s', '--source',
        help="The source repository which the issues should be copied from. Should be in the format `user/repository`.")
    arg_parser.add_argument(
        '-t', '--target',
        help="The destination repository which the issues should be copied to. Should be in the format `user/repository`.")
    arg_parser.add_argument(
        '-m', '--multiple',
        action='store_true',
        help="Set this flag if you want to import the issues into multiple target repositories.")

    include_group = arg_parser.add_mutually_exclusive_group(required=True)
    include_group.add_argument("-a", "--all", dest='import_all', action='store_true',
                               help="Import all open issues.")
    include_group.add_argument('-i', '--issues', nargs='+', type=int, help="The list of issues to import. (e.g. -i 1 5 6 10 15)")

    args = arg_parser.parse_args()

    def load_config_file(config_file_name):
        try:
            config_file = open(config_file_name)
            config.read_file(config_file)
            return True
        except (FileNotFoundError, IOError):
            return False

    if args.no_config:
        print(
            "Ignoring default config file. You may be prompted for some missing settings.")
    elif args.config:
        config_file_name = args.config
        if load_config_file(config_file_name):
            print("Loaded config options from '%s'" % config_file_name)
        else:
            sys.exit("ERROR: Unable to find or open config file '%s'" %
                     config_file_name)
    else:
        config_file_name = default_config_file
        if load_config_file(config_file_name):
            print("Loaded options from default config file in '%s'" %
                  config_file_name)
        else:
            print("Default config file not found in '%s'" % config_file_name)
            print("You may be prompted for some missing settings.")

    if args.source:
        config.set('source', 'repository', args.source)

    if args.target:
        config.set('target', 'repository', args.target)

    if args.multiple:
        config.set('settings', 'multiple', True)

    # Make sure no required config values are missing
    if not config.has_option('source', 'repository'):
        sys.exit(
            "ERROR: There is no source repository specified either in the config file, or as an argument.")
    if not args.multiple and not config.has_option('target', 'repository'):
        sys.exit(
            "ERROR: There is no target repository specified either in the config file, or as an argument, and the -m flag was not specified.")

    # Everything is here! Continue on our merry way...
    return args.issues or []



if __name__ == '__main__':

    issue_ids = init_config()
    issue_manager = Issues(config, issue_ids)
    issue_manager.migrate_issues()

