from django.contrib import admin
from .models import Attendance

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ['id', 'student', 'class_obj', 'date', 'status', 'marked_by']
    list_filter = ['status', 'date', 'class_obj']
    search_fields = ['student__first_name', 'student__last_name', 'class_obj__name']
    readonly_fields = ['created_at', 'updated_at']
    list_per_page = 20
    
    fieldsets = (
        ('Attendance Information', {
            'fields': ('student', 'class_obj', 'date', 'status')
        }),
        ('Time Information', {
            'fields': ('time_in', 'time_out'),
            'classes': ('collapse',)
        }),
        ('Additional Information', {
            'fields': ('remarks', 'marked_by'),
            'classes': ('collapse',)
        }),
        ('System Fields', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )