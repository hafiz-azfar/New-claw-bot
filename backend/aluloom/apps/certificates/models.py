"""
Certificate models for Al-Uloom Academy.
"""

from django.db import models
import uuid


class Certificate(models.Model):
    """Certificate awarded upon course completion."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid7, editable=False)
    student = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='certificates')
    course = models.ForeignKey('courses.Course', on_delete=models.CASCADE, related_name='certificates')
    certificate_number = models.CharField(max_length=50, unique=True)
    issued_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    pdf_file = models.FileField(upload_to='certificates/', blank=True, null=True)
    verification_hash = models.CharField(max_length=64, unique=True)
    
    class Meta:
        db_table = 'certificates'
        ordering = ['-issued_at']
    
    def __str__(self):
        return f"Certificate {self.certificate_number} - {self.student.email}"
    
    def save(self, *args, **kwargs):
        if not self.certificate_number:
            # Generate certificate number
            import secrets
            year = self.issued_at.year if self.issued_at else timezone.now().year
            self.certificate_number = f"ALULOOM-{year}-{secrets.token_hex(8).upper()}"
        
        if not self.verification_hash:
            import hashlib
            data = f"{self.certificate_number}{self.student.email}{self.course.id}"
            self.verification_hash = hashlib.sha256(data.encode()).hexdigest()
        
        super().save(*args, **kwargs)


class CertificateTemplate(models.Model):
    """Template for certificate generation."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid7, editable=False)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    template_html = models.TextField(help_text="HTML template with {{student_name}}, {{course_title}}, etc.")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'certificate_templates'
    
    def __str__(self):
        return self.name
