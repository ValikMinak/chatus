# chat/consumers.py
import json

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

from chat.models import Message


class ChatConsumer(AsyncWebsocketConsumer):

    def __init__(self):
        self.room_group_name = "Pervomaysk"
        super().__init__()

    async def connect(self):
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    @database_sync_to_async
    def create_message(self, username, message):
        Message.objects.create(username=username, text=message)

    @database_sync_to_async
    def get_last_msg_username(self):
        last_msg = Message.objects.last()
        if last_msg:
            last_msg_username = last_msg.username
        else:
            last_msg_username = ''
        return last_msg_username

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        username = text_data_json['username']
        last_msg_username = await self.get_last_msg_username()
        await self.create_message(username, message)
        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'username': username if last_msg_username != username else '',
            }
        )

    # Receive message from room group
    async def chat_message(self, event):
        message = event['message']
        username = event['username']
        print(username)
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'chat',
            'message': message,
            'username': username
        }))
