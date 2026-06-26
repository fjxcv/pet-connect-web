# -*- coding: utf-8 -*-
from pathlib import Path

BACKEND = Path(__file__).resolve().parent.parent / "backend"


def patch(rel, pairs):
    path = BACKEND / rel
    text = path.read_text(encoding="utf-8")
    for old, new in pairs:
        if old not in text:
            raise KeyError(f"missing in {rel}: {old[:80]!r}")
        text = text.replace(old, new, 1)
    path.write_text(text, encoding="utf-8")
    print("patched", rel)


patch("system/moderation_apply.py", [
    ("from cms.models import CmsArticle",
     '"""\n\u5185\u5bb9\u5904\u7f6e\u8054\u52a8\u4e1a\u52a1\u8868\u3002\u3010\u6743\u9650\u3011\u4ec5 admin \u8c03\u7528\u3002\n"""\n\nfrom cms.models import CmsArticle'),
    ('    """Apply hide/delete/ban to the underlying record."""',
     '    """\u540c\u6b65\u5ba1\u6838\u52a8\u4f5c\u5230\u4e1a\u52a1\u8868\u3002\u3010\u6743\u9650\u3011admin"""'),
    ("    if action == 'approve':",
     "    # \u5206\u652f\uff1a\u901a\u8fc7\u4e0d\u6539\u4e1a\u52a1\u8868\n    if action == 'approve':"),
    ("    if content_type == 'user':\n        if action != 'ban':",
     "    # \u5206\u652f\uff1a\u5c01\u7981\u7528\u6237\n    if content_type == 'user':\n        if action != 'ban':"),
    ("    if content_type == 'community_post':",
     "    # \u5206\u652f\uff1a\u793e\u533a\u5e16\u5b50 hide/delete \u6807\u8bb0\u5220\u9664\n    if content_type == 'community_post':"),
    ("    if content_type == 'cms_article':",
     "    # \u5206\u652f\uff1aCMS \u6587\u7ae0 hide/delete \u6539 status=2\n    if content_type == 'cms_article':"),
    ("    if content_type == 'lost_found_post':",
     "    # \u5206\u652f\uff1a\u5931\u9886\u5e16 hide/delete \u6539 cancelled\n    if content_type == 'lost_found_post':"),
])

patch("system/urls.py", [
    ("from django.urls import path",
     '"""\nsystem \u8def\u7531\uff1a\u540e\u53f0\u4e0e AI\u3002\n"""\n\nfrom django.urls import path'),
    ("admin_router.register(r'admin/users', AdminUserViewSet, basename='admin-users')",
     "# \u3010\u6743\u9650\u3011admin\nadmin_router.register(r'admin/users', AdminUserViewSet, basename='admin-users')"),
    ("    path('ai/breed-detect/', AiBreedDetectView.as_view()),",
     "    # \u3010\u6743\u9650\u3011user/admin\n    path('ai/breed-detect/', AiBreedDetectView.as_view()),"),
])

patch("common/permissions.py", [
    ("from rest_framework.permissions import BasePermission",
     '"""\nDRF \u6743\u9650\u7c7b visitor/user/admin\u3002\n"""\n\nfrom rest_framework.permissions import BasePermission'),
    ("def user_is_admin(user):\n    if not user",
     'def user_is_admin(user):\n    """\u5224\u5b9a admin\u3002\u3010\u6743\u9650\u3011visitor=False"""\n    if not user'),
    ("class IsAdminRole(BasePermission):\n    def has_permission(self, request, view):",
     'class IsAdminRole(BasePermission):\n    """\u3010\u6743\u9650\u3011\u4ec5 admin"""\n    def has_permission(self, request, view):'),
    ("class IsActiveUser(BasePermission):\n    message = 'account_banned'",
     'class IsActiveUser(BasePermission):\n    """\u3010\u6743\u9650\u3011\u5c01\u7981\u7528\u6237\u62e6\u622a"""\n    message = \'account_banned\''),
])

