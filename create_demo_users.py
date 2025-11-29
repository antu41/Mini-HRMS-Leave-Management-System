import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hrms_project.settings')
django.setup()

from django.contrib.auth.models import User
from leave_management.models import UserProfile

# Create employee user
employee, created = User.objects.get_or_create(
    username='john',
    defaults={
        'first_name': 'John',
        'last_name': 'Doe',
        'email': 'john@example.com'
    }
)
if created:
    employee.set_password('password123')
    employee.save()
    UserProfile.objects.create(user=employee, role='employee', leave_balance=20)
    print('Employee user created successfully')
else:
    print('Employee user already exists')

# Create manager user
manager, created = User.objects.get_or_create(
    username='jane',
    defaults={
        'first_name': 'Jane',
        'last_name': 'Smith',
        'email': 'jane@example.com'
    }
)
if created:
    manager.set_password('password123')
    manager.save()
    UserProfile.objects.create(user=manager, role='manager', leave_balance=20)
    print('Manager user created successfully')
else:
    print('Manager user already exists')

print('\nDemo users created:')
print('Employee - username: employee, password: password123')
print('Manager - username: manager, password: password123')