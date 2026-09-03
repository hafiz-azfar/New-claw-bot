"""
Course serializers for Al-Uloom Academy API.
"""

from rest_framework import serializers
from .models import (
    Course, CourseType, CourseStatus, Module, ModuleContent,
    Quiz, Question, Option, QuizAttempt
)
from users.models import User


class CourseSerializer(serializers.ModelSerializer):
    """Serializer for course model."""
    
    teacher_name = serializers.CharField(source='teacher.full_name', read_only=True)
    type_display = serializers.CharField(source='get_course_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Course
        fields = [
            'id', 'title_en', 'title_ar', 'title_ur',
            'description_en', 'description_ar', 'description_ur',
            'course_type', 'type_display', 'teacher', 'teacher_name',
            'price_amount', 'price_currency', 'thumbnail',
            'status', 'status_display', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class CourseCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating courses."""
    
    class Meta:
        model = Course
        fields = [
            'title_en', 'title_ar', 'title_ur',
            'description_en', 'description_ar', 'description_ur',
            'course_type', 'teacher', 'price_amount', 'price_currency',
            'thumbnail', 'status'
        ]
    
    def validate(self, data):
        # Ensure at least English title/description are provided
        if not data.get('title_en') and self.instance is None:
            raise serializers.ValidationError("English title is required.")
        if not data.get('description_en') and self.instance is None:
            raise serializers.ValidationError("English description is required.")
        return data


class ModuleSerializer(serializers.ModelSerializer):
    """Serializer for module model."""
    
    content_count = serializers.SerializerMethodField()
    quiz_exists = serializers.SerializerMethodField()
    
    class Meta:
        model = Module
        fields = ['id', 'course', 'title', 'order', 'pass_threshold', 'content_count', 'quiz_exists', 'created_at']
        read_only_fields = ['id', 'created_at']
    
    def get_content_count(self, obj):
        return obj.contents.count()
    
    def get_quiz_exists(self, obj):
        return hasattr(obj, 'quiz')


class ModuleContentSerializer(serializers.ModelSerializer):
    """Serializer for module content."""
    
    file_url = serializers.SerializerMethodField()
    
    class Meta:
        model = ModuleContent
        fields = ['id', 'module', 'content_type', 'file', 'file_url', 'title', 'order', 'created_at']
        read_only_fields = ['id', 'created_at']
    
    def get_file_url(self, obj):
        if obj.file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.file.url)
            return obj.file.url
        return None


class QuizSerializer(serializers.ModelSerializer):
    """Serializer for quiz model."""
    
    question_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Quiz
        fields = ['id', 'module', 'time_limit_minutes', 'question_count', 'created_at']
        read_only_fields = ['id', 'created_at']
    
    def get_question_count(self, obj):
        return obj.questions.count()


class QuestionSerializer(serializers.ModelSerializer):
    """Serializer for question model."""
    
    options = serializers.SerializerMethodField()
    
    class Meta:
        model = Question
        fields = ['id', 'quiz', 'text', 'order', 'options']
        read_only_fields = ['id']
    
    def get_options(self, obj):
        options = obj.options.all().order_by('order')
        return OptionSerializer(options, many=True).data


class OptionSerializer(serializers.ModelSerializer):
    """Serializer for option model."""
    
    class Meta:
        model = Option
        fields = ['id', 'question', 'text', 'is_correct', 'order']
        read_only_fields = ['id']
    
    def create(self, validated_data):
        # Don't allow creating options with is_correct=True directly via API
        # This should be handled carefully by teachers/admins only
        validated_data['is_correct'] = False
        return super().create(validated_data)


class QuizAttemptSerializer(serializers.ModelSerializer):
    """Serializer for quiz attempt model."""
    
    student_email = serializers.CharField(source='student.email', read_only=True)
    student_name = serializers.CharField(source='student.full_name', read_only=True)
    
    class Meta:
        model = QuizAttempt
        fields = [
            'id', 'quiz', 'student', 'student_email', 'student_name',
            'score_pct', 'passed', 'answers', 'created_at'
        ]
        read_only_fields = ['id', 'score_pct', 'passed', 'created_at']


class QuizSubmitSerializer(serializers.Serializer):
    """Serializer for submitting quiz answers."""
    
    answers = serializers.ListField(
        child=serializers.DictField(),
        help_text="List of {question_id: option_id}"
    )
    
    def validate_answers(self, value):
        if not value:
            raise serializers.ValidationError("Answers cannot be empty.")
        return value
