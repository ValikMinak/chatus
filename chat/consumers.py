# chat/consumers.py
import json

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.core.cache import cache

from chat.models import Message


class ChatConsumer(AsyncWebsocketConsumer):

    ONLINE_STATUS_COLOR = 'greenyellow'

    def __init__(self):
        self.room_group_name = "Pervomaysk"
        super().__init__()

    async def connect(self):
        name = self.scope['cookies'].get('username')
        usernames = cache.get('usernames', [])
        if not usernames and name is not None:
            usernames.append(name)
            cache.set('usernames', usernames)
        else:
            if name and name not in usernames:
                usernames.append(name)
                cache.set('usernames', usernames)
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
        username = self.scope['cookies'].get('username')
        # Leave room group and delete username from cache
        if username:
            exists_usernames = cache.get('usernames', [])
            usernames = [x for x in exists_usernames if x != username]
            cache.set('usernames', usernames)
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)
        message = text_data_json.get('message')
        username = text_data_json.get('username')
        receive_type = text_data_json.get('type')
        status_color = text_data_json.get('status_color')

        last_msg_username = await self.get_last_msg_username()
        # Send message to room group
        if receive_type == 'chat':
            await self.create_message(username, message)
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message,
                    'username': username if last_msg_username != username else '',
                    'receive_type': receive_type,
                }
            )
        elif receive_type == 'update_status':
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'receive_type': receive_type,
                    'status_color': status_color,
                }
            )
        elif receive_type == 'enter_text':
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'receive_type': receive_type,
                    'username': username
                }
            )
        elif receive_type == 'empty_input':
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'receive_type': receive_type,
                    'username': username
                }
            )

    # Receive message from room group
    async def chat_message(self, event):
        message = event.get('message', '')
        username = event.get('username', '')
        receive_type = event.get('receive_type')
        usernames = cache.get('usernames', [])
        # Send message to WebSocket
        if receive_type == 'update_status':
            await self.send(text_data=json.dumps({
                'type': receive_type,
                'usernames': usernames,
                'status_color': self.ONLINE_STATUS_COLOR,
            }))
        elif receive_type == 'chat':
            await self.send(text_data=json.dumps({
                'type': receive_type,
                'message': message,
                'username': username,
                "status_color": self.ONLINE_STATUS_COLOR if username else ''
            }))
        elif receive_type == 'enter_text':
            await self.send(text_data=json.dumps({
                'type': receive_type,
                'username': username,
            }))
        elif receive_type == 'empty_input':
            await self.send(text_data=json.dumps({
                'type': receive_type,
                'username': username,
            }))
