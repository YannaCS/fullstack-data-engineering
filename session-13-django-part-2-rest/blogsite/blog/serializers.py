from .models import Post
from rest_framework import serializers

class PostSerializer(serializers.ModelSerializer):
    # Read-only field from related model
    author_email = serializers.ReadOnlyField(source='author.email')

    class Meta:
        model = Post
        fields = '__all__' # Include all model fields
        
class PostListSerializer(serializers.ModelSerializer):
    author_email = serializers.ReadOnlyField(source='author.email')

    class Meta:
        model = Post
        # Only specific fields for list view (lighter payload)
        fields = ['id', 'title', 'content', 'author', 'published', 'author_email', 'created_at']
        
class PostDetailsSerializer(serializers.ModelSerializer):
    # Custom method field
    author = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ['id', 'title', 'content', 'author', 'published', 'created_at', 'updated_at']
        
    def get_author(self, obj):
        return {
            'id': obj.author.id,
            'username': obj.author.username,
            'email': obj.author.email,
        }
        