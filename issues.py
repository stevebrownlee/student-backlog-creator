import termios
import tty
import sys
import os
import urllib.request
import urllib.error
import urllib.parse
import json
import base64
import datetime
import time
from githubrequest import GithubRequest
from project import ProjectBoard


http_error_messages = {}
http_error_messages[401] = "ERROR: There was a problem during authentication.\nDouble check that your username and password are correct, and that you have permission to read from or write to the specified repositories."
# Basically the same problem. GitHub returns 403 instead to prevent abuse.
http_error_messages[403] = http_error_messages[401]
http_error_messages[404] = "ERROR: Unable to find the specified repository.\nDouble check the spelling for the source and target repositories. If either repository is private, make sure the specified user is allowed access to it."


class Issues(object):
    def __init__(self, config, issue_ids):
        self.config = config
        self.issue_ids = issue_ids
        self.grequest = GithubRequest(config)

    def migrate_issues(self):
        source_issues = self.get_from_source()
        print(source_issues)

        issues_to_migrate = []

        for issue in source_issues:
            new_issue = {}
            new_issue['title'] = issue['title']

            template_data = {}
            template_data['user_name'] = issue['user']['login']
            template_data['user_url'] = issue['user']['html_url']
            template_data['user_avatar'] = issue['user']['avatar_url']
            template_data['date'] = self.format_date(issue['created_at'])
            template_data['url'] = issue['html_url']
            template_data['body'] = issue['body']

            new_issue['body'] = self.format_issue(template_data)
            issues_to_migrate.append(new_issue)

        organized_issues = self.organize_issues(issues_to_migrate)

        if self.config.has_option('target', 'repository'):
            target_text = self.config.get('target', 'repository')
            targets = [t.strip() for t in target_text.split(',')]
            for target in targets:
                time.sleep(1)
                self.send_to_target(target, organized_issues)
        else:
            target = None

            while True:
                os.system('cls' if os.name == 'nt' else 'clear')
                print("Target (i.e. account/repo). Enter x when done.")
                target = input("> ")
                if target == "x":
                    break
                self.send_to_target(target, organized_issues)

    def send_to_target(self, target, issues):
        target_issues = []
        github = self.config.get('server', 'base_url')
        url = f'{github}/repos/{target}/issues'

        os.system('cls' if os.name == 'nt' else 'clear')
        print(f'You are about to migrate {len(issues)} new issues to {target}')

        for issue in issues:
            issue['labels'] = ['enhancement']
            try:
                res = self.grequest.post(url, issue)
                result_issue = res.json()
                print(f'Successfully created issue \"{result_issue["title"]}\"')
                target_issues.append(result_issue)
            except KeyError as err:
                print(f'Error creating issue. {err}.')
                print(result_issue)

        project_manager = ProjectBoard(self.config)
        project_manager.create(target)
        project_manager.create_columns()
        project_manager.add_target_issues_to_backlog(target_issues)

    def get_from_source(self):
        issues = []

        if (len(self.issue_ids) > 0):
            issues.extend(self.get_issues_by_id())
        else:
            issues.extend(self.get_open_issues())

        # Sort issues based on their original `id` field
        issues.sort(key=lambda x: x['number'], reverse=True)

        return issues

    def organize_issues(self, issues):
        fd = sys.stdin.fileno()
        old = termios.tcgetattr(fd)
        old[3] = old[3] | termios.ECHO

        tty.setcbreak(sys.stdin)

        active_issue = 0
        issue_count = len(issues) - 1
        choice = None

        while choice != 10:
            os.system('cls' if os.name == 'nt' else 'clear')

            # k
            if choice == 107:
                if active_issue > 0:
                    active_issue -= 1

            # j
            if choice == 106:
                if active_issue < issue_count:
                    active_issue += 1

            # d
            if choice == 100:
                if active_issue < issue_count:
                    a, b = active_issue, active_issue + 1
                    issues[b], issues[a] = issues[a], issues[b]
                    active_issue += 1

            # u
            if choice == 117:
                if active_issue > 0:
                    a, b = active_issue - 1, active_issue
                    issues[b], issues[a] = issues[a], issues[b]
                    active_issue -= 1

            for idx, issue in enumerate(issues):
                if idx == active_issue:
                    print(f'(⭐️) {issue["title"]}')
                else:
                    print(f'(  ) {issue["title"]}')

            print('\n\nj=cursor up   k=cursor down   u=move up   d=move down')
            choice = ord(sys.stdin.read(1))

        termios.tcsetattr(fd, termios.TCSADRAIN, old)
        issues.reverse()
        return issues

    def format_from_template(self, template_filename, template_data):
        from string import Template
        template_file = open(template_filename, 'r')
        template = Template(template_file.read())
        return template.substitute(template_data)

    def format_issue(self, template_data):
        __location__ = os.path.realpath(os.path.join(
            os.getcwd(), os.path.dirname(__file__)))
        default_template = os.path.join(__location__, 'templates', 'issue.md')
        template = self.config.get('format', 'issue_template',
                                   fallback=default_template)
        return self.format_from_template(template, template_data)

    def format_date(self, datestring):
        # The date comes from the API in ISO-8601 format
        date = datetime.datetime.strptime(datestring, "%Y-%m-%dT%H:%M:%SZ")
        date_format = self.config.get(
            'format', 'date', fallback='%A %b %d, %Y at %H:%M GMT', raw=True)
        return date.strftime(date_format)

    def get_open_issues(self):
        # https://developer.github.com/v3/issues/#list-issues-for-a-repository
        # GET /repos/:owner/:repo/issues

        issues = []
        page = 1

        github = self.config.get('server', 'base_url')
        source = self.config.get('source', 'repository')

        url = f'{github}/repos/{source}/issues?state=open&direction=asc'
        print(url)

        while True:
            res = self.grequest.get(f'{url}&page={page}')
            new_issues = res.json()
            if not new_issues:
                break
            issues.extend(new_issues)
            page += 1

        return issues

    def get_issues_by_id(self):
        issues = []
        github = self.config.get('server', 'base_url')
        source = self.config.get('source', 'repository')

        for issue_id in self.issue_ids:
            url = f'{github}/repos/{source}/issues/{int(issue_id)}'
            print(url)
            res = self.grequest.get(url)
            content = res.json()
            new_issue = content if type(content) is dict else json.loads(content)
            issues.append(new_issue)

        return issues
