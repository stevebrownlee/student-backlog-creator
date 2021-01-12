import base64
import requests
import json
from backlog_githubrequest import GithubRequest

class RetroBoard(object):
    def __init__(self, config):
        self.config = config
        self.project_id = None
        self.grequest = GithubRequest(config)

    def create(self):
        # https://developer.github.com/v3/projects/#create-a-repository-project
        # POST /repos/:owner/:repo/projects

        project = {
            "name": self.config.get("retrospective", "name"),
            "body": "NSS Student Team Retrospective"
        }

        if self.config.has_option('target', 'repository'):
            target_text = self.config.get('target', 'repository')
            targets = [t.strip() for t in target_text.split(',')]
            for target in targets:
                github = self.config.get('server', 'base_url')
                url = f'{github}/repos/{target}/projects'
                res = self.grequest.post(url, project)

                if (res.status_code == requests.codes.created):
                    new_project = res.json()
                    self.project_id = new_project["id"]
                    print(
                        f'Project {new_project["name"]} with id {new_project["id"]} created on target repository')

                    self.create_columns(new_project["id"])
                else:
                    with open('response.txt', 'wb') as fd:
                        for chunk in res.iter_content(chunk_size=128):
                            fd.write(chunk)

                    print(f'Project creation failed')
                    print(res.text)

    def create_columns(self, project_id):
        # https://developer.github.com/v3/projects/columns/#create-a-project-column
        # POST /projects/:project_id/columns

        self.columns = json.loads(self.config.get('retrospective', 'columns'))

        url = f'https://api.github.com/projects/{project_id}/columns'

        for col in self.columns:
            data = {"name": col}
            url = url
            res = self.grequest.post(url, data)

            new_column = res.json()
            print(f'Column {new_column["name"]} added to project')
