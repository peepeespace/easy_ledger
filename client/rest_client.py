import json
import asyncio
import requests
import threading
import websockets
from cryptography.fernet import Fernet
from multiprocessing import Queue, Process


class LedgerRESTClient:

    def __init__(self, email, password, server_host='127.0.0.1'):
        self.queue = Queue()

        self.email = email
        self.password = password

        self.server_host = f'http://{server_host}:8000'

        self.minutes_passed = 0
        # self._auto_token_refresh()

        p1 = Process(target=self.websocket_connection_process, args=(self.queue,))
        p1.start()

        p2 = Process(target=self.subscription_connection_process)
        p2.start()

    def _auto_token_refresh(self):
        if self.minutes_passed % 5 == 0:
            self.login()
        else:
            self._refresh_token()

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

    def _refresh_token(self):
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

    #=== Websocket Related ===#
    def send(self, data_type, **kwargs):
        self.queue.put({
            'type': data_type,
            **kwargs
        })

    def make_socket_session(self):
        params = {
            'username': self.email,
            'password': self.password
        }
        res = requests.post(f'{self.server_host}/api/user/login/', data=params)
        if res.status_code == 200:
            return res.json()
        else:
            print(res.json())
            raise Exception('socket session failed')

    def subscription_connection_process(self):
        asyncio.get_event_loop().run_until_complete(self.sub_ws_connect())

    async def sub_ws_connect(self):
        async with websockets.connect("ws://localhost:6000/sub") as websocket:
            await websocket.send(json.dumps({
                'type': 'make_connection',
                'session_id': ''
            }))

            while True:
                data = await websocket.recv()
                print(json.loads(data))

    def websocket_connection_process(self, queue):
        session_info = self.make_socket_session()
        asyncio.get_event_loop().run_until_complete(self.ws_connect(queue, session_info))

    async def ws_connect(self, queue, session_info):
        async with websockets.connect("ws://localhost:6000/ws") as websocket:
            user_id = session_info['user']
            key = session_info['key']
            result = session_info['result']

            session_str = Fernet(key.encode('utf-8')).encrypt(
                json.dumps(result).encode('utf-8')
            )
            await websocket.send(json.dumps({
                'type': 'make_connection',
                'user': user_id,
                'session': session_str.decode('utf-8')
            }))

            res = await websocket.recv()
            res = json.loads(res)

            status = res['status']
            session_id = res['session_id']

            if status == 'success':
                while True:
                    req = queue.get()
                    req = {**req, 'session_id': session_id}
                    await websocket.send(json.dumps(req))

                    res = await websocket.recv()
                    res = json.loads(res)
                    print(res)


if __name__ == '__main__':
    c = LedgerRESTClient('ppark9553@naver.com', '123123!!')

    ledger_name = 'my_first_ledger_1'
    strategy_name = 'strat_1'

    base = {'ledger_name': ledger_name, 'strategy_name': strategy_name}

    c.send('ledger', method='add_ledger', params={'ledger_name': ledger_name})
    c.send('ledger', method='get_cash', params={**base})
    # c.send('ledger', method='update_cash', params={'ledger_name': ledger_name, 'strategy_name': strategy_name, 'amount': 1000})
    # c.send('ledger', method='get_cash', params={'ledger_name': ledger_name, 'strategy_name': strategy_name})
    # c.send('ledger', method='get_orders', params={'ledger_name': ledger_name, 'strategy_name': strategy_name})

    c.send('ledger', method='get_position', params={**base, 'symbol': '005930'})
    # c.send('ledger', method='update_position', params={**base, 'symbol': '005930', 'side': 'BUY', 'price': 100, 'quantity': 12, 'position_amount': 100, 'order_state': 'filled'})
    # c.send('ledger', method='get_position', params={**base, 'symbol': '005930'})


    c.send('execution', source='simulator', method='send_order')
