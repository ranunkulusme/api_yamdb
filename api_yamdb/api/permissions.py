from rest_framework import permissions
from rest_framework.permissions import SAFE_METHODS, IsAdminUser


class IsAdminOrSuperuser(permissions.BasePermission):
    def has_permission(self, request, view):
        return (request.user.is_authenticated and request.user.is_adminisrator
                or request.user.is_authenticated
                and request.user.is_superuser)


class IsAdminUserOrReadOnly(IsAdminUser):

    def has_permission(self, request, view):
        return (request.user.is_authenticated and request.user.is_adminisrator
                or request.method in SAFE_METHODS)


class OwnerOrReadOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        return (request.user.is_authenticated and request.user.is_adminisrator
                or request.method in SAFE_METHODS)

    def has_object_permission(self, request, view, obj):
        return (request.method == 'DELETE'
                and request.user.is_authenticated
                and request.user.is_adminisrator)


class AdminOrModeratorOrRead(permissions.BasePermission):

    def has_permission(self, request, view):
        return (request.user.is_authenticated
                or request.method in SAFE_METHODS)

    def has_object_permission(self, request, view, obj):
        return (request.method in SAFE_METHODS
                or (request.user.is_authenticated
                    and request.user.is_adminisrator
                    or request.user == obj.author
                    or request.user.is_moderator))
