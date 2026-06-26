# -*- coding: utf-8 -*-
"""Apply Chinese comments to system/views.py only (safe string patches)."""
from pathlib import Path

p = Path(__file__).resolve().parent.parent / "backend" / "system" / "views.py"
t = p.read_text(encoding="utf-8")

header = (
    '"""\n'
    "\u6a21\u5757\u8bf4\u660e\uff1a\u667a\u80fd\u540e\u53f0\u7ba1\u7406\u4e0e AI \u8f85\u52a9 API \u89c6\u56fe\u3002\n\n"
    "\u5305\u542b\uff1a\u8fd0\u8425\u770b\u677f\u3001\u7528\u6237\u7ba1\u7406\u3001\u5185\u5bb9\u5ba1\u6838\u3001\u5e73\u53f0\u914d\u7f6e\u3001\n"
    "AI \u54c1\u79cd\u8bc6\u522b / \u9886\u517b\u6587\u6848 / \u667a\u80fd\u95ee\u7b54\u4e09\u6761\u94fe\u8def\u3001AI \u8c03\u7528\u65e5\u5fd7\u67e5\u8be2\u4e0e\u7528\u91cf\u7edf\u8ba1\u3002\n"
    '"""\n\n'
)
if not t.startswith('"""'):
    t = header + t

patches = [
    (
        "class AdminDashboardView(APIView):\n    permission_classes",
        "class AdminDashboardView(APIView):\n"
        '    """\u8fd0\u8425\u6570\u636e\u770b\u677f\uff1a\u805a\u5408\u5168\u7ad9 KPI\uff0c\u4ec5\u7ba1\u7406\u5458\u53ef\u8bfb\u3002"""\n'
        "    permission_classes",
    ),
    (
        "class AdminUserViewSet(viewsets.GenericViewSet):\n    queryset",
        "class AdminUserViewSet(viewsets.GenericViewSet):\n"
        '    """\u540e\u53f0\u7528\u6237\u7ba1\u7406\uff1a\u5217\u8868\u7b5b\u9009\u3001\u5c01\u7981\u4e0e\u89d2\u8272\u8c03\u6574\u3002"""\n'
        "    queryset",
    ),
    (
        "class AdminModerationViewSet(viewsets.ModelViewSet):\n    queryset",
        "class AdminModerationViewSet(viewsets.ModelViewSet):\n"
        '    """\u5185\u5bb9\u5ba1\u6838\uff1a\u5199\u5165\u5ba1\u6838\u8bb0\u5f55\u5e76\u8054\u52a8\u4e1a\u52a1\u8868\u3002"""\n'
        "    queryset",
    ),
    (
        "class AdminConfigViewSet(viewsets.ModelViewSet):\n    queryset",
        "class AdminConfigViewSet(viewsets.ModelViewSet):\n"
        '    """\u5e73\u53f0\u914d\u7f6e\u7ef4\u62a4\uff08\u542b AI \u914d\u989d\u7b49\uff09\u3002"""\n'
        "    queryset",
    ),
    (
        "class AdminOperationLogViewSet(viewsets.ReadOnlyModelViewSet):\n    queryset",
        "class AdminOperationLogViewSet(viewsets.ReadOnlyModelViewSet):\n"
        '    """\u64cd\u4f5c\u5ba1\u8ba1\u65e5\u5fd7\u53ea\u8bfb\u67e5\u8be2\u3002"""\n'
        "    queryset",
    ),
    (
        "def _ai_error_response(exc):\n    if isinstance",
        "def _ai_error_response(exc):\n"
        '    """\u5c06 LLM \u5f02\u5e38\u6620\u5c04\u4e3a 503\uff08\u672a\u914d\u7f6e\uff09\u6216 502\uff08\u4e0a\u6e38\u5931\u8d25\uff09\u3002"""\n'
        "    if isinstance",
    ),
    (
        "def _ai_quota_response(exc, user, feature_type, request_meta=''):\n    log_quota_exceeded",
        "def _ai_quota_response(exc, user, feature_type, request_meta=''):\n"
        '    """\u914d\u989d\u8d85\u9650\u65f6\u8bb0\u5931\u8d25\u65e5\u5fd7\u5e76\u8fd4\u56de HTTP 429\u3002"""\n'
        "    log_quota_exceeded",
    ),
    (
        "class AiBreedDetectView(APIView):\n    permission_classes",
        "class AiBreedDetectView(APIView):\n"
        '    """AI \u54c1\u79cd\u8bc6\u522b\u63a5\u53e3\u3002"""\n'
        "    permission_classes",
    ),
    (
        "class AiAdoptCopyView(APIView):\n    permission_classes",
        "class AiAdoptCopyView(APIView):\n"
        '    """AI \u9886\u517b\u6587\u6848\uff1a\u6839\u636e\u5ba0\u7269\u5b57\u6bb5\u8c03\u7528 LLM \u751f\u6210 Markdown \u63a8\u4ecb\u6587\u6848\u3002"""\n'
        "    permission_classes",
    ),
    (
        "class AiQaView(APIView):\n    permission_classes",
        "class AiQaView(APIView):\n"
        '    """AI \u667a\u80fd\u517b\u5ba0\u95ee\u7b54\uff1a\u643a\u5e26\u6700\u8fd1\u591a\u8f6e\u4e0a\u4e0b\u6587\u8c03\u7528 LLM\u3002"""\n'
        "    permission_classes",
    ),
    (
        "class AiLogPagination(PageNumberPagination):\n    page_size",
        "class AiLogPagination(PageNumberPagination):\n"
        '    """AI \u8c03\u7528\u65e5\u5fd7\u5206\u9875\uff1a\u9ed8\u8ba4\u6bcf\u9875 20 \u6761\u3002"""\n'
        "    page_size",
    ),
    (
        "class AdminAiLogViewSet(viewsets.ReadOnlyModelViewSet):\n    queryset",
        "class AdminAiLogViewSet(viewsets.ReadOnlyModelViewSet):\n"
        '    """AI \u8c03\u7528\u65e5\u5fd7\u67e5\u8be2\u4e0e\u7528\u91cf\u7edf\u8ba1\u3002"""\n'
        "    queryset",
    ),
    (
        "    def get(self, request):\n        return Response({\n            'users'",
        "    def get(self, request):\n"
        '        """\u8fd4\u56de\u7528\u6237\u3001\u5ba0\u7269\u3001\u7533\u8bf7\u3001\u6551\u52a9\u3001\u793e\u533a\u3001CMS\u3001\u62a5\u5931\u53ca\u9886\u517b\u72b6\u6001\u5206\u5e03\u3002"""\n'
        "        return Response({\n            'users'",
    ),
    (
        "    def list(self, request):\n        users = self.get_queryset()",
        "    def list(self, request):\n"
        '        """\u6309 role/status \u7b5b\u9009\u7528\u6237\u5217\u8868\uff0c\u6700\u591a\u8fd4\u56de 100 \u6761\u3002"""\n'
        "        users = self.get_queryset()",
    ),
    (
        "    def partial_update(self, request, pk=None):\n        user = User.objects",
        "    def partial_update(self, request, pk=None):\n"
        '        """\u66f4\u65b0\u7528\u6237\u5c01\u7981\u72b6\u6001\u6216\u89d2\u8272\uff0c\u5e76\u540c\u6b65 is_staff \u4e0e\u64cd\u4f5c\u65e5\u5fd7\u3002"""\n'
        "        user = User.objects",
    ),
    (
        "    def perform_create(self, serializer):\n        mod = serializer.save",
        "    def perform_create(self, serializer):\n"
        '        """\u5148\u5199\u5165\u5ba1\u6838\u8bb0\u5f55\uff0c\u518d\u8054\u52a8\u4e1a\u52a1\u8868\uff1b\u5931\u8d25\u5219\u56de\u6eda\u5ba1\u6838\u884c\u3002"""\n'
        "        mod = serializer.save",
    ),
    (
        "            mod.delete()\n            from rest_framework.exceptions",
        "            mod.delete()  # \u4e1a\u52a1\u5b9e\u4f53\u4e0d\u5b58\u5728\u6216\u52a8\u4f5c\u975e\u6cd5\u65f6\u56de\u6eda\n"
        "            from rest_framework.exceptions",
    ),
    (
        "    def stats(self, request):\n        return Response(get_ai_usage_stats())",
        "    def stats(self, request):\n"
        '        """\u7ba1\u7406\u5458\u67e5\u8be2 AI \u8c03\u7528\u7528\u91cf\u7edf\u8ba1\u3002"""\n'
        "        return Response(get_ai_usage_stats())",
    ),
]

