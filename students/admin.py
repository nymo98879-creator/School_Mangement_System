from django.contrib import admin
from .models import Student

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['student_id', 'first_name', 'last_name', 'email', 'class_enrolled', 'is_active']
    list_filter = ['gender', 'is_active', 'class_enrolled']
    search_fields = ['first_name', 'last_name', 'student_id', 'email']
    readonly_fields = ['enrollment_date', 'created_at', 'updated_at']
    fieldsets = (
        ('Personal Information', {
            'fields': ('student_id', 'first_name', 'last_name', 'date_of_birth', 'gender')
        }),
        ('Contact Information', {
            'fields': ('email', 'phone', 'address')
        }),
        ('Guardian Information', {
            'fields': ('guardian_name', 'guardian_phone', 'guardian_email')
        }),
        ('Academic Information', {
            'fields': ('class_enrolled', 'enrollment_date', 'is_active')
        }),
        ('Additional', {
            'fields': ('profile_picture', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )