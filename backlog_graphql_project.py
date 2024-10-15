import time
import json
from rich import print
from rich.progress import track
from backlog_github_graph_ql_request import GithubGraphQLRequest
from backlog_githubrequest import GithubRequest

class ProjectBoard:
    def __init__(self, config):
        self.config = config
        self.project_id = None
        self.project_columns = []
        self.grequest = GithubGraphQLRequest(config)
        self.request = GithubRequest(config)

    def get_cohort_org_node_id(self, org_name):
        result = self.request.get(f"https://api.github.com/orgs/{org_name}")
        if result:
            return result.json()["node_id"]
        else:
            print(f"Failed to get information for user {org_name}")
            return None

    def create(self, target):
        owner_id = self.get_cohort_org_node_id(self.config.get("target", "repository").split("/")[0])

        mutation = """
        mutation createProject($ownerId: ID!, $name: String!) {
            createProjectV2(input: {ownerId: $ownerId, title: $name }) {
                projectV2 {
                    id
                }
            }
        }
        """
        variables = {
            "ownerId": owner_id,
            "name": self.config.get("project", "name")
        }

        result = self.grequest.run_query(mutation, variables)

        if "errors" not in result:
            self.project_id = result["data"]["createProjectV2"]["projectV2"]["id"]
            print(f'Project {self.config.get("project", "name")} with id {self.project_id} created on target repository')
            time.sleep(3)
        else:
            print(f'Project creation failed')
            print(result["errors"])

