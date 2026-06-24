import random
import string
from datetime import timedelta

from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail import send_mail
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

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'has_privacy_consent']

    def validate_has_privacy_consent(self, value):
        if not value:
            raise serializers.ValidationError('Privacy consent is required')
        return value

    def create(self, validated_data):
        consent = validated_data.pop('has_privacy_consent')
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password'],
        )
        UserProfile.objects.filter(user=user).update(has_privacy_consent=consent)
        return user


class ProfileUpdateSerializer(serializers.Serializer):
    email = serializers.EmailField(required=False)
    nickname = serializers.CharField(max_length=50, required=False, allow_blank=True)
    phone = serializers.CharField(max_length=20, required=False, allow_blank=True)
    avatar_url = serializers.CharField(max_length=500, required=False, allow_blank=True)
    address = serializers.CharField(max_length=255, required=False, allow_blank=True)


def generate_verification_code():
    return ''.join(random.choices(string.digits, k=6))


def create_verification_code(email, purpose):
    code = generate_verification_code()
    UserVerificationCode.objects.create(
        email=email,
        code=code,
        purpose=purpose,
        expires_at=timezone.now() + timedelta(minutes=15),
    )
    if purpose == 'reset_password':
        recipient = settings.PASSWORD_RESET_CODE_RECIPIENT
        subject = '\u3010\u6d41\u6d6a\u5ba0\u7269\u6551\u52a9\u5e73\u53f0\u3011\u5bc6\u7801\u91cd\u7f6e\u9a8c\u8bc1\u7801'
        message = (
            f'\u60a8\u6b63\u5728\u7533\u8bf7\u91cd\u7f6e\u8d26\u53f7\u90ae\u7bb1\u4e3a {email} \u7684\u5bc6\u7801\u3002\n'
            f'\u9a8c\u8bc1\u7801\uff1a{code}\n'
            f'\u6709\u6548\u671f 15 \u5206\u949f\u3002\u5982\u975e\u672c\u4eba\u64cd\u4f5c\u8bf7\u5ffd\u7565\u3002'
        )
    else:
        recipient = email
        subject = 'PetRescue Verification Code'
        message = f'Your verification code is: {code}. Valid for 15 minutes.'
    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[recipient],
        fail_silently=False,
    )
    return code


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError('Email not registered')
        return value

    def save(self):
        try:
            create_verification_code(self.validated_data['email'], 'reset_password')
        except Exception as exc:
            raise serializers.ValidationError(
                {'detail': '\u9a8c\u8bc1\u7801\u90ae\u4ef6\u53d1\u9001\u5931\u8d25\uff0c\u8bf7\u7a0d\u540e\u91cd\u8bd5'}
            ) from exc


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
            raise serializers.ValidationError('Invalid or expired verification code')
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
            raise serializers.ValidationError('Invalid or expired verification code')
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
