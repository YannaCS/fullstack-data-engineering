from django.shortcuts import render, HttpResponse, Http404, get_object_or_404
from blog.models import Post, Category, Comment
from django.contrib.auth.models import User
from django.db.models import F
# Create your views here.
# posts/
def post_list(request):
    posts = Post.objects.filter(published=True).all()
    # return HttpResponse(f'List view {posts.count()}')
    context = {
        'posts': posts
    }
    return render(request, 'index.html', context)

# posts/<int:post_id>
def post_detail(request, post_id):
    post = Post.objects.get(id=post_id)
    if not post:
        raise Http404("Not found")
    
    # INCREASE VIEW COUNT
    # post.views += 1
    # post.save()
    # OR
    # More efficient - avoids race conditions
    Post.objects.filter(id=post_id).update(views=F('views') + 1)
    # Refresh the post object to get updated views count
    post.refresh_from_db()

    comments = post.comments.all()
    context = {
        'post': post,
        'comments': comments
    }

    return render(request, 'post_detail.html', context)

# categories/<int:category_id>
def category_post(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    posts = category.posts.filter(published=True).prefetch_related('categories', 'author')
    # for post in posts: #n+1 problem to prefetch to resolve
    #     post.author()

    context = {
        'posts': posts,
        'category': category
    }
    return render(request, 'category_posts.html', context)

# authors/<int:author_id>
def author_post(request, author_id):
    user = get_object_or_404(User, id=author_id)
    posts = user.posts.filter(published=True).prefetch_related('categories')
    context = {
        'posts': posts,
        'author': user
    }
    return render(request, 'author_posts.html', context)