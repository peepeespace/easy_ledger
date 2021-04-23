# == Django Model Import ==#
import os
from asgiref.sync import sync_to_async
from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "api.settings")
application = get_wsgi_application()

from user.models import User
from db.models import ClientSession

#== FastAPI Modules Import ==#
import zmq.asyncio

import json
import asyncio
import hashlib
import aio_pika
import traceback
from functools import partial
from typing import List, Dict
from aio_pika import ExchangeType
from cryptography.fernet import Fernet
from fastapi import FastAPI, WebSocket, WebSocketDisconnect


app = FastAPI()


class ConnectionManager:

    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)


class DataSessionManger:

    def __init__(self):
        self.sessions: List[WebSocket] = []

    def add_session(self, websocket: WebSocket):
        self.sessions.append(websocket)

    def remove_session(self, websocket: WebSocket):
        self.sessions.remove(websocket)

    async def publish(self, data: str, websocket: WebSocket = None):
        if websocket is None:
            for session in self.sessions:
                await session.send_text(data)
        else:
            await websocket.send_text(data)


class ActionSessionManger:

    def __init__(self):
        self.sessions: Dict[str, WebSocket] = {}
        self.user_info: Dict[str, dict] = {}

    def add_session(self,
                    session_id: str,
                    user_id: int,
                    username: str,
                    websocket: WebSocket):
        self.sessions[session_id] = websocket
        self.user_info[session_id] = {'id': user_id, 'username': username}

    def get_session(self, session_id: str):
        return self.sessions.get(session_id), self.user_info.get(session_id)

    def remove_session(self, websocket: WebSocket):
        for session_id in list(self.sessions.keys()):
            if self.sessions[session_id] == websocket:
                self.sessions.pop(session_id)
                self.user_info.pop(session_id)
                break


class SubscriptionSessionManger:

    def __init__(self):
        self.sessions: Dict[str, WebSocket] = {}
        self.action_session_info: Dict[str, str] = {}

    def add_session(self, session_id: str, action_session_id: str, websocket: WebSocket):
        self.sessions[session_id] = websocket
        self.action_session_info[session_id] = action_session_id

    def get_session(self, session_id: str):
        return self.sessions.get(session_id), self.action_session_info.get(session_id)

    def get_action_session_id(self, session_id: str):
        return self.action_session_info.get(session_id)

    def remove_session(self, websocket: WebSocket):
        for session_id in list(self.sessions.keys()):
            if self.sessions[session_id] == websocket:
                self.sessions.pop(session_id)
                self.action_session_info.pop(session_id)
                break


# Futures data streaming server
data_ctx = zmq.asyncio.Context()
DATA = data_ctx.socket(zmq.SUB)
DATA.connect('tcp://10.0.1.128:5567')
DATA.setsockopt_string(zmq.SUBSCRIBE, "")

# Ledger server
ledger_ctx = zmq.asyncio.Context()
LEDGER = ledger_ctx.socket(zmq.REQ)
LEDGER.connect('tcp://localhost:9999')

# Simulator execution server
simulator_ctx = zmq.asyncio.Context()
SIMULATOR = simulator_ctx.socket(zmq.REQ)
SIMULATOR.connect('tcp://localhost:9998')

MANAGER = ConnectionManager()
DAT_SESSION = DataSessionManger()
ACT_SESSION = ActionSessionManger()
SUB_SESSION = SubscriptionSessionManger()

LOOP = asyncio.get_event_loop()

@sync_to_async
def get_client_session(user_id: int, session_type: str):
    sessions = ClientSession.objects.filter(user=user_id, session_type=session_type).first()
    return sessions

@sync_to_async
def get_username(user_id):
    user = User.objects.filter(id=user_id).first()
    if user:
        return user.email


@app.websocket("/data")
async def data_endpoint(websocket: WebSocket):
    await MANAGER.connect(websocket)
    DAT_SESSION.add_session(websocket)
    try:
        while True:
            data = await DATA.recv_string()
            await DAT_SESSION.publish(data, websocket)
    except WebSocketDisconnect:
        MANAGER.disconnect(websocket)
        DAT_SESSION.remove_session(websocket)
        print('Data Sessions: ', DAT_SESSION.sessions)


