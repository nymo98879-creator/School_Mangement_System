from django.contrib import admin
from .models import Teacher

@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ['teacher_id', 'get_full_name', 'position', 'specialization', 'qualification', 'is_active']
    list_filter = ['is_active', 'position', 'gender']
    search_fields = ['teacher_id', 'first_name', 'last_name', 'email']
    readonly_fields = ['created_at', 'updated_at']  # Changed from 'hire_date' to 'created_at' and 'updated_at'
    ordering = ['-created_at']
    
    fieldsets = (
        ('Personal Information', {
            'fields': ('teacher_id', 'first_name', 'last_name', 'date_of_birth', 'gender', 'phone', 'email', 'address', 'profile_picture')
        }),
        ('Professional Information', {
            'fields': ('qualification', 'specialization', 'years_of_experience', 'position')
        }),
        ('Employment Details', {
            'fields': ('hired_date', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_full_name(self, obj):
        return obj.get_full_name()
    get_full_name.short_description = 'Full Name'