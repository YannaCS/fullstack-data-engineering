from django.urls import path
from blog import views

app_name = 'blog'

urlpatterns = [
    path('posts/', views.post_list, name="index"),
    path('posts/<int:post_id>', views.post_detail, name="post_detail"),
    path('categories/<int:category_id>', views.category_post, name="category_posts"),
    path('authors/<int:author_id>', views.author_post, name="author_posts"),
    
]