"""
User views for Al-Uloom Academy API.
"""

from rest_framework import status, generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings
import secrets

from .models import User, Role, AuditLog
from .serializers import (
    UserSerializer, UserCreateSerializer, LoginSerializer,
    PasswordResetRequestSerializer, PasswordResetConfirmSerializer,
    ChangePasswordSerializer
)


class IsOwnerOrAdmin(permissions.BasePermission):
    """Permission check for Owner or Admin roles."""
    
    def has_permission(self, request, view):
        return request.user and request.user.is_admin


class IsOwner(permissions.BasePermission):
    """Permission check for Owner role only."""
    
    def has_permission(self, request, view):
        return request.user and request.user.is_owner


class LoginView(APIView):
    """Login endpoint - returns JWT tokens."""
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = User.objects.filter(email=serializer.validated_data['email']).first()
        
        if not user or not user.check_password(serializer.validated_data['password']):
            return Response(
                {'detail': 'Invalid email or password'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        if not user.is_active:
            return Response(
                {'detail': 'Account is deactivated'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Generate tokens
        refresh = RefreshToken.for_user(user)
        
        # Log login
        AuditLog.objects.create(
            actor=user,
            action='LOGIN',
            entity_type='User',
            entity_id=user.id,
            ip_address=self.get_client_ip(request)
        )
        
        return Response({
            'access_token': str(refresh.access_token),
            'token_type': 'Bearer',
            'expires_in': 900,  # 15 minutes
            'user': UserSerializer(user).data
        })


class LogoutView(APIView):
    """Logout endpoint - invalidates refresh token."""
    
    def post(self, request):
        try:
            refresh_token = request.data.get('refresh_token')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
            
            AuditLog.objects.create(
                actor=request.user,
                action='LOGOUT',
                entity_type='User',
                entity_id=request.user.id
            )
            
            return Response({'detail': 'Successfully logged out'})
        except Exception as e:
            return Response(
                {'detail': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class PasswordResetRequestView(APIView):
    """Request password reset email."""
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = User.objects.filter(email=serializer.validated_data['email']).first()
        
        if user:
            # Generate reset token
            token = secrets.token_urlsafe(32)
            # Store token in cache with 30 min expiry
            # In production, use Redis cache
            from django.core.cache import cache
            cache.set(f'password_reset_{user.email}', token, timeout=1800)
            
            # Send email
            reset_url = f"{settings.FRONTEND_URL}/reset-password?token={token}&email={user.email}"
            send_mail(
                subject='Password Reset Request',
                message=f'Click the link to reset your password: {reset_url}',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False,
            )
        
        # Always return success to prevent email enumeration
        return Response({'detail': 'If the email exists, a reset link has been sent.'})


class PasswordResetConfirmView(APIView):
    """Confirm password reset with token."""
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Verify token from cache
        from django.core.cache import cache
        email = request.data.get('email')
        stored_token = cache.get(f'password_reset_{email}')
        
        if not stored_token or stored_token != serializer.validated_data['token']:
            return Response(
                {'detail': 'Invalid or expired token'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user = User.objects.filter(email=email).first()
        if user:
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            cache.delete(f'password_reset_{email}')
        
        return Response({'detail': 'Password reset successfully'})


class ChangePasswordView(APIView):
    """Change own password."""
    
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = request.user
        if not user.check_password(serializer.validated_data['current_password']):
            return Response(
                {'detail': 'Current password is incorrect'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        
        AuditLog.objects.create(
            actor=user,
            action='PASSWORD_CHANGE',
            entity_type='User',
            entity_id=user.id
        )
        
        return Response({'detail': 'Password changed successfully'})


class UserListView(generics.ListAPIView):
    """List users (Admin/Owner only)."""
    serializer_class = UserSerializer
    permission_classes = [IsOwnerOrAdmin]
    
    def get_queryset(self):
        queryset = User.objects.all()
        role = self.request.query_params.get('role')
        status_filter = self.request.query_params.get('status')
        search = self.request.query_params.get('search')
        
        if role:
            queryset = queryset.filter(role=role)
        if status_filter:
            queryset = queryset.filter(is_active=(status_filter == 'active'))
        if search:
            queryset = queryset.filter(
                models.Q(email__icontains=search) |
                models.Q(full_name__icontains=search)
            )
        
        return queryset


class UserCreateView(generics.CreateAPIView):
    """Create user (Admin/Owner only)."""
    serializer_class = UserCreateSerializer
    permission_classes = [IsOwnerOrAdmin]
    
    def perform_create(self, serializer):
        user = serializer.save()
        AuditLog.objects.create(
            actor=self.request.user,
            action='CREATE',
            entity_type='User',
            entity_id=user.id
        )


class UserDetailView(generics.RetrieveUpdateAPIView):
    """Get or update user detail (Admin/Owner only)."""
    serializer_class = UserSerializer
    permission_classes = [IsOwnerOrAdmin]
    queryset = User.objects.all()
    lookup_field = 'id'
    
    def perform_update(self, serializer):
        user = serializer.save()
        AuditLog.objects.create(
            actor=self.request.user,
            action='UPDATE',
            entity_type='User',
            entity_id=user.id
        )


class UserDeactivateView(APIView):
    """Deactivate user (soft delete)."""
    permission_classes = [IsOwnerOrAdmin]
    
    def post(self, request, pk):
        user = generics.get_object_or_404(User, pk=pk)
        user.is_active = False
        user.save()
        
        AuditLog.objects.create(
            actor=request.user,
            action='DEACTIVATE',
            entity_type='User',
            entity_id=user.id
        )
        
        return Response({'detail': 'User deactivated'})


class UserActivateView(APIView):
    """Reactivate user."""
    permission_classes = [IsOwnerOrAdmin]
    
    def post(self, request, pk):
        user = generics.get_object_or_404(User, pk=pk)
        user.is_active = True
        user.save()
        
        AuditLog.objects.create(
            actor=request.user,
            action='ACTIVATE',
            entity_type='User',
            entity_id=user.id
        )
        
        return Response({'detail': 'User activated'})


class ForceLogoutView(APIView):
    """Force logout user by blacklisting all tokens."""
    permission_classes = [IsOwnerOrAdmin]
    
    def post(self, request, pk):
        user = generics.get_object_or_404(User, pk=pk)
        
        # Blacklist all refresh tokens for this user
        # In production, track tokens in database
        AuditLog.objects.create(
            actor=request.user,
            action='FORCE_LOGOUT',
            entity_type='User',
            entity_id=user.id
        )
        
        return Response({'detail': 'User logged out from all sessions'})


class CurrentUserView(generics.RetrieveUpdateAPIView):
    """Get or update current user profile."""
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user


class MyCoursesView(APIView):
    """Get courses relevant to current user."""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        from aluloom.apps.courses.models import Course, Enrollment
        
        user = request.user
        courses = []
        
        if user.is_teacher:
            courses = Course.objects.filter(teacher=user)
        elif user.is_student:
            enrollments = Enrollment.objects.filter(student=user, status='ACTIVE')
            courses = [e.course for e in enrollments]
        else:
            courses = Course.objects.all()
        
        serializer = None  # Would need CourseSerializer
        return Response({'courses': 'TODO'})


class MySessionsView(APIView):
    """Get upcoming sessions for current user."""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        # Return upcoming sessions based on user role
        return Response({'sessions': 'TODO'})


class MyCertificatesView(APIView):
    """Get certificates earned by current student."""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        if not request.user.is_student:
            return Response(
                {'detail': 'Only students have certificates'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Return certificates
        return Response({'certificates': 'TODO'})


def get_client_ip(request):
    """Get client IP address from request."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
