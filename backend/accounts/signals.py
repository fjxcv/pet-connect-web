"""
模块说明：accounts 信号处理器。
"""

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UserProfile
@receiver(post_save, sender=User)

def create_user_profile(sender, instance, created, **kwargs):
    if created:
        role = 'admin' if instance.is_superuser else 'user'
        UserProfile.objects.get_or_create(
            user=instance,
            defaults={'role': role, 'has_privacy_consent': True},
        )
@receiver(post_save, sender=User)

def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        if instance.is_superuser and instance.profile.role != 'admin':
            instance.profile.role = 'admin'
            instance.profile.save(update_fields=['role'])

