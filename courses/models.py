from django.db import models


class Course(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField()
    credit_hours = models.IntegerField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.name


class CourseAssignment(models.Model):
    teacher = models.ForeignKey("teachers.Teacher", on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    school_class = models.ForeignKey("classes.SchoolClass", on_delete=models.CASCADE)

    assigned_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.course} - {self.school_class}"