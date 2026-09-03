"""
Views for Live Sessions - The Zoom/Teams Killer.
Provides API endpoints for managing live virtual classrooms.
"""

from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Q

from .models import LiveSession, SessionStatus, Attendance, SessionInvite
from .serializers import (
    LiveSessionSerializer, 
    LiveSessionCreateSerializer,
    AttendanceSerializer,
    SessionInviteSerializer
)
from .services import livekit_service
from ..courses.models import Course
from ..users.models import User


class IsTeacherOrAdmin(permissions.BasePermission):
    """Permission for teachers and admins."""
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ['teacher', 'admin', 'owner']


class IsEnrolledStudent(permissions.BasePermission):
    """Permission for enrolled students."""
    
    def has_object_permission(self, request, view, obj):
        if request.user.role in ['admin', 'owner']:
            return True
        if request.user.role == 'teacher' and obj.course.teacher == request.user:
            return True
        # Students need to be enrolled (simplified check)
        return request.user.role == 'student' and obj.course.status == 'published'


class LiveSessionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing live sessions.
    
    Why this beats Zoom/Teams:
    - Integrated with LMS (no separate app needed)
    - Auto-recording to your own storage (no cloud fees)
    - Moderated chat built-in
    - MCQ quizzes during sessions
    - Unlimited duration (no 40-minute limit)
    - No per-host pricing
    - Full attendance tracking
    - Data sovereignty (self-hosted)
    """
    
    queryset = LiveSession.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return LiveSessionCreateSerializer
        return LiveSessionSerializer
    
    def get_queryset(self):
        """Filter sessions based on user role."""
        user = self.request.user
        queryset = LiveSession.objects.select_related('course', 'teacher', 'created_by')
        
        if user.role in ['admin', 'owner']:
            return queryset
        elif user.role == 'teacher':
            return queryset.filter(course__teacher=user)
        else:  # student
            return queryset.filter(
                course__status='published',
                scheduled_start__lte=timezone.now() + timezone.timedelta(days=30)
            )
    
    def create(self, request, *args, **kwargs):
        """
        Create a new live session.
        Only Admin/Owner can create sessions.
        """
        if request.user.role not in ['admin', 'owner']:
            return Response(
                {'error': 'Only admins can create sessions'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(created_by=request.user)
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'], permission_classes=[IsTeacherOrAdmin])
    def start(self, request, pk=None):
        """
        Start a live session.
        Teacher can start any time after scheduled date.
        Creates LiveKit room and starts auto-recording.
        """
        session = self.get_object()
        
        if not session.is_startable:
            return Response(
                {'error': 'Session cannot be started yet or is already started'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create unique room name
        room_name = f"session-{session.id}-{int(timezone.now().timestamp())}"
        
        # Create LiveKit room
        try:
            room_info = livekit_service.create_room(
                room_name=room_name,
                metadata={
                    'session_id': str(session.id),
                    'course_id': str(session.course.id),
                    'teacher': session.course.teacher.email if session.course.teacher else None
                }
            )
            
            # Mark session as started
            session.mark_started(room_name)
            
            # Start auto-recording (beats Zoom - always recorded!)
            recording_info = livekit_service.start_recording(room_name, str(session.id))
            session.livekit_recording_id = recording_info['egress_id']
            session.save(update_fields=['livekit_recording_id'])
            
            return Response({
                'status': 'started',
                'room': room_info,
                'recording': recording_info,
                'session': LiveSessionSerializer(session).data
            })
            
        except Exception as e:
            return Response(
                {'error': f'Failed to start session: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'], permission_classes=[IsTeacherOrAdmin])
    def end(self, request, pk=None):
        """
        End a live session.
        Stops recording automatically.
        """
        session = self.get_object()
        
        if not session.is_live:
            return Response(
                {'error': 'Session is not currently live'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Stop recording
        if session.livekit_recording_id:
            try:
                livekit_service.stop_recording(session.livekit_recording_id)
            except Exception:
                pass  # Recording will be stopped by webhook anyway
        
        # Mark session as ended
        session.mark_ended()
        
        # Delete room (disconnect all participants)
        if session.livekit_room_id:
            livekit_service.delete_room(session.livekit_room_id)
        
        return Response({
            'status': 'ended',
            'session': LiveSessionSerializer(session).data
        })
    
    @action(detail=True, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def join_token(self, request, pk=None):
        """
        Get a JWT token to join the live session.
        Different tokens for teacher vs student.
        """
        session = self.get_object()
        
        if not session.is_live:
            return Response(
                {'error': 'Session is not currently live'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Determine role
        if request.user == session.course.teacher:
            role = 'publisher'
            can_publish = True
        elif request.user.role in ['admin', 'owner']:
            role = 'admin'
            can_publish = False
        elif request.user.role == 'student':
            role = 'subscriber'
            can_publish = True  # Allow audio for questions
        else:
            return Response(
                {'error': 'Not authorized to join this session'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Generate token
        token = livekit_service.generate_token(
            room_name=session.livekit_room_id,
            user_id=str(request.user.id),
            user_name=request.user.full_name or request.user.email,
            role=role,
            can_publish=can_publish,
            expiry_minutes=120
        )
        
        # Track attendance
        if request.user.role == 'student':
            Attendance.objects.get_or_create(
                session=session,
                student=request.user
            )
            session.attendee_count = session.attendance_records.count()
            session.save(update_fields=['attendee_count'])
        
        return Response({
            'token': token,
            'url': settings.LIVEKIT_URL.replace('wss://', 'https://'),
            'room_name': session.livekit_room_id,
            'role': role
        })
    
    @action(detail=True, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def attendance(self, request, pk=None):
        """Get attendance records for a session."""
        session = self.get_object()
        
        if request.user.role not in ['teacher', 'admin', 'owner']:
            if request.user.role != 'student':
                return Response(
                    {'error': 'Not authorized'},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        attendance_records = session.attendance_records.select_related('student').all()
        serializer = AttendanceSerializer(attendance_records, many=True)
        
        return Response({
            'total': len(attendance_records),
            'records': serializer.data
        })
    
    @action(detail=False, methods=['get'], permission_classes=[IsTeacherOrAdmin])
    def upcoming(self, request):
        """Get upcoming sessions for today/this week."""
        days = int(request.query_params.get('days', 7))
        queryset = self.get_queryset().filter(
            scheduled_start__gte=timezone.now(),
            scheduled_start__lte=timezone.now() + timezone.timedelta(days=days),
            status=SessionStatus.SCHEDULED
        ).order_by('scheduled_start')
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def missed(self, request):
        """Get missed sessions (teacher didn't show up)."""
        queryset = self.get_queryset().filter(
            status=SessionStatus.MISSED
        ).order_by('-scheduled_start')
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class AttendanceViewSet(viewsets.ReadOnlyModelViewSet):
    """View set for attendance records."""
    
    serializer_class = AttendanceSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset():
        user = self.request.user
        
        if user.role in ['admin', 'owner']:
            return Attendance.objects.all()
        elif user.role == 'teacher':
            return Attendance.objects.filter(session__course__teacher=user)
        else:  # student
            return Attendance.objects.filter(student=user)
