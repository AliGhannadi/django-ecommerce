from rest_framework import permissions


class IsOwner(permissions.BasePermission):
    """
    Object-level permission to only allow owners of an object to access it.
    For detail views (retrieve/update/destroy), checks obj.user == request.user.
    For list views and custom actions, ownership must be enforced via
    get_queryset() filtering or manual checks in the view logic.
    """

    def has_object_permission(self, request, view, obj):
        return obj.user == request.user
