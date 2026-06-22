from django.db import models
from classes.models import Class
from courses.models import Course
from students.models import Student

class Exam(models.Model):
    EXAM_TYPES = [
        ('midterm', 'Midterm'),
        ('final', 'Final'),
        ('quiz', 'Quiz'),
        ('assignment', 'Assignment'),
        ('project', 'Project')
    ]
    
    name = models.CharField(max_length=100)
    class_obj = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='exam_classes', null=True, blank=True)  # Changed related_name
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='exam_courses', null=True, blank=True)  # Changed related_name
    exam_type = models.CharField(max_length=20, choices=EXAM_TYPES, default='midterm')
    date = models.DateField(null=True, blank=True)
    time = models.TimeField(null=True, blank=True)
    duration = models.IntegerField(help_text="Duration in minutes", default=60)
    total_marks = models.IntegerField(default=100)
    passing_marks = models.IntegerField(default=40)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} - {self.class_obj.name if self.class_obj else 'No Class'}"
    
    class Meta:
        ordering = ['-date']
        verbose_name_plural = "Exams"

class ExamResult(models.Model):
    GRADE_CHOICES = [
        ('A+', 'A+'),
        ('A', 'A'),
        ('A-', 'A-'),
        ('B+', 'B+'),
        ('B', 'B'),
        ('B-', 'B-'),
        ('C+', 'C+'),
        ('C', 'C'),
        ('C-', 'C-'),
        ('D', 'D'),
        ('F', 'F'),
    ]
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='exam_result_students', null=True, blank=True)  # Changed related_name
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='exam_results', null=True, blank=True)  # Changed related_name
    marks_obtained = models.IntegerField(default=0)
    grade = models.CharField(max_length=2, choices=GRADE_CHOICES, default='F')
    remarks = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.student} - {self.exam.name if self.exam else 'No Exam'} - {self.grade}"
    
    def save(self, *args, **kwargs):
        # Auto-calculate grade based on marks
        if self.exam and self.exam.total_marks > 0 and self.marks_obtained is not None:
            percentage = (self.marks_obtained / self.exam.total_marks) * 100
            if percentage >= 90:
                self.grade = 'A+'
            elif percentage >= 80:
                self.grade = 'A'
            elif percentage >= 75:
                self.grade = 'A-'
            elif percentage >= 70:
                self.grade = 'B+'
            elif percentage >= 65:
                self.grade = 'B'
            elif percentage >= 60:
                self.grade = 'B-'
            elif percentage >= 55:
                self.grade = 'C+'
            elif percentage >= 50:
                self.grade = 'C'
            elif percentage >= 45:
                self.grade = 'C-'
            elif percentage >= 40:
                self.grade = 'D'
            else:
                self.grade = 'F'
        super().save(*args, **kwargs)
    
    class Meta:
        unique_together = ['student', 'exam']
        ordering = ['-exam__date']