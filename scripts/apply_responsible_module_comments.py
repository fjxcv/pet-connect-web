# -*- coding: utf-8 -*-
from __future__ import annotations
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BACKEND = ROOT / "backend"
FILES: dict[str, str] = {}


def write_all():
    for rel, content in FILES.items():
        path = BACKEND / rel.replace("backend/", "")
        path.write_text(content, encoding="utf-8")
        print("Wrote", rel)


FILES["backend/system/models.py"] = (
    '"""\n'
    + "\u6a21\u5757\u8bf4\u660e\uff1a\u540e\u53f0\u6cbb\u7406 ORM \u6570\u636e\u6a21\u578b\u3002\n\n"
    + "\u5305\u542b\uff1a\u64cd\u4f5c\u5ba1\u8ba1\u65e5\u5fd7\u3001\u5185\u5bb9\u5ba1\u6838\u5904\u7f6e\u3001\u5e73\u53f0\u952e\u503c\u914d\u7f6e\u3001AI \u8c03\u7528\u7559\u75d5\u56db\u5f20\u8868\u3002\n"
    + "\u3010\u6743\u9650\u3011visitor/user \u4e0d\u76f4\u63a5\u8bfb\u5199\uff1badmin \u901a\u8fc7\u540e\u53f0 API \u95f4\u63a5\u64cd\u4f5c\u3002\n"
    + '"""\n\n'
    + "from django.contrib.auth.models import User\n"
    + "from django.db import models\n\n\n"
    + "class OperationLog(models.Model):\n"
    + '    """\n'
    + "\u529f\u80fd\uff1a\u8bb0\u5f55\u7ba1\u7406\u5458\u5728\u540e\u53f0\u6267\u884c\u7684\u5173\u952e\u64cd\u4f5c\uff0c\u7528\u4e8e\u5ba1\u8ba1\u8ffd\u6eaf\u3002\n"
    + "\u3010\u6743\u9650\u3011visitor\uff1a\u4e0d\u53ef\u8bbf\u95ee\uff1buser\uff1a\u4e0d\u53ef\u8bbf\u95ee\uff1badmin\uff1a\u53ef\u67e5\u8be2\uff08\u53ea\u8bfb\u63a5\u53e3\uff09\u3002\n"
    + '    """\n\n'
    + "    # \u5b57\u6bb5\u8bf4\u660e\uff1a\u6267\u884c\u64cd\u4f5c\u7684\u7ba1\u7406\u5458\u8d26\u53f7\n"
    + "    operator = models.ForeignKey(User, on_delete=models.RESTRICT, related_name='operation_logs')\n"
    + "    # \u5b57\u6bb5\u8bf4\u660e\uff1a\u4e1a\u52a1\u6a21\u5757\u540d\uff0c\u5982 admin\u3001moderation\u3001adopt\n"
    + "    module = models.CharField(max_length=50)\n"
    + "    # \u5b57\u6bb5\u8bf4\u660e\uff1a\u5177\u4f53\u64cd\u4f5c\uff0c\u5982 user_update\u3001audit\n"
    + "    action = models.CharField(max_length=50)\n"
    + "    # \u5b57\u6bb5\u8bf4\u660e\uff1a\u88ab\u64cd\u4f5c\u5bf9\u8c61\u7c7b\u578b\n"
    + "    target_type = models.CharField(max_length=50, blank=True, null=True)\n"
    + "    # \u5b57\u6bb5\u8bf4\u660e\uff1a\u88ab\u64cd\u4f5c\u5bf9\u8c61\u4e3b\u952e ID\n"
    + "    target_id = models.BigIntegerField(blank=True, null=True)\n"
    + "    # \u5b57\u6bb5\u8bf4\u660e\uff1a\u64cd\u4f5c\u8be6\u60c5\u6587\u5b57\u63cf\u8ff0\n"
    + "    content = models.TextField()\n"
    + "    # \u5b57\u6bb5\u8bf4\u660e\uff1a\u64cd\u4f5c\u8005\u5ba2\u6237\u7aef IP\n"
    + "    ip_address = models.CharField(max_length=45, blank=True, null=True)\n"
    + "    # \u5b57\u6bb5\u8bf4\u660e\uff1a\u8bb0\u5f55\u521b\u5efa\u65f6\u95f4\n"
    + "    created_at = models.DateTimeField(auto_now_add=True)\n\n"
    + "    class Meta:\n"
    + "        db_table = 'operation_log'\n"
    + "        ordering = ['-created_at']\n\n\n"
    + "class ContentModeration(models.Model):\n"
    + '    """\n'
    + "\u529f\u80fd\uff1a\u5185\u5bb9\u5ba1\u6838\u5904\u7f6e\u8bb0\u5f55\u3002\n"
    + "\u3010\u6743\u9650\u3011visitor\uff1a\u4e0d\u53ef\u8bbf\u95ee\uff1buser\uff1a\u4e0d\u53ef\u8bbf\u95ee\uff1badmin\uff1a\u53ef\u521b\u5efa\u4e0e\u67e5\u8be2\u3002\n"
    + '    """\n\n'
    + "    ACTION_CHOICES = [\n"
    + "        ('approve', 'Approve'),\n"
    + "        ('hide', 'Hide'),\n"
    + "        ('delete', 'Delete'),\n"
    + "        ('ban', 'Ban'),\n"
    + "    ]\n"
    + "    # \u5b57\u6bb5\u8bf4\u660e\uff1a\u88ab\u5ba1\u6838\u5185\u5bb9\u7c7b\u578b\n"
    + "    content_type = models.CharField(max_length=30)\n"
    + "    content_id = models.BigIntegerField()\n"
    + "    action = models.CharField(max_length=20, choices=ACTION_CHOICES)\n"
    + "    reason = models.TextField(blank=True, null=True)\n"
    + "    target_summary = models.CharField(max_length=200, blank=True, null=True)\n"
    + "    operator = models.ForeignKey(User, on_delete=models.RESTRICT, related_name='moderation_actions')\n"
    + "    created_at = models.DateTimeField(auto_now_add=True)\n\n"
    + "    class Meta:\n"
    + "        db_table = 'content_moderation'\n"
    + "        ordering = ['-created_at']\n\n\n"
    + "class PlatformConfig(models.Model):\n"
    + '    """\n'
    + "\u529f\u80fd\uff1a\u5e73\u53f0\u952e\u503c\u914d\u7f6e\uff08\u5982 ai_daily_limit\u3001ai_total_limit\uff09\u3002\n"
    + "\u3010\u6743\u9650\u3011visitor/user\uff1a\u4e0d\u53ef\u8bbf\u95ee\uff1badmin\uff1a\u53ef\u589e\u5220\u6539\u67e5\u3002\n"
    + '    """\n\n'
    + "    config_key = models.CharField(max_length=100, unique=True)\n"
    + "    config_value = models.TextField()\n"
    + "    description = models.CharField(max_length=200, blank=True, null=True)\n"
    + "    updated_at = models.DateTimeField(auto_now=True)\n\n"
    + "    class Meta:\n"
    + "        db_table = 'platform_config'\n\n\n"
    + "class AiInvocationLog(models.Model):\n"
    + '    """\n'
    + "\u529f\u80fd\uff1aAI \u529f\u80fd\u8c03\u7528\u65e5\u5fd7\u3002\n"
    + "\u3010\u6743\u9650\u3011visitor\uff1a\u4e0d\u53ef\u8c03\u7528 AI\uff1buser\uff1a\u8c03\u7528\u65f6\u81ea\u52a8\u5199\u5165\uff1badmin\uff1a\u53ef\u67e5\u8be2\u5168\u90e8\u65e5\u5fd7\u3002\n"
    + '    """\n\n'
    + "    FEATURE_CHOICES = [\n"
    + "        ('breed_detect', 'Breed Detect'),\n"
    + "        ('adopt_copy', 'Adopt Copy'),\n"
    + "        ('qa_assistant', 'QA Assistant'),\n"
    + "    ]\n"
    + "    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ai_invocations')\n"
    + "    feature_type = models.CharField(max_length=30, choices=FEATURE_CHOICES)\n"
    + "    request_meta = models.TextField(blank=True, null=True)\n"
    + "    result_meta = models.TextField(blank=True, null=True)\n"
    + "    success = models.BooleanField(default=False)\n"
    + "    created_at = models.DateTimeField(auto_now_add=True)\n\n"
    + "    class Meta:\n"
    + "        db_table = 'ai_invocation_log'\n"
    + "        ordering = ['-created_at']\n"
)

if __name__ == "__main__":
    write_all()
