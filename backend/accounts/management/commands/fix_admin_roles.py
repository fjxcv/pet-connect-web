"""
模块说明：源码：backend/accounts/management/commands/fix_admin_roles.py
"""

from django.contrib.auth import get_user_model

from django.core.management.base import BaseCommand

from accounts.admin_utils import sync_admin_profile_role

User = get_user_model()

class Command(BaseCommand):

    help = 'Sync profile.role=admin for superuser/staff accounts'

    def handle(self, *args, **options):

        count = 0

        for user in User.objects.filter(is_superuser=True) | User.objects.filter(is_staff=True):

            sync_admin_profile_role(user)

            count += 1

        self.stdout.write(self.style.SUCCESS(f'Synced {count} admin account(s).'))

