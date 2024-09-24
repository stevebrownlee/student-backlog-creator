import time
import json
from rich import print
from rich.progress import track
from backlog_githubgrph_ql_request import GithubGraphQLRequest
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

    def create_columns(self):
        mutation = """
        mutation addProjectColumn($projectId: ID!, $name: String!) {
        addProjectV2Column(input: {projectId: $projectId, name: $name}) {
            projectV2Column {
            id
            }
        }
        }
        """

        self.columns = json.loads(self.config.get('project', 'columns'))

        for col in track(self.columns, description="Project board progress..."):
            variables = {
                "projectId": self.project_id,
                "name": col
            }
            result = self.grequest.run_query(mutation, variables)
            if "errors" not in result:
                new_column = result["data"]["addProjectV2ItemField"]["projectV2Item"]
                print(f'Column {col} added to project')
                self.project_columns.append(new_column)
            else:
                print(f'Failed to add column {col}')
                print(result["errors"])

    def get_target_issues(self):
        query = """
        query getRepoIssues($owner: String!, $name: String!, $cursor: String) {
            repository(owner: $owner, name: $name) {
                issues(first: 100, states: OPEN, orderBy: {field: CREATED_AT, direction: ASC}, after: $cursor) {
                    nodes {
                        id
                        number
                    }
                    pageInfo {
                        endCursor
                        hasNextPage
                    }
                }
            }
        }
        """

        owner, name = self.config.get("target", "url").split("/")[-2:]
        variables = {"owner": owner, "name": name}
        issues = []
        has_next_page = True
        cursor = None

        while has_next_page:
            variables["cursor"] = cursor
            result = self.grequest.run_query(query, variables)
            if "errors" not in result:
                data = result["data"]["repository"]["issues"]
                issues.extend(data["nodes"])
                has_next_page = data["pageInfo"]["hasNextPage"]
                cursor = data["pageInfo"]["endCursor"]
            else:
                print("Error fetching issues")
                print(result["errors"])
                break

        return issues

    def add_target_issues_to_backlog(self, issues):
        mutation = """
        mutation addIssueToProject($projectId: ID!, $contentId: ID!) {
            addProjectV2ItemById(input: {projectId: $projectId, contentId: $contentId}) {
                item {
                    id
                }
            }
        }
        """

        issues.reverse()

        for issue in track(issues, description="Adding to backlog..."):
            variables = {
                "projectId": self.project_id,
                "contentId": issue["id"]
            }
            result = self.grequest.run_query(mutation, variables)
            if "errors" not in result:
                card = result["data"]["addProjectV2ItemById"]["item"]
                print(f'Card {card["id"]} added to backlog from issue ticket {issue["number"]}')
            else:
                print(f'Failed to add issue {issue["number"]} to backlog')
                print(result["errors"])
            time.sleep(5)