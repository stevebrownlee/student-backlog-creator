import sys
import os
import query
import argparse
import configparser
from project import ProjectBoard
from issues import get_issues_by_id, get_issues_by_state, import_issues


__location__ = os.path.realpath(os.path.join(
    os.getcwd(), os.path.dirname(__file__)))
default_config_file = os.path.join(__location__, 'config.ini')
config = configparser.RawConfigParser()


class state:
    current = ""
    INITIALIZING = "script-initializing"
    LOADING_CONFIG = "loading-config"
    FETCHING_ISSUES = "fetching-issues"
    GENERATING = "generating"
    IMPORT_CONFIRMATION = "import-confirmation"
    IMPORTING = "importing"
    IMPORT_COMPLETE = "import-complete"
    COMPLETE = "script-complete"


state.current = state.INITIALIZING

http_error_messages = {}
http_error_messages[401] = "ERROR: There was a problem during authentication.\nDouble check that your username and password are correct, and that you have permission to read from or write to the specified repositories."
# Basically the same problem. GitHub returns 403 instead to prevent abuse.
http_error_messages[403] = http_error_messages[401]
http_error_messages[404] = "ERROR: Unable to find the specified repository.\nDouble check the spelling for the source and target repositories. If either repository is private, make sure the specified user is allowed access to it."


def init_config():

    config.add_section('login')
    config.add_section('source')
    config.add_section('target')
    config.add_section('format')
    config.add_section('settings')

    arg_parser = argparse.ArgumentParser(
        description="Import issues from one GitHub repository into another.")

    config_group = arg_parser.add_mutually_exclusive_group(required=False)
    config_group.add_argument(
        '--config', help="The location of the config file (either absolute, or relative to the current working directory). Defaults to `config.ini` found in the same folder as this script.")
    config_group.add_argument('--no-config', dest='no_config',  action='store_true',
                              help="No config file will be used, and the default `config.ini` will be ignored. Instead, all settings are either passed as arguments, or (where possible) requested from the user as a prompt.")

    arg_parser.add_argument(
        '-u', '--username', help="The username of the account that will create the new issues. The username will not be stored anywhere if passed in as an argument.")
    arg_parser.add_argument(
        '-p', '--password', help="The password (in plaintext) of the account that will create the new issues. The password will not be stored anywhere if passed in as an argument.")
    arg_parser.add_argument(
        '-s', '--source', help="The source repository which the issues should be copied from. Should be in the format `user/repository`.")
    arg_parser.add_argument(
        '-t', '--target', help="The destination repository which the issues should be copied to. Should be in the format `user/repository`.")

    include_group = arg_parser.add_mutually_exclusive_group(required=True)
    include_group.add_argument("--all", dest='import_all', action='store_true',
                               help="Import all issues, regardless of state.")
    include_group.add_argument(
        "--open", dest='import_open', action='store_true', help="Import only open issues.")
    include_group.add_argument("--closed", dest='import_closed',
                               action='store_true', help="Import only closed issues.")
    include_group.add_argument(
        "-i", "--issues", type=str, nargs='+', help="The list of issues to import.")

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

    if args.username:
        config.set('login', 'username', args.username)

    if args.password:
        config.set('login', 'password', args.password)

    if args.source:
        config.set('source', 'repository', args.source)

    if args.target:
        config.set('target', 'repository', args.target)

    config.set('settings', 'import-open-issues',
               str(args.import_all or args.import_open))
    config.set('settings', 'import-closed-issues',
               str(args.import_all or args.import_closed))

    # Make sure no required config values are missing
    if not config.has_option('source', 'repository'):
        sys.exit(
            "ERROR: There is no source repository specified either in the config file, or as an argument.")
    if not config.has_option('target', 'repository'):
        sys.exit(
            "ERROR: There is no target repository specified either in the config file, or as an argument.")

    def get_server_for(which):
        # Default to 'github.com' if no server is specified
        if (not config.has_option(which, 'server')):
            config.set(which, 'server', "github.com")

        # if SOURCE server is not github.com, then assume ENTERPRISE github (yourdomain.com/api/v3...)
        if (config.get(which, 'server') == "github.com"):
            api_url = "https://api.github.com"
        else:
            api_url = "https://%s/api/v3" % config.get(which, 'server')

        config.set(which, 'url', "%s/repos/%s" %
                   (api_url, config.get(which, 'repository')))

    get_server_for('source')
    get_server_for('target')

    # Prompt for username/password if none is provided in either the config or an argument

    def get_credentials_for(which):
        if not config.has_option(which, 'username'):
            if config.has_option('login', 'username'):
                config.set(which, 'username', config.get('login', 'username'))
            elif ((which == 'target') and query.yes_no("Do you wish to use the same credentials for the target repository?")):
                config.set('target', 'username',
                           config.get('source', 'username'))
            else:
                query_str = "Enter your username for '%s' at '%s': " % (
                    config.get(which, 'repository'), config.get(which, 'server'))
                config.set(which, 'username', query.username(query_str))

        if not config.has_option(which, 'password'):
            if config.has_option('login', 'password'):
                config.set(which, 'password', config.get('login', 'password'))
            elif ((which == 'target') and config.get('source', 'username') == config.get('target', 'username') and config.get('source', 'server') == config.get('target', 'server')):
                config.set('target', 'password',
                           config.get('source', 'password'))
            else:
                query_str = "Enter your password for '%s' at '%s': " % (
                    config.get(which, 'repository'), config.get(which, 'server'))
                config.set(which, 'password', query.password(query_str))

    get_credentials_for('source')
    get_credentials_for('target')

    # Everything is here! Continue on our merry way...
    return args.issues or []


if __name__ == '__main__':

    state.current = state.LOADING_CONFIG

    issue_ids = init_config()
    issues = []

    state.current = state.FETCHING_ISSUES

    # Argparser will prevent us from getting both issue ids and specifying issue state, so no duplicates will be added
    if (len(issue_ids) > 0):
        issues += get_issues_by_id(config, 'source', issue_ids)

    if config.getboolean('settings', 'import-open-issues'):
        issues += get_issues_by_state(config, 'source', 'open')

    if config.getboolean('settings', 'import-closed-issues'):
        issues += get_issues_by_state(config, 'source', 'closed')

    # Sort issues based on their original `id` field
    # Confusing, but taken from http://stackoverflow.com/a/2878123/617937
    issues.sort(key=lambda x: x['number'])

    # Further states defined within the function
    # Finally, add these issues to the target repository
    # import_issues(config, issues)
    project = ProjectBoard(config)
    project.create()

    state.current = state.COMPLETE
