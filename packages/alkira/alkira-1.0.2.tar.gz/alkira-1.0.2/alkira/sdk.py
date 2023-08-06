import requests
import os


class AlkiraSDK:
    def __init__(self, base_url="https://pmi.portal.alkira.com"):
        self.base_url = base_url
        self.session = requests.Session()

    def login(self, username=None, password=None):
        username = username or os.getenv("ALKIRA_USERNAME")
        password = password or os.getenv("ALKIRA_PASSWORD")

        login_url = f"{self.base_url}/api/login"
        payload = {
            "userName": username,
            "password": password
        }
        headers = {
            "Content-Type": "application/json",
            "Referer": self.base_url,
            "Origin": self.base_url
        }

        response = self.session.post(login_url, json=payload, headers=headers)
        if response.status_code != 200:
            raise Exception("Login failed")

    def get_tenant_networks(self):
        data_url = f"{self.base_url}/api/tenantnetworks"
        headers = {
            "Content-Type": "application/json",
            "Referer": self.base_url,
            "Origin": self.base_url
        }

        response = self.session.get(data_url, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception("Failed to retrieve tenant networks")

