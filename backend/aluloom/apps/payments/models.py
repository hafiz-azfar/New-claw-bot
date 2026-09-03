"""
Payment models for Al-Uloom Academy.
Supports Stripe and Razorpay payment gateways.
"""

from django.db import models
import uuid


class PaymentStatus(models.TextChoices):
    PENDING = 'pending', 'Pending'
    PROCESSING = 'processing', 'Processing'
    COMPLETED = 'completed', 'Completed'
    FAILED = 'failed', 'Failed'
    REFUNDED = 'refunded', 'Refunded'


class PaymentGateway(models.TextChoices):
    STRIPE = 'stripe', 'Stripe'
    RAZORPAY = 'razorpay', 'Razorpay'


class Payment(models.Model):
    """Payment transaction record."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid7, editable=False)
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='payments')
    course = models.ForeignKey('courses.Course', on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    gateway = models.CharField(max_length=20, choices=PaymentGateway.choices)
    status = models.CharField(max_length=20, choices=PaymentStatus.choices, default=PaymentStatus.PENDING)
    
    # Gateway-specific fields
    gateway_order_id = models.CharField(max_length=255, unique=True)
    gateway_payment_id = models.CharField(max_length=255, blank=True, null=True)
    gateway_signature = models.TextField(blank=True, null=True)
    
    # Metadata
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'payments'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Payment {self.gateway_order_id} - {self.user.email} - {self.amount} {self.currency}"


class Refund(models.Model):
    """Refund record for a payment."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid7, editable=False)
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name='refunds')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=PaymentStatus.choices, default=PaymentStatus.PENDING)
    gateway_refund_id = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'refunds'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Refund {self.id} for Payment {self.payment.gateway_order_id}"
