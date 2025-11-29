from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import LeaveRequest
from django.utils import timezone

class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Username',
            'autofocus': True
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password'
        })
    )


class LeaveRequestForm(forms.ModelForm):
    class Meta:
        model = LeaveRequest
        fields = ['start_date', 'end_date', 'reason']
        widgets = {
            'start_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'min': timezone.now().date().isoformat()
            }),
            'end_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'min': timezone.now().date().isoformat()
            }),
            'reason': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Enter reason for leave...'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
    
    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        
        if start_date and end_date:
            # Validate date range
            if end_date < start_date:
                raise forms.ValidationError("End date must be after start date")
            
            # Validate against past dates
            if start_date < timezone.now().date():
                raise forms.ValidationError("Cannot apply for leave in the past")
            
            # Calculate days and check balance
            if self.user:
                days_requested = (end_date - start_date).days + 1
                leave_balance = self.user.profile.leave_balance
                
                if days_requested > leave_balance:
                    raise forms.ValidationError(
                        f"Insufficient leave balance. You have {leave_balance} days available, "
                        f"but requested {days_requested} days."
                    )
        
        return cleaned_data