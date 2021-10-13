from rest_framework import permissions
from rest_framework.permissions import SAFE_METHODS, IsAdminUser


class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        if (request.user.is_authenticated and request.user.role == 'admin'):
            return True


class Me(permissions.BasePermission):
    def has_permission(self, request, view):
        if (request.user.is_authenticated and request.method == 'PATCH'
                or request.user.is_authenticated and request.method == 'GET'):
            return True


class IsAdminUserOrReadOnly(IsAdminUser):

    def has_permission(self, request, view):
        is_admin = super().has_permission(request, view)
        return request.method in SAFE_METHODS or is_admin
