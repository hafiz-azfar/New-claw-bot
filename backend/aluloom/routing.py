"""
WebSocket routing for Al-Uloom Academy project.
"""

from django.urls import re_path
from aluloom.apps.messaging import consumers

websocket_urlpatterns = [
    re_path(r'ws/courses/(?P<course_id>[^/]+)/chat/$', consumers.ChatConsumer.as_asgi()),
]
