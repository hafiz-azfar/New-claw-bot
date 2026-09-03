"""
Live Sessions models for Al-Uloom Academy.
Integrates with LiveKit for superior video conferencing (Zoom/Teams alternative).
"""

from django.db import models
import uuid
from django.utils import timezone
from datetime import timedelta


class SessionStatus(models.TextChoices):
    SCHEDULED = 'scheduled', 'Scheduled'
    LIVE = 'live', 'Live'
    ENDED = 'ended', 'Ended'
    MISSED = 'missed', 'Missed'  # Teacher didn't join
    RECORDING_PROCESSING = 'recording_processing', 'Recording Processing'
    RECORDING_READY = 'recording_ready', 'Recording Ready'


class LiveSession(models.Model):
    """
    Live session model for virtual classrooms.
    Beats Zoom with: auto-recording, moderated chat, MCQ integration, unlimited duration.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid7, editable=False)
    course = models.ForeignKey('courses.Course', on_delete=models.CASCADE, related_name='sessions')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    
    # Scheduling
    scheduled_start = models.DateTimeField()
    scheduled_duration_minutes = models.PositiveIntegerField(default=60)
    actual_start = models.DateTimeField(null=True, blank=True)
    actual_end = models.DateTimeField(null=True, blank=True)
    
    # LiveKit integration
    livekit_room_id = models.CharField(max_length=100, unique=True, null=True, blank=True)
    livekit_recording_id = models.CharField(max_length=100, blank=True, null=True)
    
    # Status tracking
    status = models.CharField(max_length=30, choices=SessionStatus.choices, default=SessionStatus.SCHEDULED)
    missed_reason = models.TextField(blank=True, null=True)
    
    # Recording
    recording_url = models.URLField(blank=True, null=True, help_text="MinIO URL for recorded session")
    recording_file_size = models.BigIntegerField(null=True, blank=True)
    recording_duration_seconds = models.IntegerField(null=True, blank=True)
    
    # Attendance
    max_attendees = models.PositiveIntegerField(null=True, blank=True, help_text="0 = unlimited")
    attendee_count = models.PositiveIntegerField(default=0)
    
    # Metadata
    created_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, related_name='created_sessions')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'live_sessions'
        ordering = ['-scheduled_start']
        indexes = [
            models.Index(fields=['course', 'status']),
            models.Index(fields=['scheduled_start']),
            models.Index(fields=['livekit_room_id']),
        ]

    def __str__(self):
        return f"{self.title} ({self.scheduled_start})"

    @property
    def is_startable(self):
        """Teacher can start session any time after scheduled date."""
        return timezone.now() >= self.scheduled_start and self.status == SessionStatus.SCHEDULED

    @property
    def is_live(self):
        return self.status == SessionStatus.LIVE

    @property
    def scheduled_end(self):
        if self.scheduled_start and self.scheduled_duration_minutes:
            return self.scheduled_start + timedelta(minutes=self.scheduled_duration_minutes)
        return None

    @property
    def actual_duration_minutes(self):
        if self.actual_start and self.actual_end:
            return int((self.actual_end - self.actual_start).total_seconds() / 60)
        return None

    def mark_started(self, livekit_room_id: str):
        """Mark session as started and store LiveKit room ID."""
        self.status = SessionStatus.LIVE
        self.livekit_room_id = livekit_room_id
        self.actual_start = timezone.now()
        self.save(update_fields=['status', 'livekit_room_id', 'actual_start', 'updated_at'])

    def mark_ended(self):
        """Mark session as ended. Recording will be processed by webhook."""
        self.status = SessionStatus.RECORDING_PROCESSING
        self.actual_end = timezone.now()
        self.save(update_fields=['status', 'actual_end', 'updated_at'])

    def mark_missed(self, reason: str = None):
        """Mark session as missed (teacher didn't join)."""
        self.status = SessionStatus.MISSED
        self.missed_reason = reason
        self.save(update_fields=['status', 'missed_reason', 'updated_at'])

    def mark_recording_ready(self, url: str, file_size: int = None, duration: int = None):
        """Mark recording as ready."""
        self.recording_url = url
        self.recording_file_size = file_size
        self.recording_duration_seconds = duration
        self.status = SessionStatus.RECORDING_READY
        self.save(update_fields=['recording_url', 'recording_file_size', 'recording_duration_seconds', 'status', 'updated_at'])


class Attendance(models.Model):
    """
    Tracks student attendance for live sessions.
    Better than Zoom: automatic join/leave tracking, engagement metrics.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid7, editable=False)
    session = models.ForeignKey(LiveSession, on_delete=models.CASCADE, related_name='attendance_records')
    student = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='session_attendance')
    
    join_time = models.DateTimeField(auto_now_add=True)
    leave_time = models.DateTimeField(null=True, blank=True)
    duration_seconds = models.IntegerField(null=True, blank=True)
    
    # Engagement metrics (future enhancement)
    messages_sent = models.PositiveIntegerField(default=0)
    quiz_participated = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'attendance'
        ordering = ['join_time']
        unique_together = ['session', 'student']
        indexes = [
            models.Index(fields=['session', 'student']),
            models.Index(fields=['student', 'join_time']),
        ]

    def __str__(self):
        return f"{self.student.email} - {self.session.title}"

    def calculate_duration(self):
        """Calculate attendance duration in seconds."""
        if self.join_time and self.leave_time:
            self.duration_seconds = int((self.leave_time - self.join_time).total_seconds())
            self.save(update_fields=['duration_seconds', 'updated_at'])
            return self.duration_seconds
        return 0


class SessionInvite(models.Model):
    """
    Invite tokens for joining live sessions.
    Secure, time-limited access tokens.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid7, editable=False)
    session = models.ForeignKey(LiveSession, on_delete=models.CASCADE, related_name='invites')
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='session_invites')
    
    token = models.CharField(max_length=100, unique=True, editable=False)
    role = models.CharField(max_length=20, choices=[
        ('publisher', 'Publisher (Teacher)'),
        ('subscriber', 'Subscriber (Student)'),
        ('admin', 'Admin Observer'),
    ])
    
    expires_at = models.DateTimeField()
    used = models.BooleanField(default=False)
    used_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'session_invites'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['token']),
            models.Index(fields=['user', 'expires_at']),
        ]

    def __str__(self):
        return f"Invite for {self.user.email} to {self.session.title}"

    def save(self, *args, **kwargs):
        if not self.token:
            self.token = uuid.uuid4().hex
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(hours=24)
        super().save(*args, **kwargs)
