from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow admins and staff to edit objects.
    Read permissions are allowed to any request,
    so we'll always allow GET, HEAD or OPTIONS requests.
    """

    def has_permission(self, request, view):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to authenticated admin and staff users.
        return (request.user and 
                request.user.is_authenticated and 
                (request.user.is_staff or request.user.is_superuser))