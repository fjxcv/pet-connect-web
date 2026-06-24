import random
import string
<<<<<<< HEAD
import secrets
=======
>>>>>>> 5981cf21ae81764086b722a469035686c308c5f9
from datetime import timedelta

from django.contrib.auth.models import User
from django.core.mail import send_mail
<<<<<<< HEAD
from django.conf import settings
import logging
=======
>>>>>>> 5981cf21ae81764086b722a469035686c308c5f9
from django.utils import timezone
from rest_framework import serializers

from .models import UserEmailChangeLog, UserPasswordResetLog, UserProfile, UserVerificationCode


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = [
            'role', 'nickname', 'phone', 'avatar_url', 'address',
            'status', 'has_privacy_consent', 'created_at', 'updated_at',
        ]
        read_only_fields = ['role', 'status', 'created_at', 'updated_at']


class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'is_staff', 'is_superuser', 'profile']
        read_only_fields = ['is_staff', 'is_superuser']


class RegisterSerializer(serializers.ModelSerializer):
    has_privacy_consent = serializers.BooleanField(write_only=True)
    password = serializers.CharField(write_only=True, min_length=8)
<<<<<<< HEAD
    code = serializers.CharField(write_only=True, max_length=10)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'has_privacy_consent', 'code']
=======

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'has_privacy_consent']
>>>>>>> 5981cf21ae81764086b722a469035686c308c5f9

    def validate_has_privacy_consent(self, value):
        if not value:
            raise serializers.ValidationError('Privacy consent is required')
        return value

<<<<<<< HEAD
    def validate(self, attrs):
        # ensure email/code pair is valid for registration
        email = attrs.get('email')
        code = attrs.get('code')
        if not email or not code:
            raise serializers.ValidationError('Email and code are required')
        record = UserVerificationCode.objects.filter(
            email=email,
            code=code,
            purpose='registration',
            is_used=False,
            expires_at__gt=timezone.now(),
        ).first()
        if not record:
            raise serializers.ValidationError('验证码无效或已过期')
        attrs['verify_record'] = record
        return attrs

    def create(self, validated_data):
        consent = validated_data.pop('has_privacy_consent')
        # remove code and extract verify_record before creating user
        validated_data.pop('code', None)
        record = validated_data.pop('verify_record', None)
=======
    def create(self, validated_data):
        consent = validated_data.pop('has_privacy_consent')
>>>>>>> 5981cf21ae81764086b722a469035686c308c5f9
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password'],
        )
        UserProfile.objects.filter(user=user).update(has_privacy_consent=consent)
<<<<<<< HEAD

        # one-time use: delete verification record
        if record:
            try:
                record.delete()
            except Exception:
                record.is_used = True
                record.save(update_fields=['is_used'])

=======
>>>>>>> 5981cf21ae81764086b722a469035686c308c5f9
        return user


class ProfileUpdateSerializer(serializers.Serializer):
    email = serializers.EmailField(required=False)
    nickname = serializers.CharField(max_length=50, required=False, allow_blank=True)
    phone = serializers.CharField(max_length=20, required=False, allow_blank=True)
    avatar_url = serializers.CharField(max_length=500, required=False, allow_blank=True)
    address = serializers.CharField(max_length=255, required=False, allow_blank=True)


def generate_verification_code():
<<<<<<< HEAD
    return ''.join(secrets.choice(string.digits) for _ in range(6))


def create_verification_code(email, purpose, expiry_minutes=None):
    """
    Create and send a verification code.
    Enforces a 1-minute send rate limit per email and clears previous codes for the same purpose.
    expiry_minutes: override expiry in minutes. If None, defaults to 5 for registration, 15 otherwise.
    Raises serializers.ValidationError on rate limit or send failure.
    """
    if expiry_minutes is None:
        expiry_minutes = 5 if purpose == 'registration' else 15

    # rate limit: same email & purpose within 60 seconds
    recent = UserVerificationCode.objects.filter(email=email, purpose=purpose).order_by('-created_at').first()
    if recent and (timezone.now() - recent.created_at).total_seconds() < 60:
        raise serializers.ValidationError('请求过于频繁，请稍后再试')

    # clear previous codes for same email/purpose
    UserVerificationCode.objects.filter(email=email, purpose=purpose).delete()

    code = generate_verification_code()
    expires_at = timezone.now() + timedelta(minutes=expiry_minutes)
