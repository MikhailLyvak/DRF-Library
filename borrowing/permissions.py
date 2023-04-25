from rest_framework import permissions


class IsBorrower(permissions.BasePermission):
    """
    Custom permission to only allow borrowers to see their own borrowings.
    """

    def has_object_permission(self, request, view, obj):
        # Allow GET requests for superusers
        if request.method in permissions.SAFE_METHODS and request.user.is_superuser:
            return True

        # Allow borrowers to see their own borrowings
        return obj.user == request.user
