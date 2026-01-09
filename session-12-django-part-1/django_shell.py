from blogsite.blog.models import Category, Post, Comment
from django.contrib.auth.models import User

# get object 
post = Post.objects.first()

# create object
cat1 = Category.objects.create(name = 'Tech')
# Alternative: Create but Save Later
cat2 = Category(name='Science')
cat2.save()

# Create or Get
cat, created = Category.objects.get_or_create(name="AI") # Returns (object, created)
# Update or Create
cat, created = Category.objects.update_or_create(name='Science', defaults={"description": "science category"})


# Create user
user1 = User.objects.create_user('john', 'john@example.com', 'password123')
# Create superuser (for admin access)
User.objects.create_superuser('admin', 'admin@example.com', 'admin123')

# All posts of a user
user1.posts.all()

# Create post for a user
post = Post.objects.create(
    title="New Post",
    content="Hello world",
    author=user1   # ForeignKey field
)


# Query foreign keys
post.categories.all()              # Get all categories for post
post.categories.count()            # Count categories
post.categories.filter(name='Tech')  # Filter categories

# Query Helpers
# 1. exists()
Post.objects.filter(title='Hello')          # if empty: <QuerySet []>
Post.objects.filter(title='Hello').exists() # if empty return: False
# 2. first() / last()
Post.objects.first()
Post.objects.last()
# 3. values() & values_list()
Post.objects.values("id", "title", "categories") 
# <QuerySet [{'id': 1, 'title': 'First Post', 'categories': 1}, {'id': 2, 'title': 'Second Post', 'categories': 1}, {'id': 2, 'title': 'Second Post', 'categories': 2}]>
Post.objects.values_list("title", flat=True) # <QuerySet ['First Post', 'Second Post']>
# 4. Q Lookups (OR / complex queries)
from django.db.models import Q
# title contains First OR Tech
Post.objects.filter(Q(title__icontains="First") | Q(title__icontains="Tech")) # <QuerySet [<Post: First Post>]>
# 5. exclude()
Post.objects.exclude(categories__name="Python") # <QuerySet [<Post: First Post>]>
# 6. Order & Limit
Post.objects.order_by('-created_at')[:5]
# 7. Bulk Create / Update
Category.objects.bulk_create([
    Category(name='Health'),
    Category(name='Travel'),
    Category(name='Food')
])
Category.objects.filter(name__in=['Health','Travel']).update(active=True)
# 8. select_related (ForeignKey optimization)
# Use when the relationship is One-to-Many or One-to-One.
posts = Post.objects.select_related("author")
# 9. prefetch_related (Many-to-Many or reverse FK)
posts = Post.objects.prefetch_related("categories", "comments")
# 10. Many-to-Many Through Table (if exists)
post.categories.through.objects.all()
# 11. Delete
Post.objects.filter(id=1).delete()
# 12. Count, Sum, Avg, Max, Min
from django.db.models import Count, Avg
Category.objects.annotate(post_count=Count("posts"))  # <QuerySet [<Category: Web>, <Category: Python>]>
# 13. Distinct
Post.objects.filter(categories__name__icontains="tech").distinct()
# 14. Get Random Object
Post.objects.order_by("?").first()
# 15. Raw SQL Query (rarely needed)
posts = Post.objects.raw("SELECT * FROM blog_post")

# Modify
post.categories.add(cat1)          # Add one
post.categories.add(cat1, cat2)    # Add two categories
post.categories.set([cat1, cat2])  # Replace all
post.categories.remove(cat1)       # Remove one
post.categories.clear()            # Remove all

# Reverse query
cat1.posts.all()               # Get all posts in category
cat1.posts.count()             # Count posts

# Filter posts by category
# Filtering by a Category object, pass the actual model instance
tech = Category.objects.get(name='Tech')
Post.objects.filter(categories=tech)
# Shortcut (filter by the category’s name)
Post.objects.filter(categories__name='Tech')
# case-insensitive
Post.objects.filter(categories__name__iexact='tech')

