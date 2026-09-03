"""
Course URL routing for Al-Uloom Academy API.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CourseViewSet, ModuleViewSet, ModuleContentViewSet,
    QuizViewSet, QuestionViewSet, OptionViewSet, QuizAttemptViewSet
)

router = DefaultRouter()
router.register(r'', CourseViewSet, basename='course')

# Nested routers for modules, content, quizzes, etc.
urlpatterns = [
    path('', include(router.urls)),
    path('<uuid:course_pk>/modules/', ModuleViewSet.as_view({
        'get': 'list',
        'post': 'create'
    }), name='course-modules'),
    path('<uuid:course_pk>/modules/<int:pk>/', ModuleViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy'
    }), name='course-module-detail'),
    path('modules/<uuid:module_pk>/content/', ModuleContentViewSet.as_view({
        'get': 'list',
        'post': 'create'
    }), name='module-content'),
    path('modules/<uuid:module_pk>/content/<int:pk>/', ModuleContentViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy'
    }), name='module-content-detail'),
    path('modules/<uuid:module_pk>/quizzes/', QuizViewSet.as_view({
        'get': 'list',
        'post': 'create'
    }), name='module-quizzes'),
    path('modules/<uuid:module_pk>/quizzes/<int:pk>/', QuizViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy'
    }), name='module-quiz-detail'),
    path('quizzes/<uuid:quiz_pk>/questions/', QuestionViewSet.as_view({
        'get': 'list',
        'post': 'create'
    }), name='quiz-questions'),
    path('quizzes/<uuid:quiz_pk>/questions/<int:pk>/', QuestionViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy'
    }), name='quiz-question-detail'),
    path('questions/<uuid:question_pk>/options/', OptionViewSet.as_view({
        'get': 'list',
        'post': 'create'
    }), name='question-options'),
    path('questions/<uuid:question_pk>/options/<int:pk>/', OptionViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy'
    }), name='question-option-detail'),
    path('quizzes/<uuid:quiz_pk>/attempts/', QuizAttemptViewSet.as_view({
        'get': 'list',
        'post': 'submit_attempt'
    }), name='quiz-attempts'),
    path('quizzes/<uuid:quiz_pk>/attempts/<int:pk>/', QuizAttemptViewSet.as_view({
        'get': 'retrieve',
        'delete': 'destroy'
    }), name='quiz-attempt-detail'),
]
