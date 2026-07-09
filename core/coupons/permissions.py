from rest_framework import permissions


class IsOwner(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object (Order/Cart) to view or modify it.
    """

    def has_permission(self, request, view):
        # 1. User must be authenticated to access the endpoint
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        # 2. Check object-level ownership (runs on detail views like GET /orders/1/)
        # Adjust 'user' if your model uses a different field name like 'customer' or 'owner'
        return getattr(obj, 'user', None) == request.user