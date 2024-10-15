import base64
import json
import time
import os
import requests
from requests.exceptions import ConnectionError
from rich import print
from rich.progress import track

class GithubGraphQLRequest:
    def __init__(self, config):
        self.config = config
        self.graphql_url = "https://api.github.com/graphql"
        self.rest_url = "https://api.github.com"

        username = config.get('login', 'username')
        password = config.get('login', 'password')
        credentials = f'{username}:{password}'.encode('utf-8')
        authorization = b'Basic ' + base64.urlsafe_b64encode(credentials)

        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/vnd.github+json",
            "User-Agent": "nss/ticket-migrator",
            "Authorization": authorization
        }

    def run_query(self, query, variables=None):
        json_data = {
            "query": query,
            "variables": variables or {}
        }

        return self.request_with_retry(
            lambda: requests.post(url=self.graphql_url, json=json_data, headers=self.headers)
        )

    def rest_get(self, endpoint):
        return self.request_with_retry(
            lambda: requests.get(url=f"{self.rest_url}{endpoint}", headers=self.headers)
        )

    def request_with_retry(self, request):
        retry_after_seconds = 1800
        number_of_retries = 0

        while number_of_retries <= 10:
            response = request()

            if response.status_code == 200:
                return response.json()
            elif response.status_code != 403:
                print(f"Request failed with status code: {response.status_code}")
                print(response.text)
                return None

            number_of_retries += 1
            with open("http.log", "a", encoding="utf-8") as f:
                f.write(str(response.headers))
                f.write(json.dumps(response.json()))
                f.write("\n\n")

            os.system('cls' if os.name == 'nt' else 'clear')
            print(
                f"[deep_pink2]Got a 403 from Github. Sleeping for {retry_after_seconds} seconds[/deep_pink2]")
            self.sleep_with_countdown(retry_after_seconds)

        return None

    def sleep_with_countdown(self, countdown_seconds):
        ticks = countdown_seconds * 2
        for count in range(ticks, -1, -1):
            remaining = str(int(0.5 + count / 2)).rjust(2)
            spinner = ['-', '/', '|', '\\'][count % 4]

            progress = '=' * (ticks - count)
            if count:
                progress = progress[:-1] + '>'

            print(
                f'[bright_white]  {spinner} [{progress.ljust(ticks)}] {remaining}[/bright_white]', end='\r')

            if count:
                time.sleep(0.5)

        print()

    def get_user_info(self, username):
        result = self.rest_get(f"/users/{username}")
        if result:
            print(result)
            exit()
            # return result
        else:
            print(f"Failed to get information for user {username}")
            return None

    def create_project(self):
        mutation = """
        mutation($ownerId: ID!, $title: String!) {
          createProjectV2(input: {ownerId: $ownerId, title: $title}) {
            projectV2 {
              id
            }
          }
        }
        """
        variables = {
            "ownerId": owner_id,
            "title": self.config.get('project', 'name')
        }
        result = self.run_query(mutation, variables)
        if result and "data" in result and "createProjectV2" in result["data"]:
            return result["data"]["createProjectV2"]["projectV2"]["id"]
        else:
            print(f"Failed to create project {project_name}")
            return None