for old, new in patches:
    if old in t:
        t = t.replace(old, new, 1)

for marker, post_old, post_new in [
    (
        "class AiBreedDetectView",
        "    def post(self, request):\n        try:\n            check_ai_quota",
        "    def post(self, request):\n"
        '        """\u914d\u989d\u68c0\u67e5 \u2192 \u52a0\u8f7d\u56fe\u7247 \u2192 \u672c\u5730 CNN \u63a8\u7406 \u2192 \u5199\u8c03\u7528\u65e5\u5fd7\u3002"""\n'
        "        try:\n            check_ai_quota",
    ),
    (
        "class AiAdoptCopyView",
        "    def post(self, request):\n        meta = str(request.data)",
        "    def post(self, request):\n"
        '        """\u914d\u989d\u68c0\u67e5 \u2192 \u7ec4\u88c5 Prompt \u2192 LLM \u751f\u6210 \u2192 \u5199\u8c03\u7528\u65e5\u5fd7\u3002"""\n'
        "        meta = str(request.data)",
    ),
    (
        "class AiQaView",
        "    def post(self, request):\n        question = request.data.get",
        "    def post(self, request):\n"
        '        """\u914d\u989d\u68c0\u67e5 \u2192 \u622a\u53d6 history[-6] \u2192 LLM \u56de\u7b54 \u2192 \u5199\u8c03\u7528\u65e5\u5fd7\u3002"""\n'
        "        question = request.data.get",
    ),
]:
    idx = t.find(marker)
    if idx >= 0:
        sub = t[idx:]
        if post_old in sub:
            sub = sub.replace(post_old, post_new, 1)
            t = t[:idx] + sub

p.write_text(t, encoding="utf-8", newline="\n")
print("OK", p)
