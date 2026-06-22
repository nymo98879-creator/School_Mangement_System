from django.contrib import admin
from .models import Exam, ExamResult

@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'class_obj', 'exam_type', 'date', 'total_marks', 'is_active']
    list_filter = ['exam_type', 'is_active', 'class_obj']
    search_fields = ['name', 'class_obj__name', 'course__name']
    readonly_fields = ['created_at', 'updated_at']
    list_per_page = 20
    
    fieldsets = (
        ('Exam Information', {
            'fields': ('name', 'class_obj', 'course', 'exam_type')
        }),
        ('Schedule', {
            'fields': ('date', 'time', 'duration')
        }),
        ('Marks Information', {
            'fields': ('total_marks', 'passing_marks')
        }),
        ('Additional Information', {
            'fields': ('description', 'is_active'),
            'classes': ('collapse',)
        }),
        ('System Fields', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(ExamResult)
class ExamResultAdmin(admin.ModelAdmin):
    list_display = ['id', 'student', 'exam', 'marks_obtained', 'grade']
    list_filter = ['grade', 'exam']
    search_fields = ['student__first_name', 'student__last_name', 'exam__name']
    readonly_fields = ['created_at', 'updated_at']
    list_per_page = 20
    
    fieldsets = (
        ('Result Information', {
            'fields': ('student', 'exam', 'marks_obtained', 'grade')
        }),
        ('Additional Information', {
            'fields': ('remarks',),
            'classes': ('collapse',)
        }),
        ('System Fields', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )