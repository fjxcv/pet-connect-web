"""
模块说明：system 模块序列化器。
"""

from rest_framework import serializers

from accounts.serializers import UserSerializer
from .models import AiInvocationLog, ContentModeration, OperationLog, PlatformConfig


class OperationLogSerializer(serializers.ModelSerializer):
    """操作审计日志。【权限】admin"""
    operator = UserSerializer(read_only=True)

    class Meta:
        model = OperationLog
        fields = '__all__'


class ContentModerationSerializer(serializers.ModelSerializer):
    """内容审核。【权限】admin"""
    operator = UserSerializer(read_only=True)

    class Meta:
        model = ContentModeration
        fields = '__all__'
        read_only_fields = ['operator', 'created_at']

    def validate(self, attrs):
        """校验审核动作与原因。【权限】admin"""
        action = attrs.get('action') or getattr(self.instance, 'action', None)
        reason = (attrs.get('reason') or '').strip()
        # 分支：隐藏/删除/封禁必须填原因
        if action in ('hide', 'delete', 'ban') and not reason:
            raise serializers.ValidationError({'reason': '\u5904\u7f6e\u539f\u56e0\u4e0d\u80fd\u4e3a\u7a7a'})
        # 分支：封禁只能针对 user
        if action == 'ban' and attrs.get('content_type') != 'user':
            raise serializers.ValidationError({'content_type': 'ban action requires content_type=user'})
        return attrs


class PlatformConfigSerializer(serializers.ModelSerializer):
    """平台配置。【权限】admin"""
    class Meta:
        model = PlatformConfig
        fields = '__all__'


class AiInvocationLogSerializer(serializers.ModelSerializer):
    """AI 调用日志。【权限】admin"""
    user = UserSerializer(read_only=True)

    class Meta:
        model = AiInvocationLog
        fields = '__all__'
        read_only_fields = ['user', 'success', 'created_at']
