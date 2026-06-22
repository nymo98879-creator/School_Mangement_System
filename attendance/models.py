from django.db import models
from students.models import Student
from classes.models import Class
from teachers.models import Teacher

class Attendance(models.Model):
    STATUS_CHOICES = [
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('late', 'Late'),
        ('excused', 'Excused')
    ]
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='attendances')
    class_obj = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='attendances', null=True, blank=True)
    date = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='present')
    time_in = models.TimeField(null=True, blank=True)
    time_out = models.TimeField(null=True, blank=True)
    remarks = models.TextField(blank=True, null=True)
    marked_by = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, blank=True, related_name='marked_attendances')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['student', 'class_obj', 'date']
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.student} - {self.class_obj} - {self.date} - {self.get_status_display()}"