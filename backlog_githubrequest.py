import base64
import requests
import json
import time

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

        return self.request_with_retry(
            lambda: requests.post(url=url, data=json_data, headers=self.headers))


    def request_with_retry(self, request):
        retry_after_seconds = 30

        response = request()

        while response.status_code == 403:
            print(f"\n--- Got a 403 from Github. Sleeping for {retry_after_seconds} seconds ---")
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

            print(f'  {spinner} [{progress.ljust(ticks)}] {remaining}', end='\r')

            if count:
                time.sleep(0.5)

        print()