=======
    return ''.join(random.choices(string.digits, k=6))


def create_verification_code(email, purpose):
    code = generate_verification_code()
>>>>>>> 5981cf21ae81764086b722a469035686c308c5f9
    UserVerificationCode.objects.create(
        email=email,
        code=code,
        purpose=purpose,
<<<<<<< HEAD
        expires_at=expires_at,
    )

    # send email using Django email backend (configure SMTP via settings)
    try:
        send_mail(
            subject='PawRescue 验证码',
            message=f'您的验证码为：{code}，有效期 {expiry_minutes} 分钟。如非本人操作请忽略。',
            from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', None),
            recipient_list=[email],
            fail_silently=False,
        )
    except Exception as e:
        # log detailed exception for debugging (do not expose internals to clients)
        logging.exception('Failed to send verification email to %s: %s', email, e)
        raise serializers.ValidationError('Failed to send verification email')

=======
        expires_at=timezone.now() + timedelta(minutes=15),
    )
    send_mail(
        subject='PetRescue Verification Code',
        message=f'Your verification code is: {code}. Valid for 15 minutes.',
        from_email=None,
        recipient_list=[email],
        fail_silently=True,
    )
>>>>>>> 5981cf21ae81764086b722a469035686c308c5f9
    return code


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError('Email not registered')
        return value

    def save(self):
        create_verification_code(self.validated_data['email'], 'reset_password')


class PasswordResetConfirmSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField(max_length=10)
    new_password = serializers.CharField(min_length=8, write_only=True)

    def validate(self, attrs):
        record = UserVerificationCode.objects.filter(
            email=attrs['email'],
            code=attrs['code'],
            purpose='reset_password',
            is_used=False,
            expires_at__gt=timezone.now(),
        ).first()
        if not record:
<<<<<<< HEAD
            raise serializers.ValidationError('验证码无效或已过期')
=======
            raise serializers.ValidationError('Invalid or expired verification code')
>>>>>>> 5981cf21ae81764086b722a469035686c308c5f9
        attrs['record'] = record
        return attrs

    def save(self):
        record = self.validated_data['record']
        user = User.objects.get(email=self.validated_data['email'])
        user.set_password(self.validated_data['new_password'])
        user.save()
        record.is_used = True
        record.save(update_fields=['is_used'])
        UserPasswordResetLog.objects.create(user=user)


class EmailChangeRequestSerializer(serializers.Serializer):
    new_email = serializers.EmailField()

    def validate_new_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('Email already in use')
        return value

    def save(self, user):
        create_verification_code(self.validated_data['new_email'], 'change_email')


class EmailChangeConfirmSerializer(serializers.Serializer):
    new_email = serializers.EmailField()
    code = serializers.CharField(max_length=10)

    def validate(self, attrs):
        record = UserVerificationCode.objects.filter(
            email=attrs['new_email'],
            code=attrs['code'],
            purpose='change_email',
            is_used=False,
            expires_at__gt=timezone.now(),
        ).first()
        if not record:
<<<<<<< HEAD
            raise serializers.ValidationError('验证码无效或已过期')
=======
            raise serializers.ValidationError('Invalid or expired verification code')
>>>>>>> 5981cf21ae81764086b722a469035686c308c5f9
        attrs['record'] = record
        return attrs

    def save(self, user):
        record = self.validated_data['record']
        old_email = user.email
        new_email = self.validated_data['new_email']
        user.email = new_email
        user.save(update_fields=['email'])
        record.is_used = True
        record.save(update_fields=['is_used'])
        UserEmailChangeLog.objects.create(user=user, old_email=old_email, new_email=new_email)
