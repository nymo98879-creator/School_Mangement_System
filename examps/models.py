from django.db import models


class Exam(models.Model):
    EXAM_TYPES = (
        ('mid', 'Mid Term'),
        ('final', 'Final'),
        ('quiz', 'Quiz'),
    )

    title = models.CharField(max_length=100)

    course = models.ForeignKey("courses.Course", on_delete=models.CASCADE)
    school_class = models.ForeignKey("classes.SchoolClass", on_delete=models.CASCADE)
    teacher = models.ForeignKey("teachers.Teacher", on_delete=models.CASCADE)

    exam_date = models.DateField()
    total_marks = models.IntegerField()
    exam_type = models.CharField(max_length=20, choices=EXAM_TYPES)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class ExamResult(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    student = models.ForeignKey("students.Student", on_delete=models.CASCADE)

    marks_obtained = models.DecimalField(max_digits=5, decimal_places=2)
    grade = models.CharField(max_length=5)
    remarks = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.student} - {self.exam}"