"""
User URL routing for Al-Uloom Academy API.
"""

from django.urls import path
from .views import (
    UserListView, UserCreateView, UserDetailView,
    UserDeactivateView, UserActivateView, ForceLogoutView,
    CurrentUserView, MyCoursesView, MySessionsView, MyCertificatesView
)

urlpatterns = [
    # User management (Admin/Owner)
    path('users/', UserListView.as_view(), name='user-list'),
    path('users/create/', UserCreateView.as_view(), name='user-create'),
    path('users/<uuid:pk>/', UserDetailView.as_view(), name='user-detail'),
    path('users/<uuid:pk>/deactivate/', UserDeactivateView.as_view(), name='user-deactivate'),
    path('users/<uuid:pk>/activate/', UserActivateView.as_view(), name='user-activate'),
    path('users/<uuid:pk>/force-logout/', ForceLogoutView.as_view(), name='force-logout'),
    
    # Current user endpoints
    path('me/', CurrentUserView.as_view(), name='current-user'),
    path('me/courses/', MyCoursesView.as_view(), name='my-courses'),
    path('me/sessions/upcoming/', MySessionsView.as_view(), name='my-sessions'),
    path('me/certificates/', MyCertificatesView.as_view(), name='my-certificates'),
]
