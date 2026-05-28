from django.db import models
from django.conf import settings
# Create your models here.

class Teacher(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    
    gender = models.CharField(max_length=10)
    phone = models.CharField(max_length=20)
    address = models.TextField()
    
    date_of_birth = models.DateField()
    hire_date = models.DateField()
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"
        
