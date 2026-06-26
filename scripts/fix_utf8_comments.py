# -*- coding: utf-8 -*-
"""Rewrite annotated backend files with guaranteed UTF-8."""
from pathlib import Path

BACKEND = Path(__file__).resolve().parent.parent / "backend"

FILES = {}

FILES["system/models.py"] = '''\
"""
\u6a21\u5757\u8bf4\u660e\uff1a\u540e\u53f0\u6cbb\u7406 ORM \u6570\u636e\u6a21\u578b\u3002

\u5305\u542b\uff1a\u64cd\u4f5c\u5ba1\u8ba1\u65e5\u5fd7\u3001\u5185\u5bb9\u5ba1\u6838\u5904\u7f6e\u3001\u5e73\u53f0\u952e\u503c\u914d\u7f6e\u3001AI \u8c03\u7528\u7559\u75d5\u56db\u5f20\u8868\u3002
\u3010\u6743\u9650\u3011visitor/user \u4e0d\u76f4\u63a5\u8bfb\u5199\uff1badmin \u901a\u8fc7\u540e\u53f0 API \u95f4\u63a5\u64cd\u4f5c\u3002
"""

from django.contrib.auth.models import User
from django.db import models


class OperationLog(models.Model):
    """
    \u529f\u80fd\uff1a\u8bb0\u5f55\u7ba1\u7406\u5458\u5728\u540e\u53f0\u6267\u884c\u7684\u5173\u952e\u64cd\u4f5c\uff0c\u7528\u4e8e\u5ba1\u8ba1\u8ffd\u6eaf\u3002
    \u3010\u6743\u9650\u3011visitor\uff1a\u4e0d\u53ef\u8bbf\u95ee\uff1buser\uff1a\u4e0d\u53ef\u8bbf\u95ee\uff1badmin\uff1a\u53ef\u67e5\u8be2\uff08\u53ea\u8bfb\u63a5\u53e3\uff09\u3002
    """

    # \u5b57\u6bb5\u8bf4\u660e\uff1a\u6267\u884c\u64cd\u4f5c\u7684\u7ba1\u7406\u5458\u8d26\u53f7
    operator = models.ForeignKey(User, on_delete=models.RESTRICT, related_name='operation_logs')
    # \u5b57\u6bb5\u8bf4\u660e\uff1a\u4e1a\u52a1\u6a21\u5757\u540d
    module = models.CharField(max_length=50)
    # \u5b57\u6bb5\u8bf4\u660e\uff1a\u5177\u4f53\u64cd\u4f5c
    action = models.CharField(max_length=50)
    # \u5b57\u6bb5\u8bf4\u660e\uff1a\u88ab\u64cd\u4f5c\u5bf9\u8c61\u7c7b\u578b
    target_type = models.CharField(max_length=50, blank=True, null=True)
    # \u5b57\u6bb5\u8bf4\u660e\uff1a\u88ab\u64cd\u4f5c\u5bf9\u8c61\u4e3b\u952e ID
    target_id = models.BigIntegerField(blank=True, null=True)
    # \u5b57\u6bb5\u8bf4\u660e\uff1a\u64cd\u4f5c\u8be6\u60c5
    content = models.TextField()
    # \u5b57\u6bb5\u8bf4\u660e\uff1a\u5ba2\u6237\u7aef IP
    ip_address = models.CharField(max_length=45, blank=True, null=True)
    # \u5b57\u6bb5\u8bf4\u660e\uff1a\u521b\u5efa\u65f6\u95f4
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'operation_log'
        ordering = ['-created_at']


class ContentModeration(models.Model):
    """
    \u529f\u80fd\uff1a\u5185\u5bb9\u5ba1\u6838\u5904\u7f6e\u8bb0\u5f55\u3002
    \u3010\u6743\u9650\u3011visitor/user\uff1a\u4e0d\u53ef\u8bbf\u95ee\uff1badmin\uff1a\u53ef\u521b\u5efa\u4e0e\u67e5\u8be2\u3002
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
    \u529f\u80fd\uff1a\u5e73\u53f0\u952e\u503c\u914d\u7f6e\uff08\u5982 ai_daily_limit\u3001ai_total_limit\uff09\u3002
    \u3010\u6743\u9650\u3011visitor/user\uff1a\u4e0d\u53ef\u8bbf\u95ee\uff1badmin\uff1a\u53ef\u589e\u5220\u6539\u67e5\u3002
    """

    config_key = models.CharField(max_length=100, unique=True)
    config_value = models.TextField()
    description = models.CharField(max_length=200, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'platform_config'


class AiInvocationLog(models.Model):
    """
    \u529f\u80fd\uff1aAI \u8c03\u7528\u65e5\u5fd7\u3002
    \u3010\u6743\u9650\u3011visitor\uff1a\u4e0d\u53ef\u8c03\u7528\uff1buser\uff1a\u8c03\u7528\u65f6\u5199\u5165\uff1badmin\uff1a\u53ef\u67e5\u8be2\u5168\u90e8\u3002
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
'''

for rel, content in FILES.items():
    path = BACKEND / rel
    path.write_text(content, encoding="utf-8")
    print("wrote", rel)

# seed headers
for rel, desc in [
    ("system/management/commands/seed_demo.py", "\u6f14\u793a\u6570\u636e\u79cd\u5b50\u811a\u672c\uff08\u7b54\u8fa9\u4e0d\u91cd\u70b9\u8bb2\u89e3\uff09\u3002"),
    ("system/management/commands/seed_test_data.py", "\u6d4b\u8bd5\u6570\u636e\u79cd\u5b50\u811a\u672c\uff08\u7b54\u8fa9\u4e0d\u91cd\u70b9\u8bb2\u89e3\uff09\u3002"),
]:
    p = BACKEND / rel
    body = p.read_bytes()
    try:
        text = body.decode("utf-8")
    except UnicodeDecodeError:
        text = body.decode("utf-8", errors="replace")
    if text.startswith('"""'):
        end = text.index('"""', 3) + 3
        text = text[end:].lstrip("\n")
    header = '"""\n\u6a21\u5757\u8bf4\u660e\uff1a' + desc + '\n"""\n\n'
    p.write_text(header + text, encoding="utf-8")
    print("seed", rel)
