from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.utils import timezone

class UserProfile(models.Model):
    """Extended user profile to store role and leave balance"""
    ROLE_CHOICES = [
        ('employee', 'Employee'),
        ('manager', 'Manager'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='employee')
    leave_balance = models.IntegerField(
        default=20,
        validators=[MinValueValidator(0)],
        help_text="Available leave days"
    )
    
    class Meta:
        db_table = 'user_profiles'
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'
    
    def __str__(self):
        return f"{self.user.username} - {self.role}"
    
    def is_manager(self):
        return self.role == 'manager'
    
    def is_employee(self):
        return self.role == 'employee'


class LeaveRequest(models.Model):
    """Leave request model"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    employee = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='leave_requests'
    )
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField()
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='pending'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    processed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='processed_requests'
    )
    
    class Meta:
        db_table = 'leave_requests'
        ordering = ['-created_at']
        verbose_name = 'Leave Request'
        verbose_name_plural = 'Leave Requests'
    
    def __str__(self):
        return f"{self.employee.username} - {self.start_date} to {self.end_date}"
    
    @property
    def days_requested(self):
        """Calculate number of days requested"""
        return (self.end_date - self.start_date).days + 1
    
    def clean(self):
        """Custom validation"""
        from django.core.exceptions import ValidationError
        
        if self.start_date and self.end_date:
            if self.end_date < self.start_date:
                raise ValidationError("End date must be after start date")
            
            if self.start_date < timezone.now().date():
                raise ValidationError("Cannot apply for leave in the past")