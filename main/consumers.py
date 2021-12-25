import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chat.settings')
django.setup()
import json
from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import User


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name

        # join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, code):
        # leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data=None, bytes_data=None):
        # Receive message from WebSocket
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )

    async def chat_message(self, event):
        # Receive message from room group
        message = event['message']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message
        }))


class UserAuthorizationConsumer(AsyncWebsocketConsumer):
    @sync_to_async
    def authorize(self, access_token, channel_name):
        user = User.exists(access_token=access_token)
        if user:
            user.channel_name = channel_name
            user.save()
            return user
        return None

    @sync_to_async
    def get_user_channel_name(self, phone_number):
        return User.exists(phone_number=phone_number).channel_name

    @sync_to_async
    def delete_socket_session(self, user: User):
        user.channel_name = ''
        user.save()

    async def connect(self):
        self.access_token = self.scope['url_route']['kwargs']['access_token']
        user = await self.authorize(self.access_token, self.channel_name)
        if user:
            self.connect_users_group = 'connected_users'
            self.user = user
            await self.accept()
        else:
            await self.close(None)

    async def disconnect(self, code):
        await self.close(code)
        # await  self.delete_socket_session(self.user)

    async def receive(self, text_data=None, bytes_data=None):
        # Receive message from WebSocket
        text_data_json = json.loads(text_data)
        type = text_data_json['type']


        if type == 'private_message':
            sender = text_data_json['sender']
            receiver = text_data_json['receiver']
            message = text_data_json['message']
            hash = text_data_json['hash']
            sender_channel_name = await self.get_user_channel_name(sender)
            receiver_channel_name = await self.get_user_channel_name(receiver)
            await self.channel_layer.send(
                sender_channel_name,
                {
                    'type': type,
                    'sender': sender,
                    'receiver': receiver,
                    'message': message,
                    'hash': hash,
                }
            )

            await self.channel_layer.send(
                receiver_channel_name,
                {
                    'type': type,
                    'sender': sender,
                    'receiver': receiver,
                    'message': message,
                    'hash': hash,
                }
            )
        elif type == 'delete_private_message':
            sender = text_data_json['sender']
            receiver = text_data_json['receiver']
            message = text_data_json['message']
            hash = text_data_json['hash']
            sender_channel_name = await self.get_user_channel_name(sender)
            receiver_channel_name = await self.get_user_channel_name(receiver)
            await self.channel_layer.send(
                sender_channel_name,
                {
                    'type': type,
                    'sender': sender,
                    'receiver': receiver,
                    'hash': hash,
                }
            )

            await self.channel_layer.send(
                receiver_channel_name,
                {
                    'type': type,
                    'sender': sender,
                    'receiver': receiver,
                    'hash': hash,
                }
            )



    async def private_message(self, event):
        # Receive message from room group
        type = event['type']
        sender = event['sender']
        receiver = event['receiver']
        message = event['message']
        hash = event['hash']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'type': type,
            'sender': sender,
            'receiver': receiver,
            'message': message,
            'hash': hash,
        }))

    async def delete_private_message(self, event):
        # Receive message from room group
        type = event['type']
        sender = event['sender']
        receiver = event['receiver']
        hash = event['hash']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'type': type,
            'sender': sender,
            'receiver': receiver,
            'hash': hash,
        }))
