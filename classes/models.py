from django.db import models


class SchoolClass(models.Model):
    name = models.CharField(max_length=50)
    grade_level = models.CharField(max_length=20)
    academic_year = models.CharField(max_length=10)
    capacity = models.IntegerField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Enrollment(models.Model):
    student = models.ForeignKey("students.Student", on_delete=models.CASCADE)
    school_class = models.ForeignKey(SchoolClass, on_delete=models.CASCADE)

    enrolled_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.student} - {self.school_class}"