# Django Session 1: Blog app - Quick Reference

## Setup

```bash
# Create virtual environment
uv .venv
# Activate (Mac/Linux)
source .venv/bin/activate

# Install Django
uv pip install django

# Verify installation
python3 -m django --version
```

---

## Create Project

```bash
django-admin startproject blogsite
cd blogsite

python3 manage.py runserver
```
Visit: `http://127.0.0.1:8000/`

---

## Create App

```bash
python3 manage.py startapp blog
```

### Register App

```python
# blogsite/settings.py
INSTALLED_APPS = [
    'blog.apps.BlogConfig',  # Add this
    'django.contrib.admin',
    # ... other apps
]
```

---

## Create Models

```python
# blog/models.py
from django.db import models
from django.contrib.auth.models import User

class Category(models.Model):
    ...

class Post(models.Model):
    ...

class Comment(models.Model):
    ...
```

Set DATABASES connection engine, name (database name), user and password
```python
# /blogsite/blogsite/settings.py
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "blog-app-test",
        "USER": "postgres",
        "PASSWORD": "mypassword",
        "HOST": "127.0.0.1",
        "PORT": "5432",
    }
}

```
---

## Step 4: Migrations

```bash
python manage.py makemigrations blog
python manage.py migrate
```

### Three-Step Process
1. Change models (`models.py`)
2. `python manage.py makemigrations`
3. `python manage.py migrate`

**Note:** Django auto-creates a junction table for ManyToMany!


---

## Admin

create admin user:
```bash
python manage.py createsuperuser
# Username: admin, Password: admin123
```


### Register Models

```python
# blog/admin.py
from django.contrib import admin
from .models import Category, Post, Comment

admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(Category)
```

More admin custom configuration at https://docs.djangoproject.com/en/5.2/ref/contrib/admin/

Visit: `http://127.0.0.1:8000/admin/`

---

## Views

```python
# blog/views.py

def index(request):
    ...

def post_detail(request, post_id):
    ...

def category_posts(request, category_id):
    ...

def author_posts(request, author_id):
    ...
```

---

## Route URLs

```python
# blog/urls.py (create this)
from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.index, name='index'),
    path('post/<int:post_id>/', views.post_detail, name='post_detail'),
    path('category/<int:category_id>/', views.category_posts, name='category_posts'),
    path('author/<int:author_id>/', views.author_posts, name='author_posts'),
]
```

```python
# blogsite/urls.py
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('', include('blog.urls')),
    path('admin/', admin.site.urls),
]
```

---

## Templates

base.html / index.html / post_detail.html / category_posts.html

---

## Testing

```bash
python manage.py runserver
```

**URLs:**
- `http://127.0.0.1:8000/` - Posts with multiple categories
- `http://127.0.0.1:8000/admin/` - Try the category selector!
- `http://127.0.0.1:8000/post/1/` - Post with all categories
- `http://127.0.0.1:8000/category/1/` - Posts in one category

---

## Key Differences: ManyToMany

| ForeignKey | ManyToMany |
|------------|------------|
| `category = ForeignKey(...)` | `categories = ManyToManyField(...)` |
| One post → One category | One post → Many categories |
| `post.category` | `post.categories.all()` |
| `post.category = tech` | `post.categories.add(tech)` |
| `category.posts.all()` | `category.posts.all()` |
| `select_related()` | `prefetch_related()` |

---

## Project Structure

```
blogsite/
├── manage.py
├── blogsite/
│   ├── settings.py
│   └── urls.py
└── blog/
    ├── models.py
    ├── views.py
    ├── urls.py
    ├── admin.py
    └── templates/
```

---

## Quick Commands

```bash
# Setup
python3 -m venv venv
source venv/bin/activate
uv pip install django

# Project
django-admin startproject blogsite
python manage.py startapp blog

# Database
python manage.py makemigrations
python manage.py migrate

# Admin & Server
python manage.py createsuperuser
python manage.py runserver
python manage.py shell
```

---

---

## Django Shell - ManyToMany Operations

```bash
python manage.py shell
```

```python
from blog.models import Category, Post, Comment
from django.contrib.auth.models import User

post1 = Post.objects.first()

post.categories.all() # many - many query

post.author #one - many query

Post.objects.filter(categories__name='Python') # filter

# Posts with at least one category
Post.objects.exclude(categories=None)

Post.objects.exclude(categories=None).count()

category = Category.objects.first()

category.posts.all() # query posts from category
```

### ManyToMany Quick Reference

```python
# Add relationships
post.categories.add(cat1)
post.categories.add(cat1, cat2, cat3)
post.categories.set([cat1, cat2])

# Remove relationships
post.categories.remove(cat1)
post.categories.clear()

# Query
post.categories.all()
post.categories.count()
category.posts.all()
category.posts.count()

# Check
post.categories.filter(name='Tech').exists()

# Filter posts by category
Post.objects.filter(categories=tech)
Post.objects.filter(categories__name='Python')
```
