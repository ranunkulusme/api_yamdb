from rest_framework import permissions


class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        if (request.user.is_authenticated and request.user.role == 'admin'):
            return True


class Me(permissions.BasePermission):
    def has_permission(self, request, view):
        if (request.user.is_authenticated and request.method == 'PATCH'
                or request.user.is_authenticated and request.method == 'GET'):
            return True
