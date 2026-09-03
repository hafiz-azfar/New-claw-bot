"""
Messaging serializers for Al-Uloom Academy API.
"""

from rest_framework import serializers
from .models import CourseMessage, MessageFlag


class CourseMessageSerializer(serializers.ModelSerializer):
    """Serializer for course messages."""
    
    sender_email = serializers.CharField(source='sender.email', read_only=True)
    sender_name = serializers.CharField(source='sender.full_name', read_only=True)
    sender_role = serializers.CharField(source='sender.role', read_only=True)
    
    class Meta:
        model = CourseMessage
        fields = [
            'id', 'course', 'sender', 'sender_email', 'sender_name',
            'sender_role', 'content', 'is_moderated', 'is_approved',
            'created_at', 'edited_at'
        ]
        read_only_fields = ['id', 'created_at', 'is_approved']


class MessageFlagSerializer(serializers.ModelSerializer):
    """Serializer for message flags."""
    
    flagged_by_email = serializers.CharField(source='flagged_by.email', read_only=True)
    reviewed_by_email = serializers.CharField(source='reviewed_by.email', read_only=True)
    message_content = serializers.CharField(source='message.content', read_only=True)
    
    class Meta:
        model = MessageFlag
        fields = [
            'id', 'message', 'message_content', 'flagged_by',
            'flagged_by_email', 'reason', 'created_at',
            'reviewed_by', 'reviewed_by_email', 'reviewed_at',
            'resolution'
        ]
        read_only_fields = ['id', 'created_at', 'reviewed_at']


class MessageFlagCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating message flags."""
    
    class Meta:
        model = MessageFlag
        fields = ['message', 'reason']
    
    def validate_reason(self, value):
        if not value or len(value.strip()) < 10:
            raise serializers.ValidationError("Please provide a detailed reason (at least 10 characters).")
        return value
