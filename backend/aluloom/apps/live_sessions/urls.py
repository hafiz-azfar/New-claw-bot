"""
URLs for Live Sessions app.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import LiveSessionViewSet, AttendanceViewSet

router = DefaultRouter()
router.register(r'sessions', LiveSessionViewSet, basename='live-session')
router.register(r'attendance', AttendanceViewSet, basename='attendance')

urlpatterns = [
    path('', include(router.urls)),
]
