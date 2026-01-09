from rest_framework import permissions
class HasCreatePostPermission(permissions.BasePermission):
    
    def has_permission(self, request, view):
        if request.method == 'POST':
            print(request.user.email)
            print(request.user.has_perm('blog.add_post'))
            return False
        else:
            return True