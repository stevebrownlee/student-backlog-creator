import requests
import json

class ProjectBoard(object):
    def __init__(self, config):
        self.config = config
        self.projects_url = f'{config.get("target", "url")}/projects'
        self.project_id = None

    def create(self, name):
        # https://developer.github.com/v3/projects/#create-a-repository-project
        # POST /repos/:owner/:repo/projects
        project = {
            "name": config.get("project", "name"),
            "body": "NSS Student Project"
        }
        res = requests.post(url=self.projects_url, data=project)
        if (res.status_code == requests.codes.created):
            print(f'Project {project['name']} created on target repository')
            self.project_id = res.json()["id"]
        else:
            print(f'Project creation failed')


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
