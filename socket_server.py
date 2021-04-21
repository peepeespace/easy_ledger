# == Django Model Import ==#
import os
from asgiref.sync import sync_to_async
from django.contrib.auth import authenticate
from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "api.settings")
application = get_wsgi_application()

from db.models import (
    Ledger,
    Strategy,
    Order,
    Fill,
    Position,
    Universe,
)
from rest_framework_simplejwt.tokens import RefreshToken

#== FastAPI Modules Import ==#
import json
from typing import List
from fastapi import FastAPI, WebSocket, WebSocketDisconnect


app = FastAPI()


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.connection_users: dict = {}

    def add_user(self, websocket: WebSocket, user):
        print(websocket)
        print(dir(websocket))
        print(websocket.session)
        self.connection_users[websocket] = user

    def get_user(self, websocket: WebSocket):
        return self.connection_users.get(websocket)

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        self.add_user(websocket, None)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        self.connection_users.pop(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)


manager = ConnectionManager()

@sync_to_async
def login(username, password):
    user = authenticate(username=username, password=password)
    return user

@sync_to_async
def get_ledger_count():
    return Ledger.objects.all().count()


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            data = json.loads(data)

            data_type = data.get('type')

            if data_type == 'Login':
                username = data.get('username')
                password = data.get('password')
                user = await login(username, password)
                if user is not None:
                    manager.add_user(websocket, user)
                await manager.send_personal_message({'success': 'added user to connection session'})

            if data_type == 'Ledger':
                ledgers = await get_ledger_count()
                print(ledgers)
                await manager.send_personal_message(f'ledger count: {ledgers}', websocket)
            # await manager.broadcast(f"Client says: {data}")

    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(f"Client left the chat")