@app.websocket("/action")
async def action_endpoint(websocket: WebSocket):
    await MANAGER.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()

            send = partial(MANAGER.send_personal_message, websocket=websocket)

            try:
                data = json.loads(data)

                data_type = data.get('type')

                if data_type is None:
                    await send(json.dumps({'status': 'failed', 'message': 'no type provided'}))

                elif data_type == 'make_connection':
                    user_id = data.get('user')
                    session = data.get('session', '')

                    client_session = await get_client_session(user_id, 'ACTION')

                    if client_session.is_authenticated:
                        session_info = Fernet(client_session.key.encode('utf-8')).decrypt(
                            session.encode('utf-8')
                        )
                        session_id = hashlib.sha1(session_info).hexdigest()

                        if session_id == client_session.session_id:
                            username = await get_username(user_id)
                            ACT_SESSION.add_session(session_id, user_id, username, websocket)
                            print('Sessions: ', ACT_SESSION.sessions)
                            await send(json.dumps({'status': 'success', 'session_id': session_id}))
                        else:
                            await send(json.dumps({'status': 'failed', 'message': 'wrong session info. check again'}))
                    else:
                        await send(json.dumps({'status': 'failed', 'message': 'wrong session info. check again'}))

                elif data_type == 'ping':
                    session_id = data.get('session_id')

                    execution_session, _ = ACT_SESSION.get_session(session_id)

                    if execution_session == websocket:
                        await send(json.dumps({'status': 'success', 'result': 'pong'}))
                    else:
                        await send(json.dumps({'status': 'failed', 'message': 'no existing session. make_connection first'}))

                elif data_type == 'ledger':
                    session_id = data.get('session_id')
                    method = data.get('method')
                    params = data.get('params', {})

                    execution_session, user_info = ACT_SESSION.get_session(session_id)

                    if execution_session == websocket:
                        req = {
                            'type': method,
                            'params': params
                        }

                        req['params'] = {**req['params'],
                                         'session_id': session_id,
                                         'username': user_info['username']}

                        await LEDGER.send_string(json.dumps(req))
                        raw_res = await LEDGER.recv_string()
                        res = json.loads(raw_res)

                        await send(json.dumps({'status': 'success', **res}))
                    else:
                        await send(json.dumps({'status': 'failed', 'message': 'no existing session. make_connection first'}))

                elif data_type == 'execution':
                    session_id = data.get('session_id')
                    source = data.get('source')
                    method = data.get('method')
                    params = data.get('params', {})

                    execution_session, _ = ACT_SESSION.get_session(session_id)

                    if execution_session == websocket:
                        if source == 'simulator':
                            req = {
                                'type': method,
                                'session_id': session_id,
                                'params': params
                            }

                            await SIMULATOR.send_string(json.dumps(req))
                            raw_res = await SIMULATOR.recv_string()
                            res = json.loads(raw_res)

                            await send(json.dumps({'status': 'success', **res}))
                    else:
                        await send(json.dumps({'status': 'failed', 'message': 'no existing session. make_connection first'}))

                else:
                    await send(json.dumps({'status': 'failed', 'message': 'wrong type field'}))

            except:
                traceback.print_exc()
                await send(json.dumps({'status': 'failed', 'message': 'request should be made in json format'}))

    except WebSocketDisconnect:
        MANAGER.disconnect(websocket)
        ACT_SESSION.remove_session(websocket)
        print('Action Sessions: ', ACT_SESSION.sessions)


@app.websocket("/subscription")
async def subscription_endpoint(websocket: WebSocket):
    await MANAGER.connect(websocket)

    try:
        while True:
            data = await websocket.receive_text()

            send = partial(MANAGER.send_personal_message, websocket=websocket)

            try:
                data = json.loads(data)

                data_type = data.get('type')

                if data_type is None:
                    await send(json.dumps({'status': 'failed', 'message': 'no type provided'}))

                elif data_type == 'make_connection':
                    user_id = data.get('user')
                    session = data.get('session', '')

                    client_session = await get_client_session(user_id, 'SUBSCRIPTION')

                    if client_session.is_authenticated:
                        session_info = Fernet(client_session.key.encode('utf-8')).decrypt(
                            session.encode('utf-8')
                        )
                        session_id = hashlib.sha1(session_info).hexdigest()

                        if session_id == client_session.session_id:
                            action_session = await get_client_session(user_id, 'ACTION')
                            SUB_SESSION.add_session(session_id, action_session.session_id, websocket)
                            print('Sessions: ', SUB_SESSION.sessions)
                            await send(json.dumps({'status': 'success', 'session_id': session_id}))
                        else:
                            await send(json.dumps({'status': 'failed', 'message': 'wrong session info. check again'}))
                    else:
                        await send(json.dumps({'status': 'failed', 'message': 'wrong session info. check again'}))

                elif data_type == 'start_stream':
                    session_id = data.get('session_id')

                    sub_session, act_session_id = SUB_SESSION.get_session(session_id)

                    if sub_session == websocket:
                        connection = await aio_pika.connect_robust(
                            'amqp://qraft:developer@localhost/',
                            loop=LOOP
                        )

                        def on_message(message):
                            print('consuming message')
                            print(message)

                        channel = await connection.channel()

                        exchange = await channel.declare_exchange('ledger_exchange', ExchangeType.TOPIC)
                        queue = await channel.declare_queue('ledger_queue')
                        await queue.bind(exchange, routing_key=act_session_id)
                        await queue.consume(on_message)

                        # channel = await connection.channel()
                        #
                        # queue = await channel.declare_queue('ledger')
                        #
                        # async with queue.iterator() as queue_iter:
                        #     async for message in queue_iter:
                        #         async with message.process():
                        #             message = message.body.decode('utf-8')
                        #             message = json.loads(message)
                        #             if message['session_id'] == act_session_id:
                        #                 await send(json.dumps(message))
                    else:
                        await send(json.dumps({'status': 'failed', 'message': 'no existing session. make_connection first'}))

                else:
                    await send(json.dumps({'status': 'failed', 'message': 'wrong type field'}))

            except:
                traceback.print_exc()
                await send(json.dumps({'status': 'failed', 'message': 'request should be made in json format'}))

    except WebSocketDisconnect:
        MANAGER.disconnect(websocket)
        SUB_SESSION.remove_session(websocket)
        print('Publisher Sessions: ', SUB_SESSION.sessions)
