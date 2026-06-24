from django.contrib.auth.models import User
from django.db import models


class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('user', 'User'),
        ('visitor', 'Visitor'),
        ('admin', 'Admin'),
    ]
    STATUS_CHOICES = [(0, 'Normal'), (1, 'Banned')]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='user')
    nickname = models.CharField(max_length=50, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    avatar_url = models.CharField(max_length=500, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    status = models.SmallIntegerField(choices=STATUS_CHOICES, default=0)
    has_privacy_consent = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'user_profile'

    def __str__(self):
        return f'{self.user.username} ({self.role})'


class UserVerificationCode(models.Model):
    PURPOSE_CHOICES = [
        ('reset_password', 'Reset Password'),
        ('change_email', 'Change Email'),
<<<<<<< HEAD
        ('registration', 'Registration'),
=======
>>>>>>> 5981cf21ae81764086b722a469035686c308c5f9
    ]

    email = models.CharField(max_length=100)
    code = models.CharField(max_length=10)
    purpose = models.CharField(max_length=20, choices=PURPOSE_CHOICES)
    is_used = models.BooleanField(default=False)
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'user_verification_code'


class UserEmailChangeLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='email_change_logs')
    old_email = models.CharField(max_length=100)
    new_email = models.CharField(max_length=100)
    changed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'user_email_change_log'


class UserBlock(models.Model):
    blocker = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blocking')
    blocked = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blocked_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'user_block'
        unique_together = [('blocker', 'blocked')]


class UserPasswordResetLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='password_reset_logs')
    reset_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'user_password_reset_log'
