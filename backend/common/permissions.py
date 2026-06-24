from rest_framework.permissions import BasePermission


def user_is_admin(user):
    if not user or not user.is_authenticated:
        return False
    if user.is_superuser or user.is_staff:
        return True
    profile = getattr(user, 'profile', None)
    return profile is not None and profile.role == 'admin'


class IsAdminRole(BasePermission):
    def has_permission(self, request, view):
        return user_is_admin(request.user)


class IsActiveUser(BasePermission):
    message = 'account_banned'

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        profile = getattr(request.user, 'profile', None)
        return profile is None or profile.status == 0
