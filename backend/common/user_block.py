"""
模块说明：源码：backend/common/user_block.py
"""

from accounts.models import UserBlock

def is_blocked(viewer, profile_owner) -> bool:

    if not viewer or not getattr(viewer, 'is_authenticated', False) or not viewer.is_authenticated:

        return False

    if not profile_owner or viewer.pk == profile_owner.pk:

        return False

    return UserBlock.objects.filter(blocker=profile_owner, blocked=viewer).exists()

