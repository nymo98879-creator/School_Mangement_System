from django.contrib import admin
from .models import Student

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = [
        'student_id', 
        'get_full_name', 
        'email', 
        'phone', 
        'get_classes_display',  # Changed from 'class_enrolled'
        'major', 
        'year', 
        'is_active'
    ]
    
    list_filter = [
        'is_active', 
        'major', 
        'year', 
        'gender',
        # Removed 'class_enrolled' since it no longer exists
    ]
    
    search_fields = [
        'student_id', 
        'first_name', 
        'last_name', 
        'email', 
        'phone'
    ]
    
    list_per_page = 25
    
    # Add this method to display enrolled classes
    def get_classes_display(self, obj):
        """Display all classes the student is enrolled in"""
        classes = obj.classes_enrolled.filter(is_active=True)
        if classes.exists():
            return ", ".join([c.name for c in classes])
        return "No classes enrolled"
    get_classes_display.short_description = "Classes Enrolled"
    
    # Keep this for backward compatibility
    def get_full_name(self, obj):
        return obj.get_full_name()
    get_full_name.short_description = "Full Name"
    
    # Optional: Add custom fields for better admin display
    def get_classes_count(self, obj):
        return obj.classes_enrolled.filter(is_active=True).count()
    get_classes_count.short_description = "# Classes"
    
    fieldsets = (
        ('Personal Information', {
            'fields': (
                'student_id', 
                'user', 
                'first_name', 
                'last_name', 
                'date_of_birth', 
                'gender',
                'email', 
                'phone', 
                'address'
            )
        }),
        ('Guardian Information', {
            'fields': (
                'guardian_name', 
                'guardian_phone', 
                'guardian_email'
            )
        }),
        ('Academic Information', {
            'fields': (
                'major', 
                'year', 
                'semester', 
                'graduation_year',
                'classes_enrolled',  # Changed from 'class_enrolled'
                'courses'
            )
        }),
        ('Status & Additional', {
            'fields': (
                'is_active', 
                'profile_picture', 
                'qr_code', 
                'qr_registered', 
                'registration_completed'
            )
        }),
        ('Timestamps', {
            'fields': (
                'enrollment_date', 
                'created_at', 
                'updated_at'
            ),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = [
        'student_id', 
        'qr_code', 
        'enrollment_date', 
        'created_at', 
        'updated_at'
    ]
    
    filter_horizontal = ['classes_enrolled', 'courses']  # Add this for ManyToMany fields
    
    actions = ['activate_students', 'deactivate_students', 'generate_qr_codes']
    
    def activate_students(self, request, queryset):
        queryset.update(is_active=True)
        self.message_user(request, f"{queryset.count()} student(s) activated successfully.")
    activate_students.short_description = "Activate selected students"
    
    def deactivate_students(self, request, queryset):
        queryset.update(is_active=False)
        self.message_user(request, f"{queryset.count()} student(s) deactivated successfully.")
    deactivate_students.short_description = "Deactivate selected students"
    
    def generate_qr_codes(self, request, queryset):
        count = 0
        for student in queryset:
            if not student.qr_code:
                student.generate_qr_code()
                student.save()
                count += 1
        self.message_user(request, f"QR codes generated for {count} student(s).")
    generate_qr_codes.short_description = "Generate QR Codes for selected students"