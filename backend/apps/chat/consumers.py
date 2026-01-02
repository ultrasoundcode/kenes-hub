import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from .models import ChatRoom, ChatMessage

User = get_user_model()


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'chat_{self.room_id}'
        
        # Проверяем доступ пользователя к комнате
        if await self.user_has_access():
            # Присоединяемся к группе
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            await self.accept()
        else:
            await self.close()

    async def disconnect(self, close_code):
        # Покидаем группу
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        message_type = text_data_json.get('type', 'message')
        
        user = self.scope['user']
        
        # Сохраняем сообщение в БД
        message_obj = await self.save_message(message, message_type)
        
        # Отправляем сообщение группе
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'message_type': message_type,
                'username': user.username,
                'full_name': user.get_full_name(),
                'timestamp': str(message_obj.created_at),
                'message_id': message_obj.id
            }
        )

    async def chat_message(self, event):
        # Отправляем сообщение WebSocket
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'message_type': event['message_type'],
            'username': event['username'],
            'full_name': event['full_name'],
            'timestamp': event['timestamp'],
            'message_id': event['message_id']
        }))

    @database_sync_to_async
    def user_has_access(self):
        """Проверяет, имеет ли пользователь доступ к комнате"""
        try:
            room = ChatRoom.objects.get(id=self.room_id)
            user = self.scope['user']
            return room.participants.filter(id=user.id).exists()
        except ChatRoom.DoesNotExist:
            return False

    @database_sync_to_async
    def save_message(self, message, message_type):
        """Сохраняет сообщение в БД"""
        room = ChatRoom.objects.get(id=self.room_id)
        return ChatMessage.objects.create(
            room=room,
            author=self.scope['user'],
            content=message,
            message_type=message_type
        )