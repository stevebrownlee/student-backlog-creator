import os
import urllib.request
import urllib.error
import urllib.parse
import json
import base64
import datetime


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


# Will only import milestones and issues that are in use by the imported issues, and do not exist in the target repository
def import_issues(config, issues):

    state.current = state.GENERATING

    new_issues = []

    for issue in issues:

        new_issue = {}
        new_issue['title'] = issue['title']

        # Temporary fix for marking closed issues
        if issue['closed_at']:
            new_issue['title'] = "[CLOSED] " + new_issue['title']

        template_data = {}
        template_data['user_name'] = issue['user']['login']
        template_data['user_url'] = issue['user']['html_url']
        template_data['user_avatar'] = issue['user']['avatar_url']
        template_data['date'] = format_date(config, issue['created_at'])
        template_data['url'] = issue['html_url']
        template_data['body'] = issue['body']

        new_issue['body'] = format_issue(config, template_data)
        new_issues.append(new_issue)

    state.current = state.IMPORT_CONFIRMATION

    print("You are about to add to '" +
          config.get('target', 'repository') + "':")
    print(" *", len(new_issues), "new issues")

    state.current = state.IMPORTING

    result_issues = []
    for issue in new_issues:
        issue['labels'] = ['enhancement']
        result_issue = send_import_request(config, 'target', "issues", issue)
        print("Successfully created issue '%s'" % result_issue['title'])
        result_issues.append(result_issue)

    state.current = state.IMPORT_COMPLETE

    return result_issues


def format_from_template(template_filename, template_data):
    from string import Template
    template_file = open(template_filename, 'r')
    template = Template(template_file.read())
    return template.substitute(template_data)


def format_issue(config, template_data):
    __location__ = os.path.realpath(os.path.join(
        os.getcwd(), os.path.dirname(__file__)))
    default_template = os.path.join(__location__, 'templates', 'issue.md')
    template = config.get('format', 'issue_template',
                          fallback=default_template)
    return format_from_template(template, template_data)


def format_date(config, datestring):
    # The date comes from the API in ISO-8601 format
    date = datetime.datetime.strptime(datestring, "%Y-%m-%dT%H:%M:%SZ")
    date_format = config.get(
        'format', 'date', fallback='%A %b %d, %Y at %H:%M GMT', raw=True)
    return date.strftime(date_format)


def get_issues_by_state(config, which, state):
    issues = []
    page = 1
    while True:
        new_issues = send_import_request(
            config,
            which, "issues?state=%s&direction=asc&page=%d" % (state, page))
        if not new_issues:
            break
        issues.extend(new_issues)
        page += 1
    return issues


def get_issue_by_id(config, which, issue_id):
    return send_import_request(config, which, "issues/%d" % issue_id)


def get_issues_by_id(config, which, issue_ids):
    # Populate issues based on issue IDs
    issues = []
    issue_ids = issue_ids[0].split(" ")
    for issue_id in issue_ids:
        issues.append(get_issue_by_id(which, int(issue_id)))

    return issues


def send_import_request(config, which, url, post_data=None):

    if post_data is not None:
        post_data = json.dumps(post_data).encode("utf-8")

    full_url = "%s/%s" % (config.get(which, 'url'), url)
    req = urllib.request.Request(full_url, post_data)

    username = config.get(which, 'username')
    password = config.get(which, 'password')
    req.add_header("Authorization", b"Basic " + base64.urlsafe_b64encode(
        username.encode("utf-8") + b":" + password.encode("utf-8")))

    req.add_header("Content-Type", "application/json")
    req.add_header("Accept", "application/json")
    req.add_header("User-Agent", "nss/ticket-migrator")

    try:
        response = urllib.request.urlopen(req)
        json_data = response.read()
    except urllib.error.HTTPError as error:

        error_details = error.read()
        error_details = json.loads(error_details.decode("utf-8"))

        if error.code in http_error_messages:
            sys.exit(http_error_messages[error.code])
        else:
            error_message = "ERROR: There was a problem importing the issues.\n%s %s" % (
                error.code, error.reason)
            if 'message' in error_details:
                error_message += "\nDETAILS: " + error_details['message']
            sys.exit(error_message)

    return json.loads(json_data.decode("utf-8"))
