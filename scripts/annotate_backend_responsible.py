# -*- coding: utf-8 -*-
"""Apply Chinese comments to restored backend files (ASCII source only)."""
from pathlib import Path

BACKEND = Path(__file__).resolve().parent.parent / "backend"


def patch(rel, pairs):
    path = BACKEND / rel
    text = path.read_text(encoding="utf-8")
    for old, new in pairs:
        if old not in text:
            raise KeyError(f"missing in {rel}: {old[:60]!r}")
        text = text.replace(old, new, 1)
    path.write_text(text, encoding="utf-8")
    print("patched", rel)


patch("system/serializers.py", [
    (
        "from rest_framework import serializers",
        '"""\n\u6a21\u5757\u8bf4\u660e\uff1asystem \u6a21\u5757\u5e8f\u5217\u5316\u5668\u3002\n"""\n\nfrom rest_framework import serializers',
    ),
    (
        "class OperationLogSerializer(serializers.ModelSerializer):\n    operator",
        'class OperationLogSerializer(serializers.ModelSerializer):\n    """\u529f\u80fd\uff1a\u64cd\u4f5c\u5ba1\u8ba1\u65e5\u5fd7\u3002\u3010\u6743\u9650\u3011\u4ec5 admin \u53ef\u67e5\u8be2\u3002"""\n    operator',
    ),
    (
        "class ContentModerationSerializer(serializers.ModelSerializer):\n    operator",
        'class ContentModerationSerializer(serializers.ModelSerializer):\n    """\u529f\u80fd\uff1a\u5185\u5bb9\u5ba1\u6838\u3002\u3010\u6743\u9650\u3011\u4ec5 admin \u53ef\u63d0\u4ea4\u3002"""\n    operator',
    ),
    (
        "    def validate(self, attrs):\n        action = attrs.get('action')",
        '    def validate(self, attrs):\n        """\u529f\u80fd\uff1a\u6821\u9a8c\u5ba1\u6838\u52a8\u4f5c\u4e0e\u539f\u56e0\u3002\u3010\u6743\u9650\u3011\u4ec5 admin\u3002"""\n        action = attrs.get(\'action\')',
    ),
    (
        "        if action in ('hide', 'delete', 'ban') and not reason:",
        "        # \u5206\u652f\uff1a\u9690\u85cf/\u5220\u9664/\u5c01\u7981\u5fc5\u987b\u586b\u539f\u56e0\n        if action in ('hide', 'delete', 'ban') and not reason:",
    ),
    (
        "        if action == 'ban' and attrs.get('content_type') != 'user':",
        "        # \u5206\u652f\uff1a\u5c01\u7981\u53ea\u80fd\u9488\u5bf9\u7528\u6237\n        if action == 'ban' and attrs.get('content_type') != 'user':",
    ),
    (
        "class PlatformConfigSerializer(serializers.ModelSerializer):\n    class Meta:",
        'class PlatformConfigSerializer(serializers.ModelSerializer):\n    """\u529f\u80fd\uff1a\u5e73\u53f0\u914d\u7f6e\u3002\u3010\u6743\u9650\u3011\u4ec5 admin\u3002"""\n    class Meta:',
    ),
    (
        "class AiInvocationLogSerializer(serializers.ModelSerializer):\n    user",
        'class AiInvocationLogSerializer(serializers.ModelSerializer):\n    """\u529f\u80fd\uff1aAI \u8c03\u7528\u65e5\u5fd7\u3002\u3010\u6743\u9650\u3011admin \u53ef\u67e5\u8be2\u5168\u90e8\u3002"""\n    user',
    ),
])

patch("system/moderation_apply.py", [
    (
        "from cms.models import CmsArticle",
        '"""\n\u6a21\u5757\u8bf4\u660e\uff1a\u5185\u5bb9\u5904\u7f6e\u8054\u52a8\u4e1a\u52a1\u8868\u3002\n\u3010\u6743\u9650\u3011\u4ec5 admin \u5ba1\u6838\u63a5\u53e3\u8c03\u7528\u3002\n"""\n\nfrom cms.models import CmsArticle',
    ),
    (
        "def apply_moderation(content_type, content_id, action):\n    if action == 'approve':",
        'def apply_moderation(content_type, content_id, action):\n    """\u529f\u80fd\uff1a\u5c06\u5ba1\u6838\u52a8\u4f5c\u540c\u6b65\u5230\u4e1a\u52a1\u8868\u3002\u3010\u6743\u9650\u3011\u4ec5 admin\u3002"""\n    # \u5206\u652f\uff1a\u901a\u8fc7\u4e0d\u6539\u4e1a\u52a1\u8868\n    if action == \'approve\':',
    ),
    (
        "    if content_type == 'user':\n        if action != 'ban':",
        "    # \u5206\u652f\uff1a\u5c01\u7981\u7528\u6237\n    if content_type == 'user':\n        if action != 'ban':",
    ),
])

