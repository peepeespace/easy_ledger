# == Django Model Import ==#
import os
from asgiref.sync import sync_to_async
from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "api.settings")
application = get_wsgi_application()

from db.models import ClientSession

#== FastAPI Modules Import ==#
import json
import hashlib
from functools import partial
from typing import List, Dict
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


class ExecutionSessionManger:

    def __init__(self):
        self.sessions: Dict[str, WebSocket] = {}

    def add_session(self, session_id: str, websocket: WebSocket):
        self.sessions[session_id] = websocket

    def get_session(self, session_id: str):
        return self.sessions.get(session_id)

    def remove_session(self, websocket: WebSocket):
        for session_id in list(self.sessions.keys()):
            if self.sessions[session_id] == websocket:
                self.sessions.pop(session_id)
                break


MANAGER = ConnectionManager()
SESSION = ExecutionSessionManger()

@sync_to_async
def get_client_session(user_id):
    sessions = ClientSession.objects.filter(user=user_id).first()
    return sessions


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
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

                    client_session = await get_client_session(user_id)

                    if client_session.is_authenticated:
                        session_info = Fernet(client_session.key.encode('utf-8')).decrypt(
                            session.encode('utf-8')
                        )
                        session_id = hashlib.sha1(session_info).hexdigest()

                        if session_id == client_session.session_id:
                            SESSION.add_session(session_id, websocket)
                            print('Sessions: ', SESSION.sessions)
                            await send(json.dumps({'status': 'success', 'session_id': session_id}))
                        else:
                            await send(json.dumps({'status': 'failed', 'message': 'wrong session info. check again'}))

                elif data_type == 'ping':
                    session_id = data.get('session_id')

                    execution_session = SESSION.get_session(session_id)

                    if execution_session == websocket:
                        await send(json.dumps({'status': 'success', 'message': 'pong'}))
                    else:
                        await send(json.dumps({'status': 'failed', 'message': 'no existing session. make_connection first'}))

                else:
                    await send(json.dumps({'status': 'failed', 'message': 'wrong type field'}))

            except:
                await send(json.dumps({'status': 'failed', 'message': 'request should be made in json format'}))

    except WebSocketDisconnect:
        MANAGER.disconnect(websocket)
        SESSION.remove_session(websocket)
        print('Sessions: ', SESSION.sessions)