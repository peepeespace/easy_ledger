import json
import asyncio
import websockets
from multiprocessing import Process, Queue

class WsClient:

    def __init__(self):
        self.q = Queue()

        p = Process(target=self.async_process)
        p.start()

        for i in range(0, 1):
            self.q.put({'type': 'Login', 'username': 'ppark9553@naver.com', 'password': '123123'})

        print('hello')

    def async_process(self):
        asyncio.get_event_loop().run_until_complete(self.connect(self.q))

    async def connect(self, queue):
        async with websockets.connect("ws://localhost:8000/ws") as websocket:
            while True:
                req = queue.get()
                await websocket.send(json.dumps(req))
                data = await websocket.recv()
                print(json.loads(data))


if __name__ == '__main__':
    c = WsClient()