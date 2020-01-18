import base64
import requests
import json


class ProjectBoard(object):
    def __init__(self, config):
        self.config = config
        self.projects_url = f'{config.get("target", "url")}/projects'
        self.project_id = None

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

        res = requests.post(url=self.projects_url,
                            data=json.dumps(project), headers=self.headers)

        if (res.status_code == requests.codes.created):
            new_project = res.json()
            self.project_id = new_project["id"]
            print(f'Project {new_project["name"]} with id {new_project["id"]} created on target repository')
        else:
            with open('response.txt', 'wb') as fd:
                for chunk in res.iter_content(chunk_size=128):
                    fd.write(chunk)

            print(f'Project creation failed')
            print(res.text)


    def get_column(self, column):
        # https://developer.github.com/v3/projects/columns/#get-a-project-column
        pass

    def create_columns(self, name):
        # https://developer.github.com/v3/projects/columns/#create-a-project-column
        self.columns = config.get('project', 'columns')
        pass

    def create_column_card(self, issue, column):
        # https://developer.github.com/v3/projects/cards/#create-a-project-card
        pass
