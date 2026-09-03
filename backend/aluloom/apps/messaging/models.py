"""
Messaging models for Al-Uloom Academy.
Course-based moderated messaging (no private chats).
"""

from django.db import models
import uuid


class CourseMessage(models.Model):
    """Message in a course chat room."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid7, editable=False)
    course = models.ForeignKey('courses.Course', on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='course_messages')
    content = models.TextField()
    is_moderated = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=True)  # Auto-approved, can be flagged
    created_at = models.DateTimeField(auto_now_add=True)
    edited_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'course_messages'
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.sender.email} - {self.course.title_en}"


class MessageFlag(models.Model):
    """Flagged message for moderation review."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid7, editable=False)
    message = models.ForeignKey(CourseMessage, on_delete=models.CASCADE, related_name='flags')
    flagged_by = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='flagged_messages')
    reason = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    reviewed_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, related_name='reviewed_flags')
    reviewed_at = models.DateTimeField(null=True, blank=True)
    resolution = models.CharField(max_length=50, choices=[
        ('dismissed', 'Dismissed'),
        ('removed', 'Removed'),
        ('warning_issued', 'Warning Issued'),
    ], null=True, blank=True)
    
    class Meta:
        db_table = 'message_flags'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Flag on message {self.message.id} by {self.flagged_by.email}"