patch("common/ai_quota.py", [
    ("from django.utils import timezone",
     '"""\nAI \u914d\u989d\u68c0\u67e5\u3002\n"""\n\nfrom django.utils import timezone'),
    ("class AiQuotaExceededError(Exception):\n    def __init__(self, message, quota_type='daily'):",
     'class AiQuotaExceededError(Exception):\n    """\u8d85\u914d\u989d\u5f02\u5e38"""\n    def __init__(self, message, quota_type=\'daily\'):'),
    ("def check_ai_quota(user):\n    \"\"\"Raise AiQuotaExceededError if platform AI quota is exceeded.\"\"\"\n    stats = get_ai_usage_stats()",
     'def check_ai_quota(user):\n    """\u68c0\u67e5\u914d\u989d\u3002\u3010\u6743\u9650\u3011user/admin"""\n    stats = get_ai_usage_stats()'),
    ("    if daily_limit > 0 and stats['today_count'] >= daily_limit:",
     "    # \u5206\u652f\uff1a\u4eca\u65e5\u8d85\u9650\n    if daily_limit > 0 and stats['today_count'] >= daily_limit:"),
])

patch("common/utils.py", [
    ("def write_operation_log(operator, module, action, content, target_type=None, target_id=None, ip_address=None):",
     '"""\n\u5ba1\u8ba1\u65e5\u5fd7\u4e0e IP \u5de5\u5177\u3002\n"""\n\n\ndef write_operation_log(operator, module, action, content, target_type=None, target_id=None, ip_address=None):'),
    ("def get_client_ip(request):\n    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')",
     'def get_client_ip(request):\n    """\u63d0\u53d6\u5ba2\u6237\u7aef IP"""\n    x_forwarded_for = request.META.get(\'HTTP_X_FORWARDED_FOR\')'),
])

patch("common/llm_client.py", [
    ("import base64",
     '"""\nLLM \u5c01\u88c5\u3002\n"""\n\nimport base64'),
    ("def chat(messages, max_tokens=1024):\n    return _chat_completion(messages, max_tokens=max_tokens)",
     'def chat(messages, max_tokens=1024):\n    """\u5bf9\u8bdd\u5165\u53e3\u3002\u3010\u6743\u9650\u3011user/admin"""\n    return _chat_completion(messages, max_tokens=max_tokens)'),
])

patch("common/breed_detect.py", [
    ("from common.breed_classifier import BreedModelNotReadyError, is_model_ready, model_paths, predict_breeds",
     '"""\n\u54c1\u79cd\u8bc6\u522b\u7f16\u6392\u3002\n"""\n\nfrom common.breed_classifier import BreedModelNotReadyError, is_model_ready, model_paths, predict_breeds'),
    ("def detect_pet_breed(*, image_url: str = '', image_base64: str = '', description: str = '', request=None) -> dict:\n    if not is_model_ready():",
     'def detect_pet_breed(*, image_url: str = \'\', image_base64: str = \'\', description: str = \'\', request=None) -> dict:\n    """\u54c1\u79cd\u8bc6\u522b\u4e3b\u6d41\u7a0b\u3002\u3010\u6743\u9650\u3011user/admin"""\n    if not is_model_ready():'),
])

patch("common/breed_classifier.py", [
    ("ML_DIR = Path(__file__).resolve().parent.parent / 'ml'",
     '"""\nMobileNetV3 \u63a8\u7406\u3002\n"""\n\nML_DIR = Path(__file__).resolve().parent.parent / \'ml\''),
    ("def predict_breeds(image_bytes: bytes, top_k: int = 4) -> list[dict]:",
     'def predict_breeds(image_bytes: bytes, top_k: int = 4) -> list[dict]:\n    """CNN \u63a8\u7406 Top-K"""'),
])

patch("common/image_loader.py", [
    ("import base64",
     '"""\nAI \u56fe\u7247\u52a0\u8f7d\u3002\n"""\n\nimport base64'),
    ("def load_image_for_ai(*, image_url: str = '', image_base64: str = '', request=None) -> dict:\n    if image_base64:",
     'def load_image_for_ai(*, image_url: str = \'\', image_base64: str = \'\', request=None) -> dict:\n    """\u56fe\u7247\u52a0\u8f7d\u5165\u53e3\u3002\u3010\u6743\u9650\u3011user/admin"""\n    if image_base64:'),
])

patch("pets/serializers.py", [
    ("from django.utils import timezone",
     '"""\npets \u5e8f\u5217\u5316\u5668\u3002\n"""\n\nfrom django.utils import timezone'),
    ("class PetProfileSerializer(serializers.ModelSerializer):\n    rescue_case_address",
     'class PetProfileSerializer(serializers.ModelSerializer):\n    """\u5ba0\u7269\u6863\u6848\u3002\u3010\u6743\u9650\u3011visitor/user \u8bfb\u516c\u5f00\uff1badmin \u5199"""\n    rescue_case_address'),
    ("class AdoptApplicationSerializer(serializers.ModelSerializer):\n    applicant",
     'class AdoptApplicationSerializer(serializers.ModelSerializer):\n    """\u9886\u517b\u7533\u8bf7\u3002\u3010\u6743\u9650\u3011user"""\n    applicant'),
    ("    def validate(self, attrs):\n        required_fields = ['country', 'province', 'city', 'location_text']",
     '    def validate(self, attrs):\n        """\u6821\u9a8c\u5730\u5740\u5fc5\u586b\u3002\u3010\u6743\u9650\u3011admin"""\n        required_fields = [\'country\', \'province\', \'city\', \'location_text\']'),
    ("class AdoptQuestionnaireSerializer(serializers.ModelSerializer):\n    class Meta:",
     'class AdoptQuestionnaireSerializer(serializers.ModelSerializer):\n    """\u9886\u517b\u95ee\u5377\u3002\u3010\u6743\u9650\u3011user"""\n    class Meta:'),
    ("class AdoptAttachmentSerializer(serializers.ModelSerializer):\n    class Meta:",
     'class AdoptAttachmentSerializer(serializers.ModelSerializer):\n    """\u9886\u517b\u9644\u4ef6\u3002\u3010\u6743\u9650\u3011user"""\n    class Meta:'),
    ("class AdoptOfflineVerifySerializer(serializers.ModelSerializer):\n    class Meta:",
     'class AdoptOfflineVerifySerializer(serializers.ModelSerializer):\n    """\u7ebf\u4e0b\u9a8c\u8bc1\u3002\u3010\u6743\u9650\u3011admin"""\n    class Meta:'),
    ("class AdminAdoptApplicationListSerializer(serializers.ModelSerializer):\n    applicant",
     'class AdminAdoptApplicationListSerializer(serializers.ModelSerializer):\n    """\u540e\u53f0\u9886\u517b\u5217\u8868\u3002\u3010\u6743\u9650\u3011admin"""\n    applicant'),
    ("class AdoptApplicationAuditSerializer(serializers.ModelSerializer):\n    class Meta:",
     'class AdoptApplicationAuditSerializer(serializers.ModelSerializer):\n    """\u9886\u517b\u5ba1\u6838\u3002\u3010\u6743\u9650\u3011admin"""\n    class Meta:'),
    ("    def validate(self, attrs):\n        online_status = attrs.get('online_status')",
     '    def validate(self, attrs):\n        """\u62d2\u7edd\u987b\u586b\u539f\u56e0\u3002\u3010\u6743\u9650\u3011admin"""\n        online_status = attrs.get(\'online_status\')'),
    ("class AdoptApplicationReviewDetailSerializer(serializers.ModelSerializer):\n    applicant",
     'class AdoptApplicationReviewDetailSerializer(serializers.ModelSerializer):\n    """\u9886\u517b\u5ba1\u6838\u8be6\u60c5\u3002\u3010\u6743\u9650\u3011admin"""\n    applicant'),
    ("    def get_applicant_phone_masked(self, obj):\n        phone = getattr",
     '    def get_applicant_phone_masked(self, obj):\n        """\u624b\u673a\u53f7\u8131\u654f\u3002\u3010\u6743\u9650\u3011admin"""\n        phone = getattr'),
    ("class PetProfileUpdateSerializer(PetProfileSerializer):\n    def validate(self, attrs):",
     'class PetProfileUpdateSerializer(PetProfileSerializer):\n    """\u5ba0\u7269\u66f4\u65b0\u3002\u3010\u6743\u9650\u3011admin"""\n    def validate(self, attrs):'),
    ("    def validate(self, attrs):\n        pet = attrs.get('pet')",
     '    def validate(self, attrs):\n        """\u521b\u5efa\u524d\u6821\u9a8c\u5ba0\u7269\u72b6\u6001\u3002\u3010\u6743\u9650\u3011user"""\n        pet = attrs.get(\'pet\')'),
])

print("done")
