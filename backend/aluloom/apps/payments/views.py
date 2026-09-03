"""
Payment views for Al-Uloom Academy API.
Handles Stripe and Razorpay payment integration.
"""

import secrets
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.utils import timezone
from .models import Payment, Refund, PaymentStatus
from .serializers import (
    PaymentSerializer, PaymentCreateSerializer, PaymentVerifySerializer,
    RefundSerializer, RefundCreateSerializer
)


class PaymentViewSet(viewsets.ModelViewSet):
    """ViewSet for payment operations."""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return PaymentCreateSerializer
        elif self.action == 'verify_payment':
            return PaymentVerifySerializer
        return PaymentSerializer
    
    def get_queryset(self):
        user = self.request.user
        if user.role in ['owner', 'admin']:
            return Payment.objects.all()
        return Payment.objects.filter(user=user)
    
    def create(self, request, *args, **kwargs):
        """Initialize a payment intent."""
        serializer = PaymentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        course_id = serializer.validated_data['course_id']
        gateway = serializer.validated_data['gateway']
        
        from courses.models import Course
        course = Course.objects.get(id=course_id)
        
        # Generate order ID
        order_id = f"order_{secrets.token_urlsafe(16)}"
        
        # Create payment record
        payment = Payment.objects.create(
            user=request.user,
            course=course,
            amount=course.price_amount,
            currency=course.price_currency,
            gateway=gateway,
            gateway_order_id=order_id,
            status=PaymentStatus.PENDING
        )
        
        # Return gateway-specific initialization data
        if gateway == 'stripe':
            # In production, create Stripe PaymentIntent here
            client_secret = f"pi_{secrets.token_urlsafe(24)}_secret_{secrets.token_urlsafe(24)}"
            return Response({
                'payment_id': str(payment.id),
                'order_id': order_id,
                'amount': str(payment.amount),
                'currency': payment.currency,
                'gateway': 'stripe',
                'client_secret': client_secret,
                'publishable_key': getattr(settings, 'STRIPE_PUBLISHABLE_KEY', '')
            })
        elif gateway == 'razorpay':
            # In production, create Razorpay Order here
            razorpay_order_id = f"order_{secrets.token_urlsafe(16)}"
            return Response({
                'payment_id': str(payment.id),
                'order_id': order_id,
                'razorpay_order_id': razorpay_order_id,
                'amount': str(payment.amount),
                'currency': payment.currency,
                'gateway': 'razorpay',
                'key': getattr(settings, 'RAZORPAY_KEY_ID', '')
            })
        
        return Response(PaymentSerializer(payment).data)
    
    @action(detail=True, methods=['post'], url_path='verify')
    def verify_payment(self, request, pk=None):
        """Verify payment after gateway callback."""
        payment = self.get_object()
        
        if payment.user != request.user and request.user.role not in ['owner', 'admin']:
            return Response(
                {'error': 'Unauthorized'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = PaymentVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        payment_id = serializer.validated_data.get('payment_id')
        signature = serializer.validated_data.get('signature')
        
        # Verify signature based on gateway
        if payment.gateway == 'razorpay' and signature:
            # In production, verify Razorpay signature here
            pass
        elif payment.gateway == 'stripe':
            # In production, verify Stripe webhook event here
            pass
        
        # Update payment status
        payment.status = PaymentStatus.COMPLETED
        payment.gateway_payment_id = payment_id
        payment.gateway_signature = signature
        payment.completed_at = timezone.now()
        payment.save()
        
        # Create enrollment
        self._create_enrollment(payment)
        
        return Response(PaymentSerializer(payment).data)
    
    @action(detail=True, methods=['post'], url_path='refund')
    def create_refund(self, request, pk=None):
        """Initiate a refund (admin only)."""
        payment = self.get_object()
        
        if request.user.role not in ['owner', 'admin']:
            return Response(
                {'error': 'Only admins can process refunds'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if payment.status != PaymentStatus.COMPLETED:
            return Response(
                {'error': 'Only completed payments can be refunded'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        refund = Refund.objects.create(
            payment=payment,
            amount=payment.amount,
            reason='Admin initiated refund',
            status=PaymentStatus.PENDING
        )
        
        return Response(RefundSerializer(refund).data, status=status.HTTP_201_CREATED)
    
    def _create_enrollment(self, payment):
        """Create enrollment after successful payment."""
        try:
            from enrollments.models import Enrollment
            Enrollment.objects.get_or_create(
                student=payment.user,
                course=payment.course,
                defaults={'status': 'active'}
            )
        except ImportError:
            pass  # Enrollment app not yet implemented


class RefundViewSet(viewsets.ModelViewSet):
    """ViewSet for refund operations."""
    
    serializer_class = RefundSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.role in ['owner', 'admin']:
            return Refund.objects.all()
        return Refund.objects.filter(payment__user=user)
