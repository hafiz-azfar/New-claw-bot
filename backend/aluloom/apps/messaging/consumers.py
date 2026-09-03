"""
WebSocket consumers for real-time chat.
"""

import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class ChatConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for course chat."""
    
    async def connect(self):
        self.course_id = self.scope['url_route']['kwargs']['course_id']
        self.room_group_name = f'course_{self.course_id}'
        
        # Get user from token
        token = self.scope['query_string'].decode().split('token=')[1] if 'token=' in self.scope['query_string'].decode() else None
        if not token:
            await self.close()
            return
        
        try:
            access_token = AccessToken(token)
            self.user = await self.get_user(access_token['user_id'])
            if not self.user:
                await self.close()
                return
            
            # Check if user is enrolled or is teacher/admin
            is_authorized = await self.check_course_access(self.course_id, self.user)
            if not is_authorized:
                await self.close()
                return
                
        except Exception:
            await self.close()
            return
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Send welcome message
        await self.send(text_data=json.dumps({
            'type': 'connected',
            'user': str(self.user.email)
        }))
    
    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        data = json.loads(text_data)
        
        if data.get('type') == 'message':
            # Save message to database (async)
            message = await self.save_message(
                self.course_id,
                self.user,
                data.get('body'),
            )
            
            if message:
                # Broadcast message to room
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'message.new',
                        'message': message
                    }
                )
        elif data.get('type') == 'flag':
            # Handle message flagging
            await self.handle_flag(
                data.get('message_id'),
                data.get('reason')
            )
    
    async def message_new(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps(event))
    
    async def message_flagged(self, event):
        # Send flag notification to admins/teachers
        await self.send(text_data=json.dumps(event))
    
    @database_sync_to_async
    def get_user(self, user_id):
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None
    
    @database_sync_to_async
    def check_course_access(self, course_id, user):
        """Check if user has access to the course."""
        from aluloom.apps.courses.models import Course
        
        try:
            course = Course.objects.get(id=course_id)
            
            # Admins and owners have access to all courses
            if user.role in ['owner', 'admin']:
                return True
            
            # Teachers have access to their own courses
            if user.role == 'teacher' and course.teacher == user:
                return True
            
            # Students need to be enrolled (simplified - would need Enrollment model)
            if user.role == 'student' and course.status == 'published':
                return True
            
            return False
        except Course.DoesNotExist:
            return False
    
    @database_sync_to_async
    def save_message(self, course_id, user, body):
        """Save message to database."""
        from aluloom.apps.messaging.models import CourseMessage
        
        if not body or not body.strip():
            return None
        
        message = CourseMessage.objects.create(
            course_id=course_id,
            sender=user,
            content=body,
            is_approved=True  # Auto-approved by default
        )
        
        return {
            'id': str(message.id),
            'type': 'message.new',
            'message': {
                'id': str(message.id),
                'content': message.content,
                'sender': {
                    'id': str(message.sender.id),
                    'email': message.sender.email,
                    'name': message.sender.full_name,
                    'role': message.sender.role,
                },
                'created_at': message.created_at.isoformat(),
                'is_moderated': message.is_moderated,
            }
        }
    
    @database_sync_to_async
    def handle_flag(self, message_id, reason):
        """Handle message flagging."""
        from aluloom.apps.messaging.models import CourseMessage, MessageFlag
        
        try:
            message = CourseMessage.objects.get(id=message_id)
            MessageFlag.objects.create(
                message=message,
                flagged_by=self.user,
                reason=reason or 'Inappropriate content'
            )
            
            # Notify admins/teachers in the room
            # This would typically send a separate notification
            return True
        except CourseMessage.DoesNotExist:
            return False
