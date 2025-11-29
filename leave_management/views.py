from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.db import transaction
from .models import LeaveRequest, UserProfile
from .forms import CustomLoginForm, LeaveRequestForm
import json


def login_view(request):
    """Handle user login"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = CustomLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password')
    else:
        form = CustomLoginForm()
    
    return render(request, 'leave_management/login.html', {'form': form})


@login_required
def logout_view(request):
    """Handle user logout"""
    logout(request)
    messages.info(request, 'You have been logged out successfully')
    return redirect('login')


@login_required
def dashboard_view(request):
    """Route to appropriate dashboard based on user role"""
    try:
        profile = request.user.profile
        if profile.is_manager():
            return redirect('manager_dashboard')
        else:
            return redirect('employee_dashboard')
    except UserProfile.DoesNotExist:
        messages.error(request, 'User profile not found. Please contact administrator.')
        logout(request)
        return redirect('login')


@login_required
def employee_dashboard(request):
    """Employee dashboard with leave application form"""
    try:
        profile = request.user.profile
        
        # Only employees can access this page
        if not profile.is_employee():
            messages.warning(request, 'Access denied. Managers should use manager dashboard.')
            return redirect('manager_dashboard')
        
        if request.method == 'POST':
            form = LeaveRequestForm(request.POST, user=request.user)
            if form.is_valid():
                leave_request = form.save(commit=False)
                leave_request.employee = request.user
                leave_request.save()
                messages.success(
                    request,
                    f'Leave request submitted successfully for {leave_request.days_requested} days!'
                )
                return redirect('employee_dashboard')
        else:
            form = LeaveRequestForm(user=request.user)
        
        # Get user's leave requests
        leave_requests = LeaveRequest.objects.filter(employee=request.user)
        
        context = {
            'form': form,
            'leave_balance': profile.leave_balance,
            'leave_requests': leave_requests,
            'user': request.user,
        }
        
        return render(request, 'leave_management/employee_dashboard.html', context)
    
    except UserProfile.DoesNotExist:
        messages.error(request, 'User profile not found.')
        return redirect('login')


@login_required
def manager_dashboard(request):
    """Manager dashboard with pending leave requests"""
    try:
        profile = request.user.profile
        
        # Only managers can access this page
        if not profile.is_manager():
            messages.warning(request, 'Access denied. Employees should use employee dashboard.')
            return redirect('employee_dashboard')
        
        # Get all pending leave requests
        pending_requests = LeaveRequest.objects.filter(
            status='pending'
        ).select_related('employee', 'employee__profile')
        
        context = {
            'pending_requests': pending_requests,
            'user': request.user,
        }
        
        return render(request, 'leave_management/manager_dashboard.html', context)
    
    except UserProfile.DoesNotExist:
        messages.error(request, 'User profile not found.')
        return redirect('login')


@login_required
@require_http_methods(["POST"])
def process_leave_request(request, request_id):
    """AJAX endpoint to approve or reject leave requests"""
    try:
        # Verify user is a manager
        profile = request.user.profile
        if not profile.is_manager():
            return JsonResponse({
                'success': False,
                'error': 'Unauthorized. Only managers can process leave requests.'
            }, status=403)
        
        # Get the leave request
        leave_request = get_object_or_404(
            LeaveRequest.objects.select_related('employee', 'employee__profile'),
            id=request_id,
            status='pending'
        )
        
        # Parse request body
        try:
            data = json.loads(request.body)
            action = data.get('action')
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'Invalid JSON data'
            }, status=400)
        
        if action not in ['approve', 'reject']:
            return JsonResponse({
                'success': False,
                'error': 'Invalid action. Must be "approve" or "reject".'
            }, status=400)
        
        # Process the request with transaction
        with transaction.atomic():
            if action == 'approve':
                # Check if employee has sufficient balance
                employee_profile = leave_request.employee.profile
                days_requested = leave_request.days_requested
                
                if employee_profile.leave_balance < days_requested:
                    return JsonResponse({
                        'success': False,
                        'error': f'Insufficient leave balance. Employee has {employee_profile.leave_balance} days available.'
                    }, status=400)
                
                # Deduct leave balance
                employee_profile.leave_balance -= days_requested
                employee_profile.save()
                
                # Update leave request status
                leave_request.status = 'approved'
                leave_request.processed_by = request.user
                leave_request.save()
                
                return JsonResponse({
                    'success': True,
                    'message': f'Leave request approved. {days_requested} days deducted.',
                    'new_balance': employee_profile.leave_balance,
                    'status': 'approved'
                })
            
            else:  # reject
                leave_request.status = 'rejected'
                leave_request.processed_by = request.user
                leave_request.save()
                
                return JsonResponse({
                    'success': True,
                    'message': 'Leave request rejected.',
                    'status': 'rejected'
                })
    
    except LeaveRequest.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Leave request not found or already processed.'
        }, status=404)
    
    except UserProfile.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'User profile not found.'
        }, status=404)
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'An error occurred: {str(e)}'
        }, status=500)