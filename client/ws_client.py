import json
import asyncio
import requests
import websockets
from cryptography.fernet import Fernet
from multiprocessing import Queue, Process


class LedgerWSClient:

    def __init__(self, email, password, server_host='127.0.0.1'):
        self.queue = Queue()
        self.tmp_queue = Queue()

        self.email = email
        self.password = password

        self.server_host = server_host

        p1 = Process(target=self.action_process, args=(self.queue, self.tmp_queue))
        p1.start()

        while True:
            _ = self.tmp_queue.get()
            break

        p2 = Process(target=self.subscription_process)
        p2.start()

    def send(self, data_type, **kwargs):
        self.queue.put({
            'type': data_type,
            **kwargs
        })

    def request_auth_token(self, session_type):
        params = {
            'username': self.email,
            'password': self.password,
            'session_type': session_type
        }
        res = requests.post(f'http://{self.server_host}:8000/api/user/login/', data=params)
        if res.status_code == 200:
            return res.json()
        else:
            print(res.json())
            raise Exception('socket session failed')

    def encrypt_auth_token(self, session_info):
        user_id = session_info['user']
        key = session_info['key']
        result = session_info['result']

        session_str = Fernet(key.encode('utf-8')).encrypt(
            json.dumps(result).encode('utf-8')
        )
        return json.dumps({
            'type': 'make_connection',
            'user': user_id,
            'session': session_str.decode('utf-8')
        })

    def subscription_process(self):
        session_info = self.request_auth_token(session_type='SUBSCRIPTION')
        asyncio.get_event_loop().run_until_complete(self.sub_ws_connect(session_info))

    async def sub_ws_connect(self, session_info):
        async with websockets.connect("ws://localhost:6000/subscription") as websocket:
            auth_token = self.encrypt_auth_token(session_info)
            await websocket.send(auth_token)
            res = await websocket.recv()
            res = json.loads(res)

            status = res['status']
            session_id = res['session_id']

            if status == 'success':
                await websocket.send(json.dumps({
                    'type': 'start_stream',
                    'session_id': session_id
                }))

            while True:
                data = await websocket.recv()
                print(json.loads(data))

    def action_process(self, queue, tmp_queue):
        session_info = self.request_auth_token(session_type='ACTION')
        asyncio.get_event_loop().run_until_complete(self.act_ws_connect(queue, tmp_queue, session_info))

    async def act_ws_connect(self, queue, tmp_queue, session_info):
        async with websockets.connect("ws://localhost:6000/action") as websocket:
            auth_token = self.encrypt_auth_token(session_info)
            await websocket.send(auth_token)

            res = await websocket.recv()
            res = json.loads(res)
            print(res)

            status = res['status']
            session_id = res['session_id']

            tmp_queue.put(session_id)

            if status == 'success':
                while True:
                    req = queue.get()
                    req = {**req, 'session_id': session_id}
                    await websocket.send(json.dumps(req))

                    res = await websocket.recv()
                    res = json.loads(res)
                    print(res)


if __name__ == '__main__':
    ws = LedgerWSClient('ppark9553@gmail.com', '123123!!')

    for i in range(10):
        ws.send('execution', source='simulator', method='send_order')