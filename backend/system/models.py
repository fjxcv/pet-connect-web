"""
模块说明：后台治理 ORM 数据模型。

包含：操作审计日志、内容审核处置、平台键值配置、AI 调用留痕四张表。
【权限】visitor/user 不直接读写；admin 通过后台 API 间接操作。
"""

from django.contrib.auth.models import User
from django.db import models


class OperationLog(models.Model):
    """
    功能：记录管理员在后台执行的关键操作，用于审计追溯。
    【权限】visitor：不可访问；user：不可访问；admin：可查询（只读接口）。
    """

    # 字段说明：执行操作的管理员账号
    operator = models.ForeignKey(User, on_delete=models.RESTRICT, related_name='operation_logs')
    # 字段说明：业务模块名
    module = models.CharField(max_length=50)
    # 字段说明：具体操作
    action = models.CharField(max_length=50)
    # 字段说明：被操作对象类型
    target_type = models.CharField(max_length=50, blank=True, null=True)
    # 字段说明：被操作对象主键 ID
    target_id = models.BigIntegerField(blank=True, null=True)
    # 字段说明：操作详情
    content = models.TextField()
    # 字段说明：客户端 IP
    ip_address = models.CharField(max_length=45, blank=True, null=True)
    # 字段说明：创建时间
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'operation_log'
        ordering = ['-created_at']


class ContentModeration(models.Model):
    """
    功能：内容审核处置记录。
    【权限】visitor/user：不可访问；admin：可创建与查询。
    """

    ACTION_CHOICES = [
        ('approve', 'Approve'),
        ('hide', 'Hide'),
        ('delete', 'Delete'),
        ('ban', 'Ban'),
    ]
    content_type = models.CharField(max_length=30)
    content_id = models.BigIntegerField()
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    reason = models.TextField(blank=True, null=True)
    target_summary = models.CharField(max_length=200, blank=True, null=True)
    operator = models.ForeignKey(User, on_delete=models.RESTRICT, related_name='moderation_actions')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'content_moderation'
        ordering = ['-created_at']


class PlatformConfig(models.Model):
    """
    功能：平台键值配置（如 ai_daily_limit、ai_total_limit）。
    【权限】visitor/user：不可访问；admin：可增删改查。
    """

    config_key = models.CharField(max_length=100, unique=True)
    config_value = models.TextField()
    description = models.CharField(max_length=200, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'platform_config'


class AiInvocationLog(models.Model):
    """
    功能：AI 调用日志。
    【权限】visitor：不可调用；user：调用时写入；admin：可查询全部。
    """

    FEATURE_CHOICES = [
        ('breed_detect', 'Breed Detect'),
        ('adopt_copy', 'Adopt Copy'),
        ('qa_assistant', 'QA Assistant'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ai_invocations')
    feature_type = models.CharField(max_length=30, choices=FEATURE_CHOICES)
    request_meta = models.TextField(blank=True, null=True)
    result_meta = models.TextField(blank=True, null=True)
    success = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'ai_invocation_log'
        ordering = ['-created_at']
