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
    def get_user_channel_name(self, country_code, phone_number):
        return User.exists(country_code=country_code,
                           phone_number=phone_number).channel_name

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

        sender_country_code = text_data_json['sender_country_code']
        sender_phone_number = text_data_json['sender_phone_number']
        receiver_country_code = text_data_json['receiver_country_code']
        receiver_phone_number = text_data_json['receiver_phone_number']

        if type == 'private_message':
            message = text_data_json['message']
            hash = text_data_json['hash']
            timestamp = text_data_json['timestamp']
            sender_channel_name = await self.get_user_channel_name(
                sender_country_code, sender_phone_number
            )
            receiver_channel_name = await self.get_user_channel_name(
                receiver_country_code, receiver_phone_number
            )
            await self.channel_layer.send(
                sender_channel_name,
                {
                    'type': type,
                    'sender_country_code': sender_country_code,
                    'sender_phone_number': sender_phone_number,
                    'receiver_country_code': receiver_country_code,
                    'receiver_phone_number': receiver_phone_number,
                    'message': message,
                    'hash': hash,
                    'timestamp': timestamp,
                }
            )

            await self.channel_layer.send(
                receiver_channel_name,
                {
                    'type': type,
                    'sender_country_code': sender_country_code,
                    'sender_phone_number': sender_phone_number,
                    'receiver_country_code': receiver_country_code,
                    'receiver_phone_number': receiver_phone_number,
                    'message': message,
                    'hash': hash,
                    'timestamp': timestamp,
                }
            )
        elif type == 'delete_private_message':
            hash = text_data_json['hash']
            sender_channel_name = await self.get_user_channel_name(
                sender_country_code, sender_phone_number
            )
            receiver_channel_name = await self.get_user_channel_name(
                receiver_country_code, receiver_phone_number
            )
            await self.channel_layer.send(
                sender_channel_name,
                {
                    'type': type,
                    'sender_country_code': sender_country_code,
                    'sender_phone_number': sender_phone_number,
                    'receiver_country_code': receiver_country_code,
                    'receiver_phone_number': receiver_phone_number,
                    'hash': hash,
                }
            )

            await self.channel_layer.send(
                receiver_channel_name,
                {
                    'type': type,
                    'sender_country_code': sender_country_code,
                    'sender_phone_number': sender_phone_number,
                    'receiver_country_code': receiver_country_code,
                    'receiver_phone_number': receiver_phone_number,
                    'hash': hash,
                }
            )

        elif type == 'message_delivered':
            hash = text_data_json['hash']

            receiver_channel_name = await self.get_user_channel_name(
                receiver_country_code, receiver_phone_number
            )

            await self.channel_layer.send(
                receiver_channel_name,
                {
                    'type': type,
                    'sender_country_code': sender_country_code,
                    'sender_phone_number': sender_phone_number,
                    'receiver_country_code': receiver_country_code,
                    'receiver_phone_number': receiver_phone_number,
                    'hash': hash,
                }
            )

        elif type == 'message_read':
            hash = text_data_json['hash']

            receiver_channel_name = await self.get_user_channel_name(
                receiver_country_code, receiver_phone_number
            )

            await self.channel_layer.send(
                receiver_channel_name,
                {
                    'type': type,
                    'sender_country_code': sender_country_code,
                    'sender_phone_number': sender_phone_number,
                    'receiver_country_code': receiver_country_code,
                    'receiver_phone_number': receiver_phone_number,
                    'hash': hash,
                }
            )

        elif type == 'image_message':
            image = text_data_json['image']
            timestamp = text_data_json['timestamp']
            hash = text_data_json['hash']
            sender_channel_name = await self.get_user_channel_name(
                sender_country_code, sender_phone_number
            )
            receiver_channel_name = await self.get_user_channel_name(
                receiver_country_code, receiver_phone_number
            )
            await self.channel_layer.send(
                sender_channel_name,
                {
                    'type': type,
                    'sender_country_code': sender_country_code,
                    'sender_phone_number': sender_phone_number,
                    'receiver_country_code': receiver_country_code,
                    'receiver_phone_number': receiver_phone_number,
                    'image': image,
                    'timestamp': timestamp,
                    'hash': hash,
                }
            )

            await self.channel_layer.send(
                receiver_channel_name,
                {
                    'type': type,
                    'sender_country_code': sender_country_code,
                    'sender_phone_number': sender_phone_number,
                    'receiver_country_code': receiver_country_code,
                    'receiver_phone_number': receiver_phone_number,
                    'image': image,
                    'timestamp': timestamp,
                    'hash': hash,
                }
            )

    async def private_message(self, event):
        # Receive message from room group
        type = event['type']
        sender_country_code = event['sender_country_code']
        sender_phone_number = event['sender_phone_number']
        receiver_country_code = event['receiver_country_code']
        receiver_phone_number = event['receiver_phone_number']
        message = event['message']
        hash = event['hash']
        timestamp = event['timestamp']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'type': type,
            'sender_country_code': sender_country_code,
            'sender_phone_number': sender_phone_number,
            'receiver_country_code': receiver_country_code,
            'receiver_phone_number': receiver_phone_number,
            'message': message,
            'hash': hash,
            'timestamp': timestamp,
        }))

    async def delete_private_message(self, event):
        # Receive message from room group
        type = event['type']
        sender_country_code = event['sender_country_code']
        sender_phone_number = event['sender_phone_number']
        receiver_country_code = event['receiver_country_code']
        receiver_phone_number = event['receiver_phone_number']
        hash = event['hash']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'type': type,
            'sender_country_code': sender_country_code,
            'sender_phone_number': sender_phone_number,
            'receiver_country_code': receiver_country_code,
            'receiver_phone_number': receiver_phone_number,
            'hash': hash,
        }))

    async def message_delivered(self, event):
        # Receive message from room group
        type = event['type']
        sender_country_code = event['sender_country_code']
        sender_phone_number = event['sender_phone_number']
        receiver_country_code = event['receiver_country_code']
        receiver_phone_number = event['receiver_phone_number']
        hash = event['hash']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'type': type,
            'sender_country_code': sender_country_code,
            'sender_phone_number': sender_phone_number,
            'receiver_country_code': receiver_country_code,
            'receiver_phone_number': receiver_phone_number,
            'hash': hash,
        }))

    async def message_read(self, event):
        # Receive message from room group
        type = event['type']
        sender_country_code = event['sender_country_code']
        sender_phone_number = event['sender_phone_number']
        receiver_country_code = event['receiver_country_code']
        receiver_phone_number = event['receiver_phone_number']
        hash = event['hash']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'type': type,
            'sender_country_code': sender_country_code,
            'sender_phone_number': sender_phone_number,
            'receiver_country_code': receiver_country_code,
            'receiver_phone_number': receiver_phone_number,
            'hash': hash,
        }))

    async def image_message(self, event):
        # Receive message from room group
        type = event['type']
        sender_country_code = event['sender_country_code']
        sender_phone_number = event['sender_phone_number']
        receiver_country_code = event['receiver_country_code']
        receiver_phone_number = event['receiver_phone_number']
        image = event['image']
        timestamp = event['timestamp']
        hash = event['hash']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'type': type,
            'sender_country_code': sender_country_code,
            'sender_phone_number': sender_phone_number,
            'receiver_country_code': receiver_country_code,
            'receiver_phone_number': receiver_phone_number,
            'image': image,
            'timestamp': timestamp,
            'hash': hash,
        }))
