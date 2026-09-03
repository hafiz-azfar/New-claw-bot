"""
Course views for Al-Uloom Academy API.
"""

from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Q
from .models import Course, Module, ModuleContent, Quiz, Question, Option, QuizAttempt
from .serializers import (
    CourseSerializer, CourseCreateUpdateSerializer,
    ModuleSerializer, ModuleContentSerializer,
    QuizSerializer, QuestionSerializer, OptionSerializer,
    QuizAttemptSerializer, QuizSubmitSerializer
)
from users.permissions import IsOwnerOrAdmin, IsTeacher, IsStudent


class CourseViewSet(viewsets.ModelViewSet):
    """ViewSet for course CRUD operations."""
    
    queryset = Course.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return CourseCreateUpdateSerializer
        return CourseSerializer
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'owner' or user.role == 'admin':
            return Course.objects.all()
        elif user.role == 'teacher':
            return Course.objects.filter(teacher=user)
        else:  # student
            # Students see only published courses they're enrolled in
            # This would need an Enrollment model - simplified for now
            return Course.objects.filter(status='published')
    
    def perform_create(self, serializer):
        if self.request.user.role not in ['owner', 'admin', 'teacher']:
            raise permissions.PermissionDenied("Only teachers, admins, and owners can create courses.")
        serializer.save()


class ModuleViewSet(viewsets.ModelViewSet):
    """ViewSet for module CRUD operations."""
    
    serializer_class = ModuleSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        course_id = self.kwargs.get('course_pk')
        user = self.request.user
        
        if user.role in ['owner', 'admin']:
            return Module.objects.filter(course_id=course_id)
        elif user.role == 'teacher':
            return Module.objects.filter(course_id=course_id, course__teacher=user)
        else:  # student
            # Students see modules of published courses they're enrolled in
            return Module.objects.filter(course_id=course_id, course__status='published')
    
    def perform_create(self, serializer):
        course_id = self.kwargs.get('course_pk')
        course = get_object_or_404(Course, pk=course_id)
        
        if self.request.user.role not in ['owner', 'admin', 'teacher']:
            raise permissions.PermissionDenied("Only teachers, admins, and owners can create modules.")
        if course.teacher != self.request.user and self.request.user.role != 'teacher':
            if self.request.user.role not in ['owner', 'admin']:
                raise permissions.PermissionDenied("You can only create modules for your own courses.")
        
        serializer.save(course=course)


class ModuleContentViewSet(viewsets.ModelViewSet):
    """ViewSet for module content CRUD operations."""
    
    serializer_class = ModuleContentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        module_id = self.kwargs.get('module_pk')
        user = self.request.user
        
        if user.role in ['owner', 'admin']:
            return ModuleContent.objects.filter(module_id=module_id)
        elif user.role == 'teacher':
            return ModuleContent.objects.filter(module_id=module_id, module__course__teacher=user)
        else:  # student
            return ModuleContent.objects.filter(module_id=module_id, module__course__status='published')
    
    def perform_create(self, serializer):
        module_id = self.kwargs.get('module_pk')
        module = get_object_or_404(Module, pk=module_id)
        
        if self.request.user.role not in ['owner', 'admin', 'teacher']:
            raise permissions.PermissionDenied("Only teachers, admins, and owners can add content.")
        
        serializer.save(module=module)


class QuizViewSet(viewsets.ModelViewSet):
    """ViewSet for quiz CRUD operations."""
    
    serializer_class = QuizSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        module_id = self.kwargs.get('module_pk')
        user = self.request.user
        
        if user.role in ['owner', 'admin', 'teacher']:
            return Quiz.objects.filter(module_id=module_id)
        else:  # student
            return Quiz.objects.filter(module_id=module_id, module__course__status='published')
    
    def perform_create(self, serializer):
        module_id = self.kwargs.get('module_pk')
        module = get_object_or_404(Module, pk=module_id)
        
        if self.request.user.role not in ['owner', 'admin', 'teacher']:
            raise permissions.PermissionDenied("Only teachers, admins, and owners can create quizzes.")
        
        serializer.save(module=module)


class QuestionViewSet(viewsets.ModelViewSet):
    """ViewSet for question CRUD operations."""
    
    serializer_class = QuestionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        quiz_id = self.kwargs.get('quiz_pk')
        user = self.request.user
        
        if user.role in ['owner', 'admin', 'teacher']:
            return Question.objects.filter(quiz_id=quiz_id)
        else:  # student
            # Students should not see questions before taking the quiz
            # This is simplified - in production, hide until quiz attempt starts
            return Question.objects.filter(quiz_id=quiz_id, quiz__module__course__status='published')
    
    def perform_create(self, serializer):
        quiz_id = self.kwargs.get('quiz_pk')
        quiz = get_object_or_404(Quiz, pk=quiz_id)
        
        if self.request.user.role not in ['owner', 'admin', 'teacher']:
            raise permissions.PermissionDenied("Only teachers, admins, and owners can create questions.")
        
        serializer.save(quiz=quiz)


class OptionViewSet(viewsets.ModelViewSet):
    """ViewSet for option CRUD operations."""
    
    serializer_class = OptionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        question_id = self.kwargs.get('question_pk')
        return Option.objects.filter(question_id=question_id)
    
    def perform_create(self, serializer):
        question_id = self.kwargs.get('question_pk')
        question = get_object_or_404(Question, pk=question_id)
        
        if self.request.user.role not in ['owner', 'admin', 'teacher']:
            raise permissions.PermissionDenied("Only teachers, admins, and owners can create options.")
        
        serializer.save(question=question)


class QuizAttemptViewSet(viewsets.ModelViewSet):
    """ViewSet for quiz attempts."""
    
    serializer_class = QuizAttemptSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        quiz_id = self.kwargs.get('quiz_pk')
        
        if user.role in ['owner', 'admin', 'teacher']:
            return QuizAttempt.objects.filter(quiz_id=quiz_id)
        else:  # student
            return QuizAttempt.objects.filter(quiz_id=quiz_id, student=user)
    
    @action(detail=False, methods=['post'], url_path='submit')
    def submit_attempt(self, request, quiz_pk=None):
        """Submit a quiz attempt and calculate score."""
        quiz = get_object_or_404(Quiz, pk=quiz_pk)
        
        if request.user.role != 'student':
            return Response(
                {'error': 'Only students can submit quiz attempts'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = QuizSubmitSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        answers = serializer.validated_data['answers']
        
        # Calculate score
        total_questions = quiz.questions.count()
        correct_answers = 0
        
        for answer in answers:
            question_id = answer.get('question_id')
            option_id = answer.get('option_id')
            
            if question_id and option_id:
                option = Option.objects.filter(pk=option_id, question_id=question_id).first()
                if option and option.is_correct:
                    correct_answers += 1
        
        score_pct = (correct_answers / total_questions * 100) if total_questions > 0 else 0
        passed = score_pct >= quiz.module.pass_threshold
        
        # Create attempt
        attempt = QuizAttempt.objects.create(
            quiz=quiz,
            student=request.user,
            score_pct=score_pct,
            passed=passed,
            answers=answers
        )
        
        return Response(
            QuizAttemptSerializer(attempt).data,
            status=status.HTTP_201_CREATED
        )
