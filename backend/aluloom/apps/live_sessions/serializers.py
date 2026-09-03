"""
Serializers for Live Sessions.
"""

from rest_framework import serializers
from django.utils import timezone

from .models import LiveSession, SessionStatus, Attendance, SessionInvite


class LiveSessionSerializer(serializers.ModelSerializer):
    """Serializer for live sessions."""
    
    course_title = serializers.CharField(source='course.title_en', read_only=True)
    teacher_name = serializers.CharField(source='course.teacher.full_name', read_only=True)
    teacher_email = serializers.EmailField(source='course.teacher.email', read_only=True)
    is_startable = serializers.BooleanField(read_only=True)
    is_live = serializers.BooleanField(read_only=True)
    scheduled_end = serializers.DateTimeField(read_only=True)
    actual_duration_minutes = serializers.IntegerField(read_only=True)
    attendee_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = LiveSession
        fields = [
            'id', 'course', 'course_title', 'title', 'description',
            'course_type', 'teacher', 'teacher_name', 'teacher_email',
            'scheduled_start', 'scheduled_duration_minutes', 'scheduled_end',
            'actual_start', 'actual_end', 'actual_duration_minutes',
            'status', 'livekit_room_id', 'recording_url', 
            'max_attendees', 'attendee_count',
            'is_startable', 'is_live',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'livekit_room_id', 'actual_start', 'actual_end',
            'status', 'recording_url', 'attendee_count',
            'created_at', 'updated_at'
        ]


class LiveSessionCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating live sessions."""
    
    class Meta:
        model = LiveSession
        fields = [
            'course', 'title', 'description',
            'scheduled_start', 'scheduled_duration_minutes',
            'max_attendees'
        ]
    
    def validate_scheduled_start(self, value):
        """Ensure session is scheduled in the future."""
        if value < timezone.now():
            raise serializers.ValidationError(
                "Scheduled start time must be in the future."
            )
        return value
    
    def validate_scheduled_duration_minutes(self, value):
        """Ensure duration is reasonable."""
        if value < 15 or value > 480:  # 15 min to 8 hours
            raise serializers.ValidationError(
                "Duration must be between 15 and 480 minutes."
            )
        return value


class AttendanceSerializer(serializers.ModelSerializer):
    """Serializer for attendance records."""
    
    student_name = serializers.CharField(source='student.full_name', read_only=True)
    student_email = serializers.EmailField(source='student.email', read_only=True)
    duration_minutes = serializers.SerializerMethodField()
    
    class Meta:
        model = Attendance
        fields = [
            'id', 'session', 'student', 'student_name', 'student_email',
            'join_time', 'leave_time', 'duration_seconds', 'duration_minutes',
            'messages_sent', 'quiz_participated'
        ]
        read_only_fields = ['id', 'join_time', 'leave_time', 'duration_seconds']
    
    def get_duration_minutes(self, obj):
        if obj.duration_seconds:
            return round(obj.duration_seconds / 60, 2)
        return None


class SessionInviteSerializer(serializers.ModelSerializer):
    """Serializer for session invites."""
    
    session_title = serializers.CharField(source='session.title', read_only=True)
    user_name = serializers.CharField(source='user.full_name', read_only=True)
    is_expired = serializers.SerializerMethodField()
    
    class Meta:
        model = SessionInvite
        fields = [
            'id', 'session', 'session_title', 'user', 'user_name',
            'role', 'token', 'expires_at', 'used', 'used_at',
            'is_expired', 'created_at'
        ]
        read_only_fields = ['id', 'token', 'used', 'used_at', 'created_at']
    
    def get_is_expired(self, obj):
        return timezone.now() > obj.expires_at
