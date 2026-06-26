"""
DRF 权限类 visitor/user/admin。
"""

from rest_framework.permissions import BasePermission


def user_is_admin(user):
    """
    功能：判断用户是否为管理员角色。
    参数：user — Django User 实例或 None
    返回：bool — 是否 admin
    【权限】visitor：永远 False；user：非 admin 返回 False；admin：True
    """
    # 分支：未登录或未认证 → visitor
    if not user or not user.is_authenticated:
        return False
    # 分支：Django 超级用户或 staff → admin
    if user.is_superuser or user.is_staff:
        return True
    profile = getattr(user, 'profile', None)
    # 分支：profile.role == 'admin' → admin
    return profile is not None and profile.role == 'admin'


class IsAdminRole(BasePermission):
    """
    功能：DRF 权限类，仅允许 admin 访问 /api/admin/* 等接口。
    【权限】visitor/user：has_permission=False；admin：True
    """
    def has_permission(self, request, view):
        # 调用 user_is_admin 判定
        return user_is_admin(request.user)


class IsActiveUser(BasePermission):
    """
    功能：拦截 status=1（封禁）的用户，保护需要登录的接口。
    【权限】visitor：False；user（正常）：True；user（封禁）：False
    """
    message = 'account_banned'

    def has_permission(self, request, view):
        # 分支：未登录 → 拦截
        if not request.user or not request.user.is_authenticated:
            return False
        profile = getattr(request.user, 'profile', None)
        # status==0 或无 profile → 放行
        return profile is None or profile.status == 0
