from datetime import datetime, timedelta
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# Create your models here.

class Category(models.Model):
    # CharField: Variable-length string
    name = models.CharField(max_length=50, unique=True)
    # DateTimeField: Timestamp
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Defines string representation of the object (used in admin and shell)
    def __str__(self) -> str:
        return self.name
    
    # The Meta class provides metadata about the model
    class Meta:
        verbose_name_plural = 'Categories' # Plural name in admin

class Post(models.Model):
    title = models.CharField(max_length=200)
    # TextField: Unlimited text
    content = models.TextField()
    
    # ForeignKey: Many-to-One relationship
    author = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, # Delete posts when user deleted
        related_name='posts'      # Reverse relation: user.posts.all
    )
    
    # ManyToManyField: Many-to-Many relationship
    categories = models.ManyToManyField(
        Category, 
        related_name='posts', 
        blank=True  # Optional in forms
    )
    
    created_at = models.DateTimeField(auto_now_add=True) # Set once
    updated_at = models.DateTimeField(auto_now=True) # Update always
    
    published = models.BooleanField(default=False)

    # new field required in QA
    views = models.IntegerField(default=0) # Track number of views
    
    def __str__(self) -> str:
        return self.title   # Shows "Post Title" instead of "Post object (1)"
    
    # Custom model method
    def comment_count(self):
        return self.comments.count()
    
    def get_excerpt(self):
        """Return first 100 characters of content"""
        if len(self.content) > 100:
            return self.content[:100] + '...'
        return self.content

    def published_recently(self):
        """Check if published in last 7 days"""
        seven_days_ago = timezone.now() - timedelta(days=7)
        # cannot use datetime.now()
        # Django stores all datetimes in UTC with timezone information. 
        # You need to use timezone-aware datetimes in your comparisons
        return self.created_at >= seven_days_ago

    def has_multiple_categories(self):
        """Check if post has more than one category"""
        return self.categories.count() > 1


class Comment(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self) -> str:
        return f"Comment by {self.author.username} on {self.post.title}"
    
    
