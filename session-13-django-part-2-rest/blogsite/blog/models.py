from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

class User(AbstractUser):
    email = models.EmailField(unique=True)
    age = models.IntegerField(null=True)
    
    USERNAME_FIELD='email'
    REQUIRED_FIELDS=['username']
    
    def __str__(self) -> str:
        return self.email

class Post(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    published = models.BooleanField(default=False)
    
    def __str__(self) -> str:
        return self.title