import requests
import threading


class LedgerRESTClient:

    def __init__(self, email, password, server_host='127.0.0.1'):
        self.email = email
        self.password = password

        self.server_host = f'http://{server_host}:8000'

        self.minutes_passed = 0
        self._auto_token_refresh()

    def _auto_token_refresh(self):
        if self.minutes_passed % 5 == 0:
            self.login()
        else:
            self.refresh_token()

        self.minutes_passed += 1

        if self.minutes_passed == 60:
            # 1시간에 한번씩 0으로 바꿔주기
            self.minutes_passed = 0

        timer = threading.Timer(60, self._auto_token_refresh)
        timer.setDaemon(True)
        timer.start()

    def login(self):
        params = {
            'email': self.email,
            'password': self.password
        }
        res = requests.post(f'{self.server_host}/api/token/', data=params)
        if res.status_code == 200:
            self.set_token(res.json())
        else:
            raise Exception('login failed')

    def refresh_token(self):
        params = {
            'refresh': self.refresh_token
        }
        res = requests.post(f'{self.server_host}/api/token/refresh/', data=params)
        if res.status_code == 200:
            self.set_token(res.json())
        else:
            raise Exception('token refresh failed')

    def set_token(self, res: dict):
        if 'refresh' in res:
            self.refresh_token = res['refresh']

        if 'access' in res:
            self.access_token = res['access']

        self.header = {'Authorization': f'Bearer {self.access_token}'}

    def get_user(self):
        res = requests.get(f'{self.server_host}/api/user/?email={self.email}')
        if res.status_code == 200:
            return res.json()


if __name__ == '__main__':
    c = LedgerRESTClient('ppark9553@naver.com', '123123')
    user = c.get_user()
    print(user)