import base64
import requests
import json

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
        response = requests.get(url=url, headers=self.headers)
        return response

    def post(self, url, data):
        json_data = json.dumps(data)
        response = requests.post(url=url, data=json_data, headers=self.headers)
        return response

