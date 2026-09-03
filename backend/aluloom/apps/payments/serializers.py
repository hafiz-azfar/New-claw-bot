"""
Payment serializers for Al-Uloom Academy API.
"""

from rest_framework import serializers
from .models import Payment, Refund, PaymentStatus


class PaymentSerializer(serializers.ModelSerializer):
    """Serializer for payment model."""
    
    user_email = serializers.CharField(source='user.email', read_only=True)
    course_title = serializers.CharField(source='course.title_en', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    gateway_display = serializers.CharField(source='get_gateway_display', read_only=True)
    
    class Meta:
        model = Payment
        fields = [
            'id', 'user', 'user_email', 'course', 'course_title',
            'amount', 'currency', 'gateway', 'gateway_display',
            'status', 'status_display', 'gateway_order_id',
            'gateway_payment_id', 'metadata', 'created_at',
            'updated_at', 'completed_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'completed_at']


class PaymentCreateSerializer(serializers.Serializer):
    """Serializer for creating a payment intent."""
    
    course_id = serializers.UUIDField()
    gateway = serializers.ChoiceField(choices=[('stripe', 'Stripe'), ('razorpay', 'Razorpay')])
    
    def validate_course_id(self, value):
        from courses.models import Course
        try:
            course = Course.objects.get(id=value)
            if course.status != 'published':
                raise serializers.ValidationError("Course is not available for purchase.")
        except Course.DoesNotExist:
            raise serializers.ValidationError("Course not found.")
        return value


class PaymentVerifySerializer(serializers.Serializer):
    """Serializer for verifying payment."""
    
    payment_id = serializers.CharField()
    order_id = serializers.CharField()
    signature = serializers.CharField(required=False)


class RefundSerializer(serializers.ModelSerializer):
    """Serializer for refund model."""
    
    payment_order_id = serializers.CharField(source='payment.gateway_order_id', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Refund
        fields = [
            'id', 'payment', 'payment_order_id', 'amount',
            'reason', 'status', 'status_display',
            'gateway_refund_id', 'created_at', 'processed_at'
        ]
        read_only_fields = ['id', 'created_at', 'processed_at']


class RefundCreateSerializer(serializers.Serializer):
    """Serializer for creating a refund request."""
    
    payment_id = serializers.UUIDField()
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    reason = serializers.CharField(min_length=20)
    
    def validate_payment_id(self, value):
        from .models import Payment
        try:
            payment = Payment.objects.get(id=value)
            if payment.status != 'completed':
                raise serializers.ValidationError("Only completed payments can be refunded.")
        except Payment.DoesNotExist:
            raise serializers.ValidationError("Payment not found.")
        return value
