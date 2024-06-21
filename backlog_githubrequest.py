import base64
import json
import time
import os
import requests
from requests.exceptions import ConnectionError
from rich import print
from rich.progress import track


class GithubRequest(object):
    def __init__(self, config):
        self.config = config

        username = config.get('login', 'username')
        password = config.get('login', 'password')
        credentials = f'{username}:{password}'.encode('utf-8')
        authorization = b'Basic ' + base64.urlsafe_b64encode(credentials)

        self.headers = {
            "Content-Type": "application/json",
            "Accept": config.get('server', 'media_type'),
            "User-Agent": "nss/ticket-migrator",
            "Authorization": authorization
        }

    def get(self, url):
        return self.request_with_retry(
            lambda: requests.get(url=url, headers=self.headers))

    def post(self, url, data):
        json_data = json.dumps(data)

        try:
            result = self.request_with_retry(
                lambda: requests.post(url=url, data=json_data, headers=self.headers))

            return result

        except TimeoutError:
            print("Request timed out. Trying next...")

        except ConnectionError:
            print("Request timed out. Trying next...")

        return None

    def request_with_retry(self, request):
        retry_after_seconds = 1800
        number_of_retries = 0

        response = request()

        while response.status_code == 403 and number_of_retries <= 10:
            number_of_retries += 1
            f = open("http.log", "a", encoding="utf-8")
            f.write(response.headers)
            f.write(json.dumps(response.json()))
            f.write("\n\n")
            f.close()

            os.system('cls' if os.name == 'nt' else 'clear')
            print(
                f"[deep_pink2]Got a 403 from Github. Sleeping for {retry_after_seconds} seconds[/deep_pink2]")
            self.sleep_with_countdown(retry_after_seconds)

            response = request()

        return response

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
