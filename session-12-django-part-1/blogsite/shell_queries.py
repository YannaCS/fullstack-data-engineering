#!/usr/bin/env python
"""
Django ORM Queries - Homework Assignment
Run this script to execute all 8 queries
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'blogsite.settings')
django.setup()

# Now import models
from blog.models import Post, Category, Comment
from django.contrib.auth.models import User

def main():
    print("=" * 60)
    print("DJANGO ORM QUERIES OUTPUT")
    print("=" * 60)

    # 1. Published posts
    print("\n1. Published posts:")
    published = Post.objects.filter(published=True)
    print(f"   Count: {published.count()}")
    for post in published:
        print(f"   • {post.title} by {post.author.username}")

    # 2. Posts by john
    print("\n2. Posts by user 'john':")
    john_posts = Post.objects.filter(author__username='john')
    print(f"   Count: {john_posts.count()}")
    for post in john_posts:
        print(f"   • {post.title}")

    # 3. Posts in Technology
    print("\n3. Posts in 'Technology' category:")
    tech_posts = Post.objects.filter(categories__name='Technology')
    print(f"   Count: {tech_posts.count()}")
    for post in tech_posts:
        print(f"   • {post.title}")

    # 4. Total posts
    print("\n4. Total posts:")
    print(f"   Count: {Post.objects.count()}")

    # 5. Total comments
    print("\n5. Total comments:")
    print(f"   Count: {Comment.objects.count()}")

    # 6. Posts with no categories
    print("\n6. Posts with no categories:")
    no_cats = Post.objects.filter(categories__isnull=True)
    print(f"   Count: {no_cats.count()}")
    for post in no_cats:
        print(f"   • {post.title}")

    # 7. 3 newest posts
    print("\n7. 3 Newest posts:")
    newest = Post.objects.order_by('-created_at')[:3]
    for post in newest:
        print(f"   • {post.title} ({post.created_at.strftime('%Y-%m-%d %H:%M')})")

    # 8. Categories alphabetically
    print("\n8. Categories (alphabetical):")
    categories = Category.objects.order_by('name')
    for cat in categories:
        print(f"   • {cat.name} ({cat.posts.count()} posts)")

    print("\n" + "=" * 60)
    print("ALL QUERIES COMPLETED!")
    print("=" * 60)

if __name__ == '__main__':
    main()