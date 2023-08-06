import json
import requests


class DiscordClient:
    api_base = 'https://discord.com/api/v10'
    login_url = f'{api_base}/auth/login'
    logout_url = f'{api_base}/auth/logout'
    settings_url = f'{api_base}/users/@me/settings'

    def __init__(self):
        self.__s = None

    def login(self, email, password):
        self.__s = requests.Session()
        payload = {'email': email, 'password': password}
        req = self.__s.post(self.login_url, data=json.dumps(payload),
                            headers={'Content-Type': 'application/json'})
        if req.status_code == 200:
            token = req.json()['token']
            self.__s.headers.update({'Authorization': token})
        return req.status_code == 200

    def logout(self):
        payload = {'provider': None, 'token': None}
        req = self.__s.post(self.logout_url, data=json.dumps(payload),
                            headers={'Content-Type': 'application/json'})
        self.__s = None
        return req.status_code in (200, 204)

    def update_status(self, status):
        payload = status
        req = self.__s.patch(self.settings_url, data=json.dumps(payload),
                             headers={'Content-Type': 'application/json'})
        return req.status_code == 200

    def get_status(self):
        req = self.__s.get(self.settings_url)
        if req.status_code != 200:
            return None
        status_keys = ('custom_status', 'status')
        return {k: v for k, v in req.json().items() if k in status_keys}
