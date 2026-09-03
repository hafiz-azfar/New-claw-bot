"""
Messaging URL routing for Al-Uloom Academy API.
"""

from django.urls import path
from .views import CourseMessageViewSet, MessageFlagViewSet

urlpatterns = [
    # Course messages (nested under courses)
    path('courses/<uuid:course_pk>/messages/', CourseMessageViewSet.as_view({
        'get': 'list',
        'post': 'create'
    }), name='course-messages'),
    path('courses/<uuid:course_pk>/messages/<int:pk>/', CourseMessageViewSet.as_view({
        'get': 'retrieve',
        'delete': 'destroy'
    }), name='course-message-detail'),
    
    # Message flags
    path('flags/', MessageFlagViewSet.as_view({
        'get': 'list',
        'post': 'create'
    }), name='message-flags'),
    path('flags/<int:pk>/', MessageFlagViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy'
    }), name='message-flag-detail'),
    path('flags/<int:pk>/review/', MessageFlagViewSet.as_view({
        'post': 'review_flag'
    }), name='message-flag-review'),
]
