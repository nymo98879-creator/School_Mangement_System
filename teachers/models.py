from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Teacher(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other')
    ]
    
    POSITION_CHOICES = [
        ('dean', '👑 Dean'),
        ('associate_dean', 'Associate Dean'),
        ('department_head', 'Department Head'),
        ('professor', 'Professor'),
        ('associate_professor', 'Associate Professor'),
        ('assistant_professor', 'Assistant Professor'),
        ('lecturer', 'Lecturer'),
        ('instructor', 'Instructor'),
        ('teaching_assistant', 'Teaching Assistant'),
    ]
    
    # ===== BASIC INFORMATION =====
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='teacher_profile', null=True, blank=True)
    teacher_id = models.CharField(max_length=20, unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    phone = models.CharField(max_length=15)
    email = models.EmailField()
    address = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='teachers/', blank=True, null=True)
    
    # ===== PROFESSIONAL INFORMATION =====
    qualification = models.CharField(max_length=200, blank=True, null=True)
    specialization = models.CharField(max_length=200, blank=True, null=True)
    years_of_experience = models.IntegerField(default=0)
    
    # ===== POSITION =====
    position = models.CharField(
        max_length=50, 
        choices=POSITION_CHOICES, 
        default='lecturer',
        help_text="Current position/rank of the teacher"
    )
    
    # ===== EMPLOYMENT =====
    hired_date = models.DateField(null=True, blank=True)
    
    # ===== STATUS =====
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.teacher_id})"
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def is_dean(self):
        return self.position == 'dean'
    
    def is_associate_dean(self):
        return self.position == 'associate_dean'
    
    def is_department_head(self):
        return self.position == 'department_head'
    
    def is_professor(self):
        return self.position in ['professor', 'associate_professor', 'assistant_professor']
    
    def get_position_display(self):
        return dict(self.POSITION_CHOICES).get(self.position, self.position)
    
    def get_dean_of_faculty(self):
        """Get the faculty this teacher is dean of"""
        from courses.models import Faculty
        return Faculty.objects.filter(dean=self).first()
    
    def get_department_head_of(self):
        """Get the department this teacher is head of"""
        from courses.models import Department
        return Department.objects.filter(head=self).first()
    
    def has_phd(self):
        """Check if teacher has a Ph.D. qualification"""
        if self.qualification:
            return 'Ph.D.' in self.qualification or 'PhD' in self.qualification
        return False
    
    class Meta:
        ordering = ['first_name', 'last_name']