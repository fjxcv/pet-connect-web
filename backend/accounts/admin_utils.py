"""
模块说明：源码：backend/accounts/admin_utils.py
"""

from .models import UserProfile

def sync_admin_profile_role(user):
    """Ensure superuser/staff accounts have profile.role=admin."""
    if not user or not user.is_authenticated:
        return
    if not (user.is_superuser or user.is_staff):
        return
    profile, _ = UserProfile.objects.get_or_create(
        user=user,
        defaults={'role': 'admin', 'has_privacy_consent': True},
    )
    if profile.role != 'admin':
        profile.role = 'admin'
        profile.save(update_fields=['role'])

