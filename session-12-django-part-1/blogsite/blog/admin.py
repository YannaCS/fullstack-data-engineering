from django.contrib import admin
from blog.models import Post, Comment,Category

# Register your models here.
# admin.site.register(Post)
admin.site.register(Comment)
# admin.site.register(Category)

admin.site.site_header = "My Blog"
admin.site.site_title = 'My Blog Portal'

# Customize which fields to be shown
# not use admin.site.register(Category) 
# but use this decorator:
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'post_count', 'created_at')
    
    def post_count(self, obj):
        return obj.posts.count()
    post_count.short_description = 'Number of posts'
    
@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    # ADD 'views' to list_display
    list_display = (
        'title', 'author', 'published', 'views', 
        'is_new',              # NEW: Show if recently published
        'multiple_cats',       # NEW: Show if has multiple categories
        'get_categories'
        )
    
    # fieldsets = (
    #     ('Content', {
    #         'fields': ('title', 'content', 'author')
    #     }),
    # )

    # ADD views to list_filter for filtering by view count
    list_filter = ('published', 'created_at', 'views')
    
    # Make views read-only in admin (optional - prevents manual editing)
    readonly_fields = ('views', 'created_at', 'updated_at')
    
    search_fields = ('title', 'author__username', 'content')

    def get_categories(self, obj):
        return ", ".join([c.name for c in obj.categories.all()])
    get_categories.short_description = 'Categories'

    # NEW: Custom admin method - displays boolean icon
    def is_new(self, obj):
        return obj.published_recently()
    is_new.boolean = True # Display as checkmark/X icon
    is_new.short_description = 'Recent?'
    is_new.admin_order_field = 'created_at'  # Allow sorting by this column

    # NEW: Custom admin method - show if multiple categories
    def multiple_cats(self, obj):
        return obj.has_multiple_categories()
    multiple_cats.boolean = True
    multiple_cats.short_description = 'Multiple Categories?'