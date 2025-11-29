from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('employee/', views.employee_dashboard, name='employee_dashboard'),
    path('manager/', views.manager_dashboard, name='manager_dashboard'),
    path('api/leave-request/<int:request_id>/process/', views.process_leave_request, name='process_leave_request'),
]