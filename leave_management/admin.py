from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import UserProfile, LeaveRequest


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'user'


class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'get_role', 'get_leave_balance', 'is_staff')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'profile__role')
    
    def get_role(self, obj):
        try:
            return obj.profile.role.title()
        except UserProfile.DoesNotExist:
            return '-'
    get_role.short_description = 'Role'
    
    def get_leave_balance(self, obj):
        try:
            return f"{obj.profile.leave_balance} days"
        except UserProfile.DoesNotExist:
            return '-'
    get_leave_balance.short_description = 'Leave Balance'


@admin.register(LeaveRequest)
class LeaveRequestAdmin(admin.ModelAdmin):
    list_display = ('employee', 'start_date', 'end_date', 'days_requested', 'status', 'created_at', 'processed_by')
    list_filter = ('status', 'created_at', 'start_date')
    search_fields = ('employee__username', 'employee__email', 'reason')
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at', 'updated_at', 'days_requested')
    
    fieldsets = (
        ('Employee Information', {
            'fields': ('employee',)
        }),
        ('Leave Details', {
            'fields': ('start_date', 'end_date', 'days_requested', 'reason')
        }),
        ('Status', {
            'fields': ('status', 'processed_by')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)