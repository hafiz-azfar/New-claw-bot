"""
Messaging views for Al-Uloom Academy API.
"""

from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import CourseMessage, MessageFlag
from .serializers import (
    CourseMessageSerializer, MessageFlagSerializer,
    MessageFlagCreateSerializer
)
from users.permissions import IsOwnerOrAdmin, IsTeacher, IsStudent


class CourseMessageViewSet(viewsets.ModelViewSet):
    """ViewSet for course messages."""
    
    serializer_class = CourseMessageSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        course_id = self.kwargs.get('course_pk')
        user = self.request.user
        
        if user.role in ['owner', 'admin']:
            return CourseMessage.objects.filter(course_id=course_id, is_approved=True)
        elif user.role == 'teacher':
            # Teachers see all messages in their courses
            return CourseMessage.objects.filter(
                course_id=course_id,
                course__teacher=user,
                is_approved=True
            )
        else:  # student
            # Students see approved messages only
            return CourseMessage.objects.filter(
                course_id=course_id,
                is_approved=True
            )
    
    def perform_create(self, serializer):
        course_id = self.kwargs.get('course_pk')
        course = get_object_or_404('courses.Course', pk=course_id)
        
        if self.request.user.role not in ['owner', 'admin', 'teacher', 'student']:
            raise permissions.PermissionDenied("Only enrolled users can send messages.")
        
        serializer.save(course=course, sender=self.request.user)


class MessageFlagViewSet(viewsets.ModelViewSet):
    """ViewSet for message flags."""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return MessageFlagCreateSerializer
        return MessageFlagSerializer
    
    def get_queryset(self):
        user = self.request.user
        
        if user.role in ['owner', 'admin']:
            return MessageFlag.objects.all()
        elif user.role == 'teacher':
            # Teachers see flags for messages in their courses
            return MessageFlag.objects.filter(
                message__course__teacher=user
            )
        else:  # student
            # Students see only their own flags
            return MessageFlag.objects.filter(flagged_by=user)
    
    def perform_create(self, serializer):
        if self.request.user.role != 'student':
            raise permissions.PermissionDenied("Only students can flag messages.")
        
        serializer.save(flagged_by=self.request.user)
    
    @action(detail=True, methods=['post'], url_path='review')
    def review_flag(self, request, pk=None):
        """Review and resolve a flag (admin/teacher only)."""
        flag = self.get_object()
        
        if request.user.role not in ['owner', 'admin', 'teacher']:
            return Response(
                {'error': 'Only admins and teachers can review flags'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        resolution = request.data.get('resolution')
        if resolution not in ['dismissed', 'removed', 'warning_issued']:
            return Response(
                {'error': 'Invalid resolution type'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        from django.utils import timezone
        flag.reviewed_by = request.user
        flag.reviewed_at = timezone.now()
        flag.resolution = resolution
        flag.save()
        
        # If resolution is 'removed', hide the message
        if resolution == 'removed':
            flag.message.is_approved = False
            flag.message.save()
        
        return Response(MessageFlagSerializer(flag).data)
