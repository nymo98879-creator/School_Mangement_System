from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.
class User(AbstractUser):
    ROLE_CHOISES = [
        ('admin', 'Admin'),
        ('teacher', 'Teacher'),
        ('student', 'Student'),
    ]
    role = models.CharField(max_length=50, choices=ROLE_CHOISES, default='student')
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.username