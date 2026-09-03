"""
WSGI config for Al-Uloom Academy project.
"""

import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'aluloom.settings')

application = get_wsgi_application()
