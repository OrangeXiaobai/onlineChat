import base64
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_type = text_data_json['type']
        message = text_data_json.get('message', '')
        file_data = text_data_json.get('file_data', None)
        file_type = text_data_json.get('file_type', '')
        user_phone_number = text_data_json.get('user_phone_number', 'Anonymous')

        if file_data:
            file_content = base64.b64decode(file_data['data'].split(',')[1])
            file_path = default_storage.save(file_data['name'], ContentFile(file_content))
            file_url = default_storage.url(file_path)
            message = file_url

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'message_type': message_type,
                'file_type': file_type,
                'user_phone_number': user_phone_number
            }
        )

    async def chat_message(self, event):
        message = event['message']
        message_type = event['message_type']
        file_type = event['file_type']
        user_phone_number = event['user_phone_number']

        await self.send(text_data=json.dumps({
            'message': message,
            'message_type': message_type,
            'file_type': file_type,
            'user_phone_number': user_phone_number
        }))
