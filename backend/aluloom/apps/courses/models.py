"""
Course models for Al-Uloom Academy.
"""

from django.db import models
import uuid


class CourseType(models.TextChoices):
    LIVE = 'live', 'Live'
    RECORDED = 'recorded', 'Recorded'


class CourseStatus(models.TextChoices):
    DRAFT = 'draft', 'Draft'
    PUBLISHED = 'published', 'Published'
    ARCHIVED = 'archived', 'Archived'


class Course(models.Model):
    """Course model for both live and recorded courses."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid7, editable=False)
    title_en = models.CharField(max_length=200)
    title_ar = models.CharField(max_length=200, blank=True, null=True)
    title_ur = models.CharField(max_length=200, blank=True, null=True)
    description_en = models.TextField()
    description_ar = models.TextField(blank=True, null=True)
    description_ur = models.TextField(blank=True, null=True)
    course_type = models.CharField(max_length=20, choices=CourseType.choices)
    teacher = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, related_name='courses')
    price_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    price_currency = models.CharField(max_length=3, default='USD')
    thumbnail = models.ImageField(upload_to='course_thumbnails/', blank=True, null=True)
    status = models.CharField(max_length=20, choices=CourseStatus.choices, default=CourseStatus.DRAFT)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'courses'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title_en


class Module(models.Model):
    """Module for recorded courses."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid7, editable=False)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='modules')
    title = models.CharField(max_length=200)
    order = models.PositiveIntegerField()
    pass_threshold = models.PositiveIntegerField(default=40)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'modules'
        ordering = ['order']
        unique_together = ['course', 'order']
    
    def __str__(self):
        return f"{self.course.title_en} - Module {self.order}"


class ModuleContent(models.Model):
    """Content items within a module (video, audio, PDF, images)."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid7, editable=False)
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='contents')
    content_type = models.CharField(max_length=20, choices=[
        ('video', 'Video'),
        ('audio', 'Audio'),
        ('pdf', 'PDF'),
        ('image', 'Image'),
    ])
    file = models.FileField(upload_to='module_content/')
    title = models.CharField(max_length=200, blank=True)
    order = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'module_contents'
        ordering = ['order']
    
    def __str__(self):
        return f"{self.module} - {self.content_type}"


class Quiz(models.Model):
    """MCQ Quiz for a module."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid7, editable=False)
    module = models.OneToOneField(Module, on_delete=models.CASCADE, related_name='quiz')
    time_limit_minutes = models.PositiveIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'quizzes'
    
    def __str__(self):
        return f"Quiz for {self.module}"


class Question(models.Model):
    """Question in a quiz."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid7, editable=False)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()
    order = models.PositiveIntegerField()
    
    class Meta:
        db_table = 'questions'
        ordering = ['order']
    
    def __str__(self):
        return f"Question {self.order}"


class Option(models.Model):
    """Option for a question."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid7, editable=False)
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='options')
    text = models.CharField(max_length=500)
    is_correct = models.BooleanField(default=False)
    order = models.PositiveIntegerField()
    
    class Meta:
        db_table = 'options'
        ordering = ['order']
    
    def __str__(self):
        return f"Option {self.order} for {self.question}"


class QuizAttempt(models.Model):
    """Student attempt at a quiz."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid7, editable=False)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='attempts')
    student = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='quiz_attempts')
    score_pct = models.DecimalField(max_digits=5, decimal_places=2)
    passed = models.BooleanField()
    answers = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'quiz_attempts'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.student.email} - {self.quiz} - {self.score_pct}%"
