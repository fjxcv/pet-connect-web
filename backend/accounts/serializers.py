"""
模块说明：accounts 模块序列化器。

负责账号相关请求/响应数据的校验与转换，涵盖：
- 用户注册、个人资料读写
- 邮箱验证码生成与校验（重置密码、更换邮箱）
- 对外暴露的用户信息结构（含 profile 嵌套）
"""

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
    """
    用户扩展资料序列化器。

    用于嵌套在 UserSerializer 中返回昵称、头像、角色等信息；
    role 与 status 由系统维护，客户端不可直接修改。
    """

    class Meta:
        model = UserProfile
        fields = [
            'role', 'nickname', 'phone', 'avatar_url', 'address',
            'status', 'has_privacy_consent', 'created_at', 'updated_at',
        ]
        # 角色、状态、时间戳仅服务端写入，前端只读
        read_only_fields = ['role', 'status', 'created_at', 'updated_at']


class UserSerializer(serializers.ModelSerializer):
    """
    用户完整信息序列化器。

    组合 Django User 基础字段与 UserProfile 扩展资料，
    用于注册成功、登录成功、资料查询等接口的响应体。
    """

    # 嵌套返回 profile 子对象
    profile = UserProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'is_staff', 'is_superuser', 'profile']
        # 后台管理员标记不允许客户端篡改
        read_only_fields = ['is_staff', 'is_superuser']


class RegisterSerializer(serializers.ModelSerializer):
    """
    账号注册序列化器。

    权限：visitor（未登录游客）可调用。
    校验用户名、邮箱、密码及隐私协议同意后创建用户账号。
    """

    # 隐私协议同意标记，仅写入不返回
    has_privacy_consent = serializers.BooleanField(write_only=True)
    # 登录密码，最少 8 位，仅写入不返回
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'has_privacy_consent']

    def validate_has_privacy_consent(self, value):
        """
        校验用户是否勾选隐私协议。

        参数:
            value (bool): 前端提交的同意标记
        返回:
            bool: 校验通过后的原值
        异常:
            ValidationError: 未同意隐私协议时抛出
        """
        if not value:
            raise serializers.ValidationError('Privacy consent is required')
        return value

    def create(self, validated_data):
        """
        创建新用户并写入隐私协议同意状态。

        参数:
            validated_data (dict): 已通过校验的注册字段
        返回:
            User: 新创建的用户实例
        """
        consent = validated_data.pop('has_privacy_consent')
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password'],
        )
        # 信号可能已创建 profile，此处更新隐私同意标记
        UserProfile.objects.filter(user=user).update(has_privacy_consent=consent)
        return user


class ProfileUpdateSerializer(serializers.Serializer):
    """
    个人资料更新序列化器。

    权限：user / admin（需已登录）。
    所有字段均为可选，仅更新请求体中实际提交的字段。
    注意：直接修改 email 走本序列化器；更换绑定邮箱需走验证码流程。
    """

    email = serializers.EmailField(required=False)
    nickname = serializers.CharField(max_length=50, required=False, allow_blank=True)
    phone = serializers.CharField(max_length=20, required=False, allow_blank=True)
    avatar_url = serializers.CharField(max_length=500, required=False, allow_blank=True)
    address = serializers.CharField(max_length=255, required=False, allow_blank=True)


def generate_verification_code():
    """
    生成 6 位纯数字邮箱验证码。

    返回:
        str: 6 位数字字符串
    """
    return ''.join(random.choices(string.digits, k=6))


