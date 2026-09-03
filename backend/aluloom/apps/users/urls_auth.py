"""
Authentication URL routing for Al-Uloom Academy API.
"""

from django.urls import path
from .views import (
    LoginView, LogoutView, PasswordResetRequestView,
    PasswordResetConfirmView, ChangePasswordView
)

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('forgot-password/', PasswordResetRequestView.as_view(), name='password-reset-request'),
    path('reset-password/', PasswordResetConfirmView.as_view(), name='password-reset-confirm'),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
]
