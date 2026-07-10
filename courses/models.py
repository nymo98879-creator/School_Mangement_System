from django.db import models
from teachers.models import Teacher


class Faculty(models.Model):
    """College/Faculty (e.g., College of Science)"""
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True, null=True)
    dean = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, blank=True, related_name='faculties')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Faculties"
        ordering = ['name']


class Department(models.Model):
    """Department (e.g., Computer Science Department)"""
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True, null=True)
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE, related_name='departments')
    head = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, blank=True, related_name='departments')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.code} - {self.name}"
    
    class Meta:
        ordering = ['name']


class Major(models.Model):
    """Major/Program (e.g., BSc Computer Science)"""
    DEGREE_TYPES = [
        ('bachelor', 'Bachelor'),
        ('master', 'Master'),
        ('phd', 'PhD'),
        ('diploma', 'Diploma'),
        ('certificate', 'Certificate'),
    ]
    
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20, unique=True)
    degree_type = models.CharField(max_length=20, choices=DEGREE_TYPES, default='bachelor')
    description = models.TextField(blank=True, null=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='majors')
    duration = models.IntegerField(help_text="Duration in years")
    total_credits = models.IntegerField(help_text="Total credits required to graduate")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.code} - {self.name}"
    
    class Meta:
        ordering = ['name']


class Course(models.Model):
    """Individual course (e.g., CS-101 Introduction to Programming)"""
    LEVEL_CHOICES = [
        ('100', 'Year 1'),
        ('200', 'Year 2'),
        ('300', 'Year 3'),
        ('400', 'Year 4'),
        ('500', 'Year 5'),
    ]
    
    course_id = models.CharField(max_length=20, unique=True, editable=False)
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=200)
    description = models.TextField()
    credits = models.IntegerField()
    level = models.CharField(max_length=10, choices=LEVEL_CHOICES, default='100')
    duration = models.CharField(max_length=50, default='12 weeks')
    fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    # Relationships
    major = models.ForeignKey(
        Major, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='courses'
    )
    teacher = models.ForeignKey(
        Teacher, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='courses'
    )
    prerequisites = models.ManyToManyField('self', symmetrical=False, blank=True)
    time_slots = models.ManyToManyField(
        'classes.TimeSlot', 
        blank=True, 
        related_name='course_time_slots'  # CHANGED
    )
    
    # Many-to-Many relationship with Class
    classes = models.ManyToManyField(
        'classes.Class',
        blank=True,
        related_name='course_classes'  # CHANGED from 'course_set' to 'course_classes'
    )
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.code} - {self.name}"
    
    def save(self, *args, **kwargs):
        if not self.course_id:
            last_course = Course.objects.order_by('id').last()
            if last_course and last_course.course_id:
                try:
                    last_num = int(last_course.course_id[2:])
                    new_num = last_num + 1
                except (ValueError, IndexError):
                    new_num = 1
            else:
                new_num = 1
            self.course_id = f"CS{new_num:03d}"
        
        super().save(*args, **kwargs)
    
    def get_schedule_display(self):
        if self.time_slots.exists():
            return ", ".join([str(slot) for slot in self.time_slots.all()])
        return "Schedule TBD"
    
    def get_classes_display(self):
        """Return string of all classes this course is assigned to"""
        if self.classes.exists():
            return ", ".join([c.name for c in self.classes.all()])
        return "No classes assigned"
    
    class Meta:
        ordering = ['code']