def create_verification_code(email, purpose):
    """
    创建验证码记录并发送邮件。

    根据用途向不同收件人发送邮件：
    - reset_password：发往配置的 PASSWORD_RESET_CODE_RECIPIENT（开发环境可统一收件）
    - change_email：发往用户填写的新邮箱

    参数:
        email (str): 关联的邮箱地址（重置密码时为注册邮箱，换绑时为 new_email）
        purpose (str): 用途，'reset_password' 或 'change_email'
    返回:
        str: 生成的验证码（调用方通常不返回给前端，仅用于测试）
    """
    code = generate_verification_code()
    UserVerificationCode.objects.create(
        email=email,
        code=code,
        purpose=purpose,
        expires_at=timezone.now() + timedelta(minutes=15),
    )
    if purpose == 'reset_password':
        # 重置密码：邮件发往配置的统一收件地址（便于开发调试）
        recipient = settings.PASSWORD_RESET_CODE_RECIPIENT
        subject = '\u3010\u6d41\u6d6a\u5ba0\u7269\u6551\u52a9\u5e73\u53f0\u3011\u5bc6\u7801\u91cd\u7f6e\u9a8c\u8bc1\u7801'
        message = (
            f'\u60a8\u6b63\u5728\u7533\u8bf7\u91cd\u7f6e\u8d26\u53f7\u90ae\u7bb1\u4e3a {email} \u7684\u5bc6\u7801\u3002\n'
            f'\u9a8c\u8bc1\u7801\uff1a{code}\n'
            f'\u6709\u6548\u671f 15 \u5206\u949f\u3002\u5982\u975e\u672c\u4eba\u64cd\u4f5c\u8bf7\u5ffd\u7565\u3002'
        )
    else:
        # 更换邮箱：验证码发往用户填写的新邮箱
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
    """
    申请重置密码序列化器（第一步：发送验证码）。

    权限：visitor（未登录游客）可调用。
    校验邮箱已注册后，向该邮箱发送 6 位验证码。
    """

    email = serializers.EmailField()

    def validate_email(self, value):
        """
        校验邮箱是否已在平台注册。

        参数:
            value (str): 用户提交的邮箱
        返回:
            str: 校验通过的邮箱
        异常:
            ValidationError: 邮箱未注册时抛出
        """
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError('Email not registered')
        return value

    def save(self):
        """
        生成验证码并发送邮件。

        异常:
            ValidationError: 邮件发送失败时抛出友好提示
        """
        try:
            create_verification_code(self.validated_data['email'], 'reset_password')
        except Exception as exc:
            raise serializers.ValidationError(
                {'detail': '\u9a8c\u8bc1\u7801\u90ae\u4ef6\u53d1\u9001\u5931\u8d25\uff0c\u8bf7\u7a0d\u540e\u91cd\u8bd5'}
            ) from exc


class PasswordResetConfirmSerializer(serializers.Serializer):
    """
    确认重置密码序列化器（第二步：验证码 + 新密码）。

    权限：visitor（未登录游客）可调用。
    校验验证码有效且未使用后，更新用户密码并记录重置日志。
    """

    email = serializers.EmailField()
    code = serializers.CharField(max_length=10)
    new_password = serializers.CharField(min_length=8, write_only=True)

    def validate(self, attrs):
        """
        校验验证码是否匹配、未使用且未过期。

        参数:
            attrs (dict): 包含 email、code、new_password 的字段字典
        返回:
            dict: 附加 record（验证码记录对象）后的 attrs
        异常:
            ValidationError: 验证码无效或已过期时抛出
        """
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
        """
        执行密码重置：更新密码、标记验证码已用、写入重置日志。

        返回:
            None
        """
        record = self.validated_data['record']
        user = User.objects.get(email=self.validated_data['email'])
        user.set_password(self.validated_data['new_password'])
        user.save()
        record.is_used = True
        record.save(update_fields=['is_used'])
        UserPasswordResetLog.objects.create(user=user)


class EmailChangeRequestSerializer(serializers.Serializer):
    """
    申请更换绑定邮箱序列化器（第一步：向新邮箱发验证码）。

    权限：user / admin（需已登录，由视图传入当前用户）。
    """

    new_email = serializers.EmailField()

    def validate_new_email(self, value):
        """
        校验新邮箱未被其他账号占用。

        参数:
            value (str): 用户填写的新邮箱
        返回:
            str: 校验通过的新邮箱
        异常:
            ValidationError: 邮箱已被使用时抛出
        """
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('Email already in use')
        return value

    def save(self, user):
        """
        向新邮箱发送更换绑定验证码。

        参数:
            user (User): 当前登录用户（本步仅发码，尚未改库）
        返回:
            None
        """
        create_verification_code(self.validated_data['new_email'], 'change_email')


class EmailChangeConfirmSerializer(serializers.Serializer):
    """
    确认更换绑定邮箱序列化器（第二步：验证码确认后更新邮箱）。

    权限：user / admin（需已登录）。
    校验通过后更新 User.email，标记验证码已用，并写入变更日志。
    """

    new_email = serializers.EmailField()
    code = serializers.CharField(max_length=10)

    def validate(self, attrs):
        """
        校验换绑验证码是否有效。

        参数:
            attrs (dict): 包含 new_email、code 的字段字典
        返回:
            dict: 附加 record 后的 attrs
        异常:
            ValidationError: 验证码无效或已过期时抛出
        """
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
        """
        执行邮箱更换并记录变更历史。

        参数:
            user (User): 当前登录用户
        返回:
            None
        """
        record = self.validated_data['record']
        old_email = user.email
        new_email = self.validated_data['new_email']
        user.email = new_email
        user.save(update_fields=['email'])
        record.is_used = True
        record.save(update_fields=['is_used'])
        UserEmailChangeLog.objects.create(user=user, old_email=old_email, new_email=new_email)
