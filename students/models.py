from django.db import models
from django.contrib.auth import get_user_model
from classes.models import Class
from courses.models import Major, Course
import qrcode
from io import BytesIO
from django.core.files import File
from PIL import Image
import json

User = get_user_model()

class Student(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other')
    ]
    
    YEAR_CHOICES = [
        ('1', '1st Year'),
        ('2', '2nd Year'),
        ('3', '3rd Year'),
        ('4', '4th Year'),
        ('5', '5th Year'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile', null=True, blank=True)
    student_id = models.CharField(max_length=20, unique=True, editable=False)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    phone = models.CharField(max_length=15)
    email = models.EmailField()
    address = models.TextField()
    guardian_name = models.CharField(max_length=100)
    guardian_phone = models.CharField(max_length=15)
    guardian_email = models.EmailField(blank=True, null=True)
    enrollment_date = models.DateField(auto_now_add=True)
    
    # ===== UNIVERSITY SPECIFIC FIELDS =====
    major = models.ForeignKey(Major, on_delete=models.SET_NULL, null=True, blank=True, related_name='students')
    year = models.CharField(max_length=10, choices=YEAR_CHOICES, default='1')
    semester = models.IntegerField(default=1, help_text="Current semester (1-8)")
    graduation_year = models.IntegerField(null=True, blank=True)
    
    # CHANGE THIS: Replace ForeignKey with ManyToManyField
    # REMOVE: class_enrolled = models.ForeignKey(Class, on_delete=models.SET_NULL, null=True, blank=True, related_name='students')
    # ADD THIS:
    classes_enrolled = models.ManyToManyField(
        Class, 
        blank=True, 
        related_name='enrolled_students'
    )
    
    courses = models.ManyToManyField(Course, blank=True, related_name='students')
    
    is_active = models.BooleanField(default=True)
    profile_picture = models.ImageField(upload_to='students/', blank=True, null=True)
    qr_code = models.ImageField(upload_to='qr_codes/', blank=True, null=True)
    qr_registered = models.BooleanField(default=False)
    registration_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.student_id})"
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def get_courses_list(self):
        return self.courses.all()
    
    def get_courses_count(self):
        return self.courses.count()
    
    def is_enrolled_in_course(self, course_id):
        return self.courses.filter(id=course_id).exists()
    
    # ===== NEW METHODS FOR MULTIPLE CLASSES =====
    def get_classes_enrolled(self):
        """Get all classes the student is enrolled in"""
        return self.classes_enrolled.filter(is_active=True)
    
    def get_classes_count(self):
        """Get number of classes the student is enrolled in"""
        return self.classes_enrolled.filter(is_active=True).count()
    
    def is_enrolled_in_class(self, class_obj):
        """Check if student is enrolled in a specific class"""
        return self.classes_enrolled.filter(id=class_obj.id).exists()
    
    def get_class_names(self):
        """Get names of all classes student is enrolled in"""
        return ", ".join([c.name for c in self.classes_enrolled.filter(is_active=True)])
    
    def generate_qr_code(self):
        if not self.student_id:
            return
        
        qr_data = {
            'student_id': self.student_id,
            'name': self.get_full_name(),
            'email': self.email,
            'major': self.major.name if self.major else None,
            'year': self.year,
            'classes': [{'id': c.id, 'name': c.name} for c in self.classes_enrolled.all()],
            'courses': [{'id': c.id, 'name': c.name} for c in self.courses.all()],
            'type': 'student_registration'
        }
        
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(json.dumps(qr_data))
        qr.make(fit=True)
        
        qr_image = qr.make_image(fill_color="black", back_color="white")
        
        buffer = BytesIO()
        qr_image.save(buffer, 'PNG')
        
        filename = f"qr_{self.student_id}.png"
        self.qr_code.save(filename, File(buffer), save=False)
    
    def save(self, *args, **kwargs):
        if not self.student_id:
            existing_ids = Student.objects.values_list('student_id', flat=True)
            max_num = 0
            for sid in existing_ids:
                if sid and sid.startswith('STU'):
                    try:
                        num = int(sid[3:])
                        if num > max_num:
                            max_num = num
                    except (ValueError, IndexError):
                        continue
            new_num = max_num + 1
            self.student_id = f"STU{new_num:04d}"
        
        super().save(*args, **kwargs)
        
        if not self.qr_code and self.student_id:
            self.generate_qr_code()
            super().save(update_fields=['qr_code'])

    class Meta:
        ordering = ['-enrollment_date']