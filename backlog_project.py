from time import sleep
import os
import requests
import json
from rich import print
from rich.progress import track
from backlog_githubrequest import GithubRequest


class ProjectBoard(object):
    def __init__(self, config):
        self.config = config
        self.project_id = None
        self.project_columns = []
        self.grequest = GithubRequest(config)

    def create(self, target):
        # https://developer.github.com/v3/projects/#create-a-repository-project
        # POST /repos/:owner/:repo/projects

        project = {
            "name": self.config.get("project", "name"),
            "body": "NSS Student Project"
        }

        github = self.config.get('server', 'base_url')
        url = f'{github}/repos/{target}/projects'
        res = self.grequest.post(url, project)

        if (res.status_code == requests.codes.created):
            new_project = res.json()
            self.project_id = new_project["id"]
            print(
                f'Project {new_project["name"]} with id {new_project["id"]} created on target repository')
            sleep(3)
        else:
            with open('response.txt', 'wb') as fd:
                for chunk in res.iter_content(chunk_size=128):
                    fd.write(chunk)

            print(f'Project creation failed')
            print(res.text)

    def create_columns(self):
        # https://developer.github.com/v3/projects/columns/#create-a-project-column
        # POST /projects/:project_id/columns

        self.columns = json.loads(self.config.get('project', 'columns'))

        url = f'https://api.github.com/projects/{self.project_id}/columns'

        for col in track(self.columns, description="Project board progress..."):
            data = {"name": col}
            url = url
            res = self.grequest.post(url, data)

            new_column = res.json()
            os.system('cls' if os.name == 'nt' else 'clear')
            print(f'Column {new_column["name"]} added to project')
            self.project_columns.append(new_column)

    def get_target_issues(self):
        # https://developer.github.com/v3/issues/#list-issues-for-a-repository
        # GET /repos/:owner/:repo/issues

        page = 1
        issues = []

        while True:
            url = f'{self.config.get("target", "url")}/issues?state=open&page={page}&direction=asc'
            res = self.grequests.get(url=url)
            new_issues = res.json()

            if not new_issues:
                break

            issues.extend(new_issues)
            page += 1

        return issues

    def add_target_issues_to_backlog(self, issues):
        # https://developer.github.com/v3/projects/cards/#create-a-project-card
        # POST /projects/columns/:column_id/cards
        # {
        #     "content_id": issue.id,
        #     "content_type": "Issue"
        # }

        backlog = self.project_columns[0]["id"]
        url = f'https://api.github.com/projects/columns/{backlog}/cards'

        # Reversing the order when adding to backlog column so that top priorities are listed first
        issues.reverse()

        os.system('cls' if os.name == 'nt' else 'clear')
        for issue in track(issues, description="Adding to backlog..."):

            sleep(5)

            data = {
                "content_id": issue["id"],
                "content_type": "Issue"
            }
            res = self.grequest.post(url, data)
            card = res.json()
            os.system('cls' if os.name == 'nt' else 'clear')
            print(f'Card {card["id"]} added to backlog from issue ticket {issue["number"]}')
