"""
Certificate views for Al-Uloom Academy API.
"""

from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Q
from .models import Certificate, CertificateTemplate
from .serializers import (
    CertificateSerializer, CertificateCreateSerializer,
    CertificateTemplateSerializer, CertificateVerificationSerializer
)


class CertificateViewSet(viewsets.ModelViewSet):
    """ViewSet for certificate operations."""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return CertificateCreateSerializer
        return CertificateSerializer
    
    def get_queryset(self):
        user = self.request.user
        if user.role in ['owner', 'admin']:
            return Certificate.objects.all()
        elif user.role == 'teacher':
            return Certificate.objects.filter(course__teacher=user)
        else:  # student
            return Certificate.objects.filter(student=user)
    
    def create(self, request, *args, **kwargs):
        """Create a certificate (admin/teacher only)."""
        if request.user.role not in ['owner', 'admin', 'teacher']:
            return Response(
                {'error': 'Only admins and teachers can issue certificates'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = CertificateCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        from users.models import User
        from courses.models import Course
        
        student = User.objects.get(id=serializer.validated_data['student_id'])
        course = Course.objects.get(id=serializer.validated_data['course_id'])
        
        # Check if certificate already exists
        existing = Certificate.objects.filter(student=student, course=course).first()
        if existing:
            return Response(
                {'error': 'Certificate already issued for this student and course'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        certificate = Certificate.objects.create(
            student=student,
            course=course
        )
        
        return Response(CertificateSerializer(certificate, context={'request': request}).data,
                       status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['get'], url_path='download')
    def download_certificate(self, request, pk=None):
        """Download certificate PDF."""
        certificate = self.get_object()
        
        if certificate.pdf_file:
            return Response({
                'url': certificate.pdf_file.url,
                'filename': f"certificate_{certificate.certificate_number}.pdf"
            })
        
        return Response(
            {'error': 'PDF not generated yet'},
            status=status.HTTP_404_NOT_FOUND
        )


class CertificateTemplateViewSet(viewsets.ModelViewSet):
    """ViewSet for certificate template management."""
    
    queryset = CertificateTemplate.objects.all()
    serializer_class = CertificateTemplateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        if self.request.user.role in ['owner', 'admin']:
            return CertificateTemplate.objects.all()
        return CertificateTemplate.objects.filter(is_active=True)


class CertificateVerificationView(viewsets.ViewSet):
    """ViewSet for public certificate verification."""
    
    permission_classes = [permissions.AllowAny]
    
    @action(detail=False, methods=['get'], url_path='verify/(?P<hash>[^/.]+)')
    def verify(self, request, hash=None):
        """Verify a certificate by its hash."""
        try:
            certificate = Certificate.objects.get(verification_hash=hash)
            
            data = {
                'is_valid': True,
                'certificate_number': certificate.certificate_number,
                'student_name': certificate.student.full_name,
                'course_title': certificate.course.title_en,
                'issued_at': certificate.issued_at,
                'issuer': 'Al-Uloom Academy'
            }
            
            return Response(data)
        except Certificate.DoesNotExist:
            return Response(
                {'is_valid': False, 'error': 'Certificate not found or invalid'},
                status=status.HTTP_404_NOT_FOUND
            )
