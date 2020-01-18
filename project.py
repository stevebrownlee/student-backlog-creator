import base64
import requests
import json


class ProjectBoard(object):
    def __init__(self, config):
        self.config = config
        self.project_id = None
        self.project_columns = []

        username = config.get('login', 'username')
        password = config.get('login', 'password')
        credentials = f'{username}:{password}'.encode('utf-8')
        authorization = b'Basic ' + base64.urlsafe_b64encode(credentials)

        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/vnd.github.inertia-preview+json",
            "User-Agent": "nss/ticket-migrator",
            "Authorization": authorization
        }

    def create(self):
        # https://developer.github.com/v3/projects/#create-a-repository-project
        # POST /repos/:owner/:repo/projects
        project = {
            "name": self.config.get("project", "name"),
            "body": "NSS Student Project"
        }

        url = f'{self.config.get("target", "url")}/projects'

        res = requests.post(url=url, data=json.dumps(
            project), headers=self.headers)

        if (res.status_code == requests.codes.created):
            new_project = res.json()
            self.project_id = new_project["id"]
            print(
                f'Project {new_project["name"]} with id {new_project["id"]} created on target repository')
        else:
            with open('response.txt', 'wb') as fd:
                for chunk in res.iter_content(chunk_size=128):
                    fd.write(chunk)

            print(f'Project creation failed')
            print(res.text)

    def get_column(self, column):
        # https://developer.github.com/v3/projects/columns/#get-a-project-column
        pass

    def create_columns(self):
        # https://developer.github.com/v3/projects/columns/#create-a-project-column
        # POST /projects/:project_id/columns

        self.columns = json.loads(self.config.get('project', 'columns'))

        url = f'https://api.github.com/projects/{self.project_id}/columns'
        # url = f'https://api.github.com/projects/3823604/columns'

        for col in self.columns:
            data = json.dumps({"name": col})
            url = url

            res = requests.post(url=url,
                                data=data, headers=self.headers)

            new_column = res.json()
            print(f'Column {new_column["name"]} added to project')
            self.project_columns.append(new_column)

    def get_target_issues(self):
        # https://developer.github.com/v3/issues/#list-issues-for-a-repository
        # GET /repos/:owner/:repo/issues

        url = f'{self.config.get("target", "url")}/issues?state=open'
        res = requests.get(url=url, headers=self.headers)
        target_issues = res.json()
        return target_issues


    def add_target_issues_to_backlog(self):
        # https://developer.github.com/v3/projects/cards/#create-a-project-card
        # POST /projects/columns/:column_id/cards
        # {
        #     "content_id": issue.id,
        #     "content_type": "Issue"
        # }
        issues = self.get_target_issues()
        backlog = self.project_columns[0]["id"]
        url = f'https://api.github.com/projects/columns/{backlog}/cards'
        print(f'Adding open issues to {url}')

        for issue in issues:
            data = {
                "content_id": issue["id"],
                "content_type": "Issue"
            }
            res = requests.post(url=url, data=json.dumps(data), headers=self.headers)
            card = res.json()
            print(f'Issue "{card["note"]}" added to backlog')

