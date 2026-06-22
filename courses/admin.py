from django.contrib import admin
from .models import Course

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['course_id', 'name', 'teacher', 'credits', 'duration', 'fee', 'is_active']
    list_filter = ['is_active', 'teacher', 'credits']
    search_fields = ['course_id', 'name', 'description']
    ordering = ['course_id']
    list_per_page = 20
    
    fieldsets = (
        ('Course Information', {
            'fields': ('course_id', 'name', 'description')
        }),
        ('Course Details', {
            'fields': ('credits', 'duration', 'fee', 'teacher')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )
    
    readonly_fields = ['course_id']  # Make course_id read-only in admin
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # Editing an existing object
            return self.readonly_fields + ('course_id',)
        return self.readonly_fields