patch("system/urls.py", [
    (
        "from django.urls import path",
        '"""\n\u6a21\u5757\u8bf4\u660e\uff1asystem \u8def\u7531\uff08\u540e\u53f0\u4e0e AI\uff09\u3002\n"""\n\nfrom django.urls import path',
    ),
    (
        "admin_router.register(r'admin/users', AdminUserViewSet, basename='admin-users')",
        "# \u3010\u6743\u9650\u3011admin\nadmin_router.register(r'admin/users', AdminUserViewSet, basename='admin-users')",
    ),
    (
        "    path('ai/breed-detect/', AiBreedDetectView.as_view()),",
        "    # \u3010\u6743\u9650\u3011user/admin \u9700\u767b\u5f55\n    path('ai/breed-detect/', AiBreedDetectView.as_view()),",
    ),
])

patch("common/permissions.py", [
    (
        "from rest_framework.permissions import BasePermission",
        '"""\n\u6a21\u5757\u8bf4\u660e\uff1aDRF \u6743\u9650\u7c7b\uff08visitor/user/admin\uff09\u3002\n"""\n\nfrom rest_framework.permissions import BasePermission',
    ),
    (
        "def user_is_admin(user):\n    if not user",
        'def user_is_admin(user):\n    """\u529f\u80fd\uff1a\u5224\u5b9a\u662f\u5426 admin\u3002\u8fd4\u56de bool\u3002"""\n    # \u3010\u6743\u9650\u3011visitor \u8fd4\u56de False\n    if not user',
    ),
    (
        "class IsAdminRole(BasePermission):\n    def has_permission(self, request, view):",
        'class IsAdminRole(BasePermission):\n    """\u3010\u6743\u9650\u3011\u4ec5 admin \u5141\u8bb8\u3002"""\n    def has_permission(self, request, view):',
    ),
    (
        "class IsActiveUser(BasePermission):\n    message = 'account_banned'",
        'class IsActiveUser(BasePermission):\n    """\u3010\u6743\u9650\u3011\u5c01\u7981\u7528\u6237\u62e6\u622a\u3002"""\n    message = \'account_banned\'',
    ),
])

patch("common/ai_quota.py", [
    (
        "from django.utils import timezone",
        '"""\n\u6a21\u5757\u8bf4\u660e\uff1aAI \u914d\u989d\u68c0\u67e5\u4e0e\u7528\u91cf\u7edf\u8ba1\u3002\n"""\n\nfrom django.utils import timezone',
    ),
    (
        "class AiQuotaExceededError(Exception):\n    def __init__(self, message, quota_type='daily'):",
        'class AiQuotaExceededError(Exception):\n    """AI \u8d85\u914d\u989d\u5f02\u5e38\u3002"""\n    def __init__(self, message, quota_type=\'daily\'):',
    ),
    (
        "def check_ai_quota(user):\n    stats = get_ai_usage_stats()",
        'def check_ai_quota(user):\n    """\u529f\u80fd\uff1a\u68c0\u67e5\u5168\u7ad9 AI \u914d\u989d\u3002\u3010\u6743\u9650\u3011user/admin \u5171\u4eab\u914d\u989d\u3002"""\n    stats = get_ai_usage_stats()',
    ),
    (
        "    if daily_limit > 0 and stats['today_count'] >= daily_limit:",
        "    # \u5206\u652f\uff1a\u4eca\u65e5\u8d85\u9650\n    if daily_limit > 0 and stats['today_count'] >= daily_limit:",
    ),
])

patch("common/utils.py", [
    (
        "def write_operation_log(operator, module, action, content, target_type=None, target_id=None, ip_address=None):",
        '"""\n\u6a21\u5757\u8bf4\u660e\uff1a\u5ba1\u8ba1\u65e5\u5fd7\u4e0e IP \u5de5\u5177\u3002\n"""\n\n\ndef write_operation_log(operator, module, action, content, target_type=None, target_id=None, ip_address=None):',
    ),
    (
        "def get_client_ip(request):\n    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')",
        'def get_client_ip(request):\n    """\u529f\u80fd\uff1a\u63d0\u53d6\u5ba2\u6237\u7aef IP\u3002"""\n    x_forwarded_for = request.META.get(\'HTTP_X_FORWARDED_FOR\')',
    ),
])

patch("common/llm_client.py", [
    (
        "import base64",
        '"""
\u6a21\u5757\u8bf4\u660e\uff1aLLM \u5c01\u88c5\uff08\u661f\u706b/OpenAI\uff09\u3002\n"""
\nimport base64',
    ),
    (
        "def chat(messages, max_tokens=1024):\n    return _chat_completion(messages, max_tokens=max_tokens)",
        'def chat(messages, max_tokens=1024):\n    """\u5bf9\u5916\u6587\u672c\u5bf9\u8bdd\u5165\u53e3\u3002\u3010\u6743\u9650\u3011user/admin\u3002"""\n    return _chat_completion(messages, max_tokens=max_tokens)',
    ),
])

patch("common/breed_detect.py", [
    (
        "from common.breed_classifier import BreedModelNotReadyError, is_model_ready, model_paths, predict_breeds",
        '"""\n\u6a21\u5757\u8bf4\u660e\uff1a\u54c1\u79cd\u8bc6\u522b\u4e1a\u52a1\u7f16\u6392\u3002\n"""\n\nfrom common.breed_classifier import BreedModelNotReadyError, is_model_ready, model_paths, predict_breeds',
    ),
    (
        "def detect_pet_breed(*, image_url: str = '', image_base64: str = '', description: str = '', request=None) -> dict:\n    if not is_model_ready():",
        'def detect_pet_breed(*, image_url: str = \'\', image_base64: str = \'\', description: str = \'\', request=None) -> dict:\n    """\u54c1\u79cd\u8bc6\u522b\u4e3b\u6d41\u7a0b\u3002\u3010\u6743\u9650\u3011user/admin\u3002"""\n    if not is_model_ready():',
    ),
])

patch("common/breed_classifier.py", [
    (
        "ML_DIR = Path(__file__).resolve().parent.parent / 'ml'",
        '"""\n\u6a21\u5757\u8bf4\u660e\uff1aMobileNetV3 \u672c\u5730\u63a8\u7406\u3002\n"""\n\nML_DIR = Path(__file__).resolve().parent.parent / \'ml\'',
    ),
    (
        "def predict_breeds(image_bytes: bytes, top_k: int = 4) -> list[dict]:",
        'def predict_breeds(image_bytes: bytes, top_k: int = 4) -> list[dict]:\n    """\u672c\u5730 CNN \u63a8\u7406 Top-K \u54c1\u79cd\u3002"""',
    ),
])

patch("common/image_loader.py", [
    (
        "import base64",
        '"""\n\u6a21\u5757\u8bf4\u660e\uff1aAI \u56fe\u7247\u52a0\u8f7d\u3002\n"""\n\nimport base64',
    ),
    (
        "def load_image_for_ai(*, image_url: str = '', image_base64: str = '', request=None) -> dict:\n    if image_base64:",
        'def load_image_for_ai(*, image_url: str = \'\', image_base64: str = \'\', request=None) -> dict:\n    """\u56fe\u7247\u52a0\u8f7d\u7edf\u4e00\u5165\u53e3\u3002\u3010\u6743\u9650\u3011user/admin\u3002"""\n    if image_base64:',
    ),
])

patch("pets/serializers.py", [
    (
        "from django.utils import timezone",
        '"""\n\u6a21\u5757\u8bf4\u660e\uff1apets \u5e8f\u5217\u5316\u5668\u3002\n"""\n\nfrom django.utils import timezone',
    ),
    (
        "class PetProfileSerializer(serializers.ModelSerializer):\n    rescue_case_address",
        'class PetProfileSerializer(serializers.ModelSerializer):\n    """\u5ba0\u7269\u6863\u6848\u3002\u3010\u6743\u9650\u3011visitor/user \u53ef\u8bfb\u516c\u5f00\u6863\u6848\uff1badmin \u53ef\u5199\u3002"""\n    rescue_case_address',
    ),
    (
        "class AdoptApplicationSerializer(serializers.ModelSerializer):\n    applicant",
        'class AdoptApplicationSerializer(serializers.ModelSerializer):\n    """\u9886\u517b\u7533\u8bf7\u3002\u3010\u6743\u9650\u3011user \u53ef\u63d0\u4ea4\u3002"""\n    applicant',
    ),
])

print("all done")
