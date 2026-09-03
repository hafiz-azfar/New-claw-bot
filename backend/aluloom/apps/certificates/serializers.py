"""
Certificate serializers for Al-Uloom Academy API.
"""

from rest_framework import serializers
from .models import Certificate, CertificateTemplate


class CertificateSerializer(serializers.ModelSerializer):
    """Serializer for certificate model."""
    
    student_email = serializers.CharField(source='student.email', read_only=True)
    student_name = serializers.CharField(source='student.full_name', read_only=True)
    course_title = serializers.CharField(source='course.title_en', read_only=True)
    verification_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Certificate
        fields = [
            'id', 'certificate_number', 'student', 'student_email',
            'student_name', 'course', 'course_title', 'issued_at',
            'expires_at', 'pdf_file', 'verification_hash', 'verification_url'
        ]
        read_only_fields = ['id', 'certificate_number', 'verification_hash']
    
    def get_verification_url(self, obj):
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(f'/api/certificates/verify/{obj.verification_hash}/')
        return f'/api/certificates/verify/{obj.verification_hash}/'


class CertificateCreateSerializer(serializers.Serializer):
    """Serializer for creating a certificate (admin/teacher only)."""
    
    student_id = serializers.UUIDField()
    course_id = serializers.UUIDField()
    
    def validate_course_id(self, value):
        from courses.models import Course
        try:
            course = Course.objects.get(id=value)
            # Check if student completed the course
        except Course.DoesNotExist:
            raise serializers.ValidationError("Course not found.")
        return value
    
    def validate_student_id(self, value):
        from users.models import User
        try:
            user = User.objects.get(id=value)
            if user.role != 'student':
                raise serializers.ValidationError("User is not a student.")
        except User.DoesNotExist:
            raise serializers.ValidationError("Student not found.")
        return value


class CertificateTemplateSerializer(serializers.ModelSerializer):
    """Serializer for certificate template."""
    
    class Meta:
        model = CertificateTemplate
        fields = ['id', 'name', 'description', 'template_html', 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at']


class CertificateVerificationSerializer(serializers.Serializer):
    """Serializer for certificate verification response."""
    
    is_valid = serializers.BooleanField()
    certificate_number = serializers.CharField()
    student_name = serializers.CharField()
    course_title = serializers.CharField()
    issued_at = serializers.DateTimeField()
    issuer = serializers.CharField()
