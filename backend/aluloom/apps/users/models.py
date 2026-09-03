"""
User models for Al-Uloom Academy.
Implements custom user model with role-based access control.
"""

from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid


class Role(models.TextChoices):
    OWNER = 'owner', 'Owner'
    ADMIN = 'admin', 'Admin'
    TEACHER = 'teacher', 'Teacher'
    STUDENT = 'student', 'Student'


class User(AbstractUser):
    """Custom user model with role-based access."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid7, editable=False)
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.STUDENT,
    )
    phone = models.CharField(max_length=20, blank=True, null=True)
    language_pref = models.CharField(
        max_length=10,
        choices=[('en', 'English'), ('ar', 'Arabic'), ('ur', 'Urdu')],
        default='en',
    )
    timezone = models.CharField(max_length=50, default='UTC')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    guardian_email = models.EmailField(blank=True, null=True, help_text="For students only")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'users'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.email} ({self.get_role_display()})"
    
    @property
    def is_owner(self):
        return self.role == Role.OWNER
    
    @property
    def is_admin(self):
        return self.role in [Role.OWNER, Role.ADMIN]
    
    @property
    def is_teacher(self):
        return self.role == Role.TEACHER
    
    @property
    def is_student(self):
        return self.role == Role.STUDENT


class AuditLog(models.Model):
    """Audit log for tracking user actions."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid7, editable=False)
    actor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='audit_logs')
    action = models.CharField(max_length=50)  # CREATE, UPDATE, DELETE, LOGIN, etc.
    entity_type = models.CharField(max_length=50)  # User, Course, Session, etc.
    entity_id = models.UUIDField(null=True, blank=True)
    details = models.JSONField(default=dict, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'audit_logs'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['actor', 'timestamp']),
            models.Index(fields=['entity_type', 'entity_id']),
        ]
    
    def __str__(self):
        return f"{self.action} by {self.actor} on {self.entity_type}"
