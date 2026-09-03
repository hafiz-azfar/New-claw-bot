"""
User serializers for Al-Uloom Academy API.
"""

from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import User, Role


class UserSerializer(serializers.ModelSerializer):
    """Serializer for user model."""
    
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'full_name', 'role', 'role_display',
            'phone', 'language_pref', 'timezone', 'avatar',
            'guardian_email', 'is_active', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class UserCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating users (Admin/Owner only)."""
    
    password = serializers.CharField(write_only=True, validators=[validate_password])
    temporary_password = serializers.CharField(read_only=True)
    
    class Meta:
        model = User
        fields = [
            'email', 'password', 'full_name', 'role', 'phone',
            'language_pref', 'timezone', 'guardian_email', 'temporary_password'
        ]
    
    def create(self, validated_data):
        # Set default values
        validated_data.setdefault('language_pref', 'en')
        validated_data.setdefault('timezone', 'UTC')
        
        # Create user with password
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            full_name=validated_data.get('full_name', ''),
            role=validated_data.get('role', Role.STUDENT),
            phone=validated_data.get('phone'),
            language_pref=validated_data['language_pref'],
            timezone=validated_data['timezone'],
            guardian_email=validated_data.get('guardian_email'),
        )
        
        # Generate temporary password if not provided
        import secrets
        temp_password = secrets.token_urlsafe(12)
        user.temporary_password = temp_password  # This would be sent via email
        
        return user


class LoginSerializer(serializers.Serializer):
    """Serializer for login endpoint."""
    
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class PasswordResetRequestSerializer(serializers.Serializer):
    """Serializer for password reset request."""
    
    email = serializers.EmailField()


class PasswordResetConfirmSerializer(serializers.Serializer):
    """Serializer for password reset confirmation."""
    
    token = serializers.CharField()
    new_password = serializers.CharField(validators=[validate_password])


class ChangePasswordSerializer(serializers.Serializer):
    """Serializer for changing password."""
    
    current_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, validators=[validate_password])
