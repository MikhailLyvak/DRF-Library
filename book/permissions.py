from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsAdminOrReadOnly(BasePermission):
    """
    Custom permission to only users see only list of books.
    """
    def has_permission(self, request, view):
        return bool(
            (
                request.method in SAFE_METHODS
                and request.user
            )
            or (request.user and request.user.is_staff)
        )
