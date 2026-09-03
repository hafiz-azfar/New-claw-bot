"""
Custom permissions for Al-Uloom Academy API.
"""

from rest_framework import permissions


class IsOwner(permissions.BasePermission):
    """Allow only owners."""
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == 'owner'


class IsAdmin(permissions.BasePermission):
    """Allow only admins."""
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == 'admin'


class IsTeacher(permissions.BasePermission):
    """Allow only teachers."""
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == 'teacher'


class IsStudent(permissions.BasePermission):
    """Allow only students."""
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == 'student'


class IsOwnerOrAdmin(permissions.BasePermission):
    """Allow only owners and admins."""
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role in ['owner', 'admin']


class IsTeacherOrAdmin(permissions.BasePermission):
    """Allow only teachers and admins."""
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role in ['teacher', 'admin']


class IsOwnerAdminOrTeacher(permissions.BasePermission):
    """Allow owners, admins, and teachers."""
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role in ['owner', 'admin', 'teacher']


class IsEnrolledStudent(permissions.BasePermission):
    """Allow only enrolled students (for course content access)."""
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.role != 'student':
            return False
        # Check enrollment - this would need an Enrollment model
        # Simplified for now - will be enhanced with actual enrollment check
        return True


class IsCourseTeacherOrAdmin(permissions.BasePermission):
    """Allow only the teacher of the course or admins."""
    
    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.role in ['owner', 'admin']:
            return True
        if hasattr(obj, 'teacher') and obj.teacher == request.user:
            return True
        return False
