from django.contrib import admin
from .models import Attendance

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = [
        'id', 
        'student', 
        'course',  # Changed from 'class_obj'
        'date', 
        'status', 
        'time_in', 
        'time_out',
        'marked_by'
    ]
    
    list_filter = [
        'status', 
        'date', 
        'course',  # Changed from 'class_obj'
        'marked_by'
    ]
    
    search_fields = [
        'student__first_name', 
        'student__last_name', 
        'student__student_id',
        'course__name',  # Changed from 'class_obj__name'
        'course__code'   # Added
    ]
    
    list_per_page = 25
    list_select_related = ['student', 'course', 'marked_by']  # Changed from 'class_obj'
    
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Student & Course', {
            'fields': ('student', 'course')  # Changed from 'class_obj'
        }),
        ('Attendance Details', {
            'fields': ('date', 'status', 'time_in', 'time_out', 'remarks')
        }),
        ('Marked By', {
            'fields': ('marked_by',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('student', 'course', 'marked_by')