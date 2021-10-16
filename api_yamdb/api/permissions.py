from rest_framework import permissions
from rest_framework.permissions import SAFE_METHODS, IsAdminUser


class IsAdminOrSuperuser(permissions.BasePermission):
    def has_permission(self, request, view):
        if (request.user.is_authenticated and request.user.role == 'admin'
                or request.user.is_authenticated
                and request.user.is_superuser):
            return True


class IsAdminUserOrReadOnly(IsAdminUser):

    def has_permission(self, request, view):
        if (request.user.is_authenticated and request.user.role == 'admin'
                or request.method in SAFE_METHODS):
            return True


class OwnerOrReadOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        if (request.user.is_authenticated and request.user.role == 'admin'
                or request.method in SAFE_METHODS):
            return True

    def has_object_permission(self, request, view, obj):
        if (request.method == 'DELETE'
                and request.user.is_authenticated
                and request.user.role == 'admin'):
            return True


class AdminOrModeratorOrRead(permissions.BasePermission):

    def has_permission(self, request, view):
        if (request.user.is_authenticated
                or request.method in SAFE_METHODS):
            return True

    def has_object_permission(self, request, view, obj):
        if (request.method in SAFE_METHODS
            or (request.user.is_authenticated
                and request.user.role == 'admin'
                or request.user == obj.author
                or request.user.role == 'moderator')):
            return True
