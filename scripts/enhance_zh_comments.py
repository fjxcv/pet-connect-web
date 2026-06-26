# -*- coding: utf-8 -*-
"""Fix garbled Chinese headers and add method-level docstrings (ASCII source, Unicode via escapes)."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BACKEND = ROOT / "backend"
FRONTEND_SRC = ROOT / "frontend" / "src"
SKIP_PARTS = {"migrations", "__pycache__", "venv", "node_modules"}
SKIP_NAMES = {"setupTests.js", "reportWebVitals.js", "App.test.js", "test_api.py", "original_views.py"}

MARKER_PY = "\u6a21\u5757\u8bf4\u660e\uff1a"

# --- file-level descriptions ---
FILE_DOCS: dict[str, str] = {
    "backend/system/views.py": (
        "\u667a\u80fd\u540e\u53f0\u7ba1\u7406\u4e0e AI \u8f85\u52a9 API \u89c6\u56fe\u3002"
        "\u5305\u542b\u8fd0\u8425\u770b\u677f\u3001\u7528\u6237\u7ba1\u7406\u3001\u5185\u5bb9\u5ba1\u6838\u3001"
        "\u5e73\u53f0\u914d\u7f6e\u3001AI \u8bc6\u522b/\u6587\u6848/\u95ee\u7b54\u4e0e\u8c03\u7528\u65e5\u5fd7\u3002"
    ),
    "backend/system/models.py": "\u540e\u53f0\u6cbb\u7406 ORM\uff1a\u64cd\u4f5c\u65e5\u5fd7\u3001\u5185\u5bb9\u5904\u7f6e\u3001\u5e73\u53f0\u914d\u7f6e\u3001AI \u8c03\u7528\u65e5\u5fd7\u3002",
    "backend/system/moderation_apply.py": "\u5185\u5bb9\u5904\u7f6e\u8054\u52a8\uff1a\u5ba1\u6838\u52a8\u4f5c\u540c\u6b65\u5230\u4e1a\u52a1\u8868\u3002",
    "backend/system/serializers.py": "system \u6a21\u5757\u5e8f\u5217\u5316\u5668\u3002",
    "backend/system/urls.py": "system \u6a21\u5757 URL \u8def\u7531\u3002",
    "backend/common/permissions.py": "DRF \u6743\u9650\u7c7b\uff1a\u7ba1\u7406\u5458\u5224\u5b9a\u3001\u5c01\u7981\u62e6\u622a\u3002",
    "backend/common/ai_quota.py": "AI \u8c03\u7528\u914d\u989d\u68c0\u67e5\u4e0e\u7528\u91cf\u7edf\u8ba1\u3002",
    "backend/common/llm_client.py": "\u5927\u8bed\u8a00\u6a21\u578b\u7edf\u4e00\u5c01\u88c5\uff08\u8baf\u98de\u661f\u706b / OpenAI \u517c\u5bb9 HTTP\uff09\u3002",
    "backend/common/breed_detect.py": "\u54c1\u79cd\u8bc6\u522b\u4e1a\u52a1\u7f16\u6392\uff1a\u672c\u5730 CNN \u63a8\u7406\u4e0e\u7f6e\u4fe1\u5ea6\u8865\u5168\u3002",
    "backend/common/breed_classifier.py": "MobileNetV3 \u672c\u5730\u63a8\u7406\u4e0e\u6743\u91cd\u52a0\u8f7d\u3002",
    "backend/common/utils.py": "\u901a\u7528\u5de5\u5177\uff1a\u5ba1\u8ba1\u65e5\u5fd7\u3001\u5ba2\u6237\u7aef IP \u63d0\u53d6\u3002",
    "backend/common/image_loader.py": "\u56fe\u7247\u52a0\u8f7d\uff1aURL / Base64 / \u672c\u5730\u4e0a\u4f20\u6587\u4ef6\u3002",
    "backend/pets/views.py": "\u5ba0\u7269\u6863\u6848\u4e0e\u9886\u517b\u7533\u8bf7 API\u3002",
    "backend/accounts/views.py": "\u7528\u6237\u8ba4\u8bc1\u4e0e\u4e2a\u4eba\u8d44\u6599 API\u3002",
    "frontend/src/context/ManageModeContext.js": "\u7ba1\u7406\u5458\u6a21\u5f0f\u4e0a\u4e0b\u6587\uff1a\u63a7\u5236\u524d\u53f0\u7ba1\u7406\u5de5\u5177\u6761\u53ef\u89c1\u6027\u3002",
    "frontend/src/components/AdminManageBar.js": "\u524d\u53f0\u7ba1\u7406\u5de5\u5177\u6761\uff1a\u5207\u6362\u7ba1\u7406\u6a21\u5f0f\u4e0e\u5feb\u6377\u5165\u53e3\u3002",
    "frontend/src/components/AiAssistantWidget.js": "\u667a\u80fd\u517b\u5ba0\u95ee\u7b54\u6302\u4ef6\uff08\u53ef\u62d6\u62fd\u6d6e\u7a97\uff09\u3002",
    "frontend/src/pages/AdminDashboard.js": "\u7ba1\u7406\u540e\u53f0\u4e3b\u9875\uff1a\u8fd0\u8425\u6570\u636e\u4e0e\u5ba1\u6838\u5165\u53e3\u3002",
    "frontend/src/pages/AddPet.js": "\u6dfb\u52a0 / \u7f16\u8f91\u5ba0\u7269\u6863\u6848\u9875\uff08\u4ec5\u7ba1\u7406\u5458\uff09\u3002",
    "frontend/src/App.js": "React \u6839\u7ec4\u4ef6\u4e0e\u8def\u7531\u914d\u7f6e\u3002",
    "frontend/src/api/modules.js": "REST API \u6a21\u5757\u5316\u5c01\u88c5\u3002",
}

CLASS_DOCS: dict[str, str] = {
    "AdminDashboardView": "\u8fd0\u8425\u6570\u636e\u770b\u677f\uff1a\u805a\u5408\u5168\u7ad9 KPI\uff0c\u4ec5\u7ba1\u7406\u5458\u53ef\u8bfb\u3002",
    "AdminUserViewSet": "\u540e\u53f0\u7528\u6237\u7ba1\u7406\uff1a\u5217\u8868\u7b5b\u9009\u3001\u5c01\u7981\u4e0e\u89d2\u8272\u8c03\u6574\u3002",
    "AdminModerationViewSet": "\u5185\u5bb9\u5ba1\u6838\uff1a\u5199\u5165\u5ba1\u6838\u8bb0\u5f55\u5e76\u8054\u52a8\u4e1a\u52a1\u8868\u3002",
    "AdminConfigViewSet": "\u5e73\u53f0\u914d\u7f6e\u7ef4\u62a4\uff08\u542b AI \u914d\u989d\u7b49\uff09\u3002",
    "AdminOperationLogViewSet": "\u64cd\u4f5c\u5ba1\u8ba1\u65e5\u5fd7\u53ea\u8bfb\u67e5\u8be2\u3002",
    "AiBreedDetectView": "AI \u54c1\u79cd\u8bc6\u522b\u63a5\u53e3\u3002",
    "AiAdoptCopyView": "AI \u9886\u517b\u6587\u6848\u751f\u6210\u63a5\u53e3\u3002",
    "AiQaView": "AI \u667a\u80fd\u517b\u5ba9\u95ee\u7b54\u63a5\u53e3\u3002",
    "AdminAiLogViewSet": "AI \u8c03\u7528\u65e5\u5fd7\u67e5\u8be2\u4e0e\u7528\u91cf\u7edf\u8ba1\u3002",
    "PetProfileViewSet": "\u5ba0\u7269\u6863\u6848 CRUD\u3001\u9644\u8fd1\u67e5\u8be2\u4e0e\u6211\u7684\u5ba0\u7269\u3002",
    "AdoptApplicationViewSet": "\u9886\u517b\u7533\u8bf7\u63d0\u4ea4\u3001\u95ee\u5377\u4e0e\u9644\u4ef6\u3002",
    "AdminAdoptApplicationViewSet": "\u7ba1\u7406\u5458\u9886\u517b\u5ba1\u6838\u4e0e\u8be6\u60c5\u67e5\u8be2\u3002",
    "AdminOfflineVerifyViewSet": "\u7ebf\u4e0b\u6838\u9a8c\u7ed3\u679c\u5f55\u5165\u4e0e\u8054\u52a8\u5ba0\u7269\u72b6\u6001\u3002",
    "IsAdminRole": "\u7ba1\u7406\u5458\u89d2\u8272\u6743\u9650\u68c0\u67e5\u3002",
    "IsActiveUser": "\u672a\u5c01\u7981\u7528\u6237\u624d\u53ef\u8bbf\u95ee\u3002",
    "AiQuotaExceededError": "AI \u8c03\u7528\u8d85\u51fa\u5e73\u53f0\u914d\u989d\u65f6\u629b\u51fa\u3002",
    "LLMNotConfiguredError": "LLM \u672a\u914d\u7f6e\u6216\u7f3a\u5c11\u4f9d\u8d56\u3002",
    "LLMRequestError": "LLM \u4e0a\u6e38\u8bf7\u6c42\u5931\u8d25\u3002",
}

# rel_path -> {func_name: doc}
FUNC_DOCS: dict[str, dict[str, str]] = {
    "backend/system/moderation_apply.py": {
        "apply_moderation": "\u5c06\u5ba1\u6838\u52a8\u4f5c\uff08hide/delete/ban\uff09\u540c\u6b65\u5230\u5bf9\u5e94\u4e1a\u52a1\u8868\u8bb0\u5f55\u3002",
    },
    "backend/common/ai_quota.py": {
        "_get_config_int": "\u4ece PlatformConfig \u8bfb\u53d6\u6574\u6570\u914d\u7f6e\uff0c\u7f3a\u5931\u6216\u975e\u6cd5\u65f6\u8fd4\u56de\u9ed8\u8ba4\u503c\u3002",
        "get_ai_usage_stats": "\u7edf\u8ba1\u4eca\u65e5/\u7d2f\u8ba1 AI \u8c03\u7528\u6b21\u6570\u4e0e\u5e73\u53f0\u914d\u989d\u4e0a\u9650\u3002",
        "check_ai_quota": "\u68c0\u67e5\u662f\u5426\u8d85\u51fa\u65e5/\u603b\u914d\u989d\uff0c\u8d85\u9650\u5219\u629b\u51fa AiQuotaExceededError\u3002",
        "log_quota_exceeded": "\u8bb0\u5f55\u4e00\u6761\u914d\u989d\u8d85\u9650\u7684\u5931\u8d25\u65e5\u5fd7\u3002",
    },
    "backend/common/llm_client.py": {
        "_spark_configured": "\u68c0\u67e5\u8baf\u98de\u661f\u706b\u73af\u5883\u53d8\u91cf\u662f\u5426\u5df2\u914d\u7f6e\u3002",
        "_spark_auth_url": "\u751f\u6210\u661f\u706b WebSocket \u9274\u6743 URL\u3002",
        "_normalize_messages": "\u5c06\u6d88\u606f\u5217\u8868\u7edf\u4e00\u4e3a\u6587\u672c\u683c\u5f0f\u3002",
        "_spark_chat_completion": "\u901a\u8fc7\u661f\u706b WebSocket \u5b8c\u6210\u5bf9\u8bdd\u3002",
        "_http_chat_completion": "\u901a\u8fc7 OpenAI \u517c\u5bb9 HTTP \u63a5\u53e3\u5b8c\u6210\u5bf9\u8bdd\u3002",
        "_chat_completion": "\u4f18\u5148\u661f\u706b\uff0c\u5426\u5219\u8d70 HTTP \u517c\u5bb9\u63a5\u53e3\u3002",
        "chat": "\u5bf9\u5916\u7edf\u4e00\u6587\u672c\u5bf9\u8bdd\u5165\u53e3\u3002",
        "chat_vision": "\u591a\u6a21\u6001\u5bf9\u8bdd\u5165\u53e3\uff08\u56fe\u7247 + \u6587\u672c\uff09\u3002",
    },
    "backend/common/breed_detect.py": {
        "_fallback_breeds_for_species": "\u6309\u7269\u79cd\u8fd4\u56de\u4f4e\u7f6e\u4fe1\u5ea6\u65f6\u7684\u9ed8\u8ba4\u54c1\u79cd\u5019\u9009\u3002",
        "_ensure_breed_candidates": "\u8865\u5168\u5019\u9009\u5217\u8868\u5e76\u6807\u8bb0\u662f\u5426\u4f4e\u7f6e\u4fe1\u5ea6\u3002",
        "_build_result_text": "\u751f\u6210\u7528\u6237\u53ef\u8bfb\u7684\u8bc6\u522b\u6458\u8981\u6587\u672c\u3002",
        "_predictions_to_payload": "\u5c06\u6a21\u578b\u8f93\u51fa\u8f6c\u4e3a API \u54cd\u5e94\u7ed3\u6784\u3002",
        "detect_pet_breed": "\u54c1\u79cd\u8bc6\u522b\u4e3b\u6d41\u7a0b\uff1a\u52a0\u8f7d\u56fe\u7247 \u2192 \u672c\u5730\u63a8\u7406 \u2192 \u8fd4\u56de\u7ed3\u679c\u3002",
    },
    "backend/common/permissions.py": {
        "user_is_admin": "\u5224\u5b9a\u7528\u6237\u662f\u5426\u4e3a\u7ba1\u7406\u5458\uff08staff / superuser / profile.role\uff09\u3002",
    },
    "backend/common/utils.py": {
        "write_operation_log": "\u5199\u5165\u4e00\u6761\u540e\u53f0\u64cd\u4f5c\u5ba1\u8ba1\u65e5\u5fd7\u3002",
        "get_client_ip": "\u4ece\u8bf7\u6c42\u5934\u63d0\u53d6\u5ba2\u6237\u7aef IP\uff08\u652f\u6301 X-Forwarded-For\uff09\u3002",
    },
    "backend/system/views.py": {
        "_ai_error_response": "\u5c06 LLM \u5f02\u5e38\u6620\u5c04\u4e3a 503\uff08\u672a\u914d\u7f6e\uff09\u6216 502\uff08\u4e0a\u6e38\u5931\u8d25\uff09\u3002",
        "_ai_quota_response": "\u914d\u989d\u8d85\u9650\u65f6\u8bb0\u5931\u8d25\u65e5\u5fd7\u5e76\u8fd4\u56de HTTP 429\u3002",
        "stats": "\u7ba1\u7406\u5458\u67e5\u8be2 AI \u8c03\u7528\u7528\u91cf\u7edf\u8ba1\u3002",
    },
    "backend/pets/views.py": {
        "_haversine_distance": "\u8ba1\u7b97\u4e24\u70b9\u95f4\u7403\u9762\u8ddd\u79bb\uff08\u5343\u7c73\uff09\u3002",
        "get_serializer_class": "\u66f4\u65b0\u64cd\u4f5c\u4f7f\u7528 PetProfileUpdateSerializer\u3002",
        "get_permissions": "\u5217\u8868/\u8be6\u60c5\u516c\u5f00\uff0c\u521b\u5efa\u7b49\u9700\u7ba1\u7406\u5458\u6743\u9650\u3002",
        "get_queryset": "\u6309\u67e5\u8be2\u53c2\u6570\u7b5b\u9009\u5ba0\u7269\uff0c\u975e\u7ba1\u7406\u5458\u9ed8\u8ba4\u53ea\u770b\u516c\u5f00\u6863\u6848\u3002",
        "nearby": "\u6309\u7ecf\u7eac\u5ea6\u4e0e\u534a\u5f84\uff08Haversine\uff09\u67e5\u8be2\u9644\u8fd1\u5ba0\u7269\u3002",
        "my_pets": "\u8fd4\u56de\u5f53\u524d\u7528\u6237\u901a\u8fc7\u6551\u52a9\u6848\u4e0a\u4f20\u7684\u5ba0\u7269\u5217\u8868\u3002",
        "perform_create": "\u521b\u5efa\u9886\u517b\u7533\u8bf7\u5e76\u5c06\u5ba0\u7269\u72b6\u6001\u6539\u4e3a pending\u3002",
        "questionnaire": "\u63d0\u4ea4\u9886\u517b\u95ee\u5377\u7b54\u6848\u3002",
        "attachments": "\u4e0a\u4f20\u9886\u517b\u7533\u8bf7\u9644\u4ef6\u3002",
        "review_detail": "\u7ba1\u7406\u5458\u67e5\u770b\u7533\u8bf7\u5ba1\u6838\u8be6\u60c5\u3002",
        "update": "\u7ba1\u7406\u5458\u5ba1\u6838\u9886\u517b\u7533\u8bf7\u5e76\u8bb0\u5ba1\u8ba1\u65e5\u5fd7\u3002",
        "create_for_application": "\u4e3a\u7533\u8bf7\u5355\u521b\u5efa\u6216\u83b7\u53d6\u7ebf\u4e0b\u6838\u9a8c\u8bb0\u5f55\u3002",
    },
}

# Fix corrupted string literals (mojibake -> correct Chinese)
LITERAL_FIXES: list[tuple[str, str]] = [
    ("\u6dfb\u52a0\u5ba0\u7269\u6863\u6848\u9875", None),  # placeholder skip
]
# Actual mojibake patterns found in codebase
MOJIBAKE_REPLACEMENTS: list[tuple[str, str]] = [
    # country name
    ("\u6d93\uFE00\u6d93\u6d93\u6d93", "\u4e2d\u56fd"),  # won't match - use regex below
]

# Known wrong -> right (using explicit wrong strings from files)
STRING_FIXES = [
    ("country: '\u6d93\uFE00\u6d93\u6d93\u6d93'", "country: '\u4e2d\u56fd'"),
    ("country: '\u6d88\u56fd'", "country: '\u4e2d\u56fd'"),
    ("['\u6d88\u56fd', 'CN', 'cn']", "['\u4e2d\u56fd', 'CN', 'cn']"),
    ("'\u7c7b\u578b\u9519\u8bef'", "'\u7c7b\u578b\u9519\u8bef'"),  # noop
]
# pets/views nearby error messages - use unicode for correct
NEARBY_ERR_LAT = "\u8bf7\u63d0\u4f9b\u6709\u6548\u7684\u7ecf\u7eac\u5ea6\u53c2\u6570\uff08lat, lon\uff09"
NEARBY_ERR_LON = "\u8bf7\u63d0\u4f9b\u7ecf\u7eac\u5ea6\u53c2\u6570"


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT)).replace("\\", "/")


def guess_doc(r: str, path: Path) -> str:
    if r in FILE_DOCS:
        return FILE_DOCS[r]
    name = path.name
    if r.startswith("backend/"):
        app = r.split("/")[1] if len(r.split("/")) > 1 else ""
        mapping = {
            "views.py": f"{app} \u6a21\u5757 API \u89c6\u56fe\u3002",
            "models.py": f"{app} \u6a21\u5757\u6570\u636e\u6a21\u578b\uff08ORM\uff09\u3002",
            "serializers.py": f"{app} \u6a21\u5757\u5e8f\u5217\u5316\u5668\u3002",
            "urls.py": f"{app} \u6a21\u5757 URL \u8def\u7531\u3002",
            "apps.py": f"{app} Django App \u914d\u7f6e\u3002",
            "admin.py": f"{app} Django Admin \u6ce8\u518c\u3002",
            "signals.py": f"{app} \u4fe1\u53f7\u5904\u7406\u5668\u3002",
        }
        return mapping.get(name, f"\u6e90\u7801\uff1a{r}")
    if r.startswith("frontend/src/pages/"):
        return f"\u9875\u9762\u7ec4\u4ef6\uff1a{path.stem}\u3002"
    if r.startswith("frontend/src/components/"):
        return f"\u53ef\u590d\u7528\u7ec4\u4ef6\uff1a{path.stem}\u3002"
    if r.startswith("frontend/src/context/"):
        return f"React Context\uff1a{path.stem}\u3002"
    if r.startswith("frontend/src/api/"):
        return f"API \u5c01\u88c5\uff1a{path.stem}\u3002"
    if r.startswith("frontend/src/utils/"):
        return f"\u5de5\u5177\u51fd\u6570\uff1a{path.stem}\u3002"
    return f"\u6e90\u7801\uff1a{r}"


def read_text_safe(path: Path) -> str:
    raw = path.read_bytes()
    for enc in ("utf-8", "utf-8-sig", "gbk"):
        try:
            text = raw.decode(enc)
            break
        except UnicodeDecodeError:
            continue
    else:
        text = raw.decode("utf-8", errors="replace")
    return text.replace("\r\n", "\n").replace("\r", "\n")


def fix_py_header(text: str, doc: str) -> str:
    new_header = f'"""\n{MARKER_PY}{doc}\n"""\n\n'
    if text.startswith('"""'):
        end = text.find('"""', 3)
        if end != -1:
            return new_header + text[end + 3 :].lstrip("\n")
    elif text.startswith("'''"):
        end = text.find("'''", 3)
        if end != -1:
            return new_header + text[end + 3 :].lstrip("\n")
    return new_header + text


def fix_js_header(text: str, filename: str, doc: str) -> str:
    new_header = f"/**\n * @file {filename}\n * @module PawRescue\n * @description {doc}\n */\n\n"
    if text.startswith("/**"):
        end = text.find("*/")
        if end != -1:
            return new_header + text[end + 2 :].lstrip("\n")
    return new_header + text


def fix_class_docstrings(text: str) -> str:
    for cls, cdoc in CLASS_DOCS.items():
        pat = rf"(class {cls}(\([^\)]*\))?:)\n(?!\s+\"\"\")"
        text, _ = re.subn(pat, rf'\1\n    """{cdoc}"""\n', text, count=1)
        pat2 = rf"(class {cls}(\([^\)]*\))?:)\n\s+\"\"\"[^\"]*\"\"\"\n"
        text, _ = re.subn(pat2, rf'\1\n    """{cdoc}"""\n', text, count=1)
    return text


def fix_func_docstrings(text: str, r: str) -> str:
    """Add method docstrings only when the next line is not already a docstring."""
    docs = FUNC_DOCS.get(r, {})
    for func, fdoc in docs.items():
        # Module-level function
        pat_mod = rf"(^def {re.escape(func)}\([^\)]*\):)\n(?!\s+\"\"\")"
        text, n = re.subn(pat_mod, rf'\1\n    """{fdoc}"""\n', text, count=1, flags=re.MULTILINE)
        if n:
            continue
        # Class method (4-space indent)
        pat_cls = rf"(^    def {re.escape(func)}\([^\)]*\):)\n(?!\s+\"\"\")"
        text, n = re.subn(pat_cls, rf'\1\n        """{fdoc}"""\n', text, count=1, flags=re.MULTILINE)
    if r == "backend/system/views.py":
        pat = (
            r"(^    @action\(detail=False, methods=\['get'\]\)\n"
            r"    def stats\(self, request\):)\n(?!\s+\"\"\")"
        )
        text, _ = re.subn(
            pat,
            rf'\1\n        """{FUNC_DOCS[r]["stats"]}"""\n',
            text,
            count=1,
            flags=re.MULTILINE,
        )
    return text


def fix_mojibake_strings(text: str, r: str = "") -> str:
    # Fix country default in AddPet.js only
    if r.endswith("frontend/src/pages/AddPet.js"):
        text = re.sub(
            r"country:\s*'[^']*'",
            "country: '\u4e2d\u56fd'",
            text,
            count=1,
        )

    # Fix pets/views nearby error messages
    if r == "backend/pets/views.py":
        text = re.sub(
            r"\{'detail': '[^']*'\}, status=status\.HTTP_400_BAD_REQUEST\)\s*\n\n\s+if not lat",
            f"{{'detail': '{NEARBY_ERR_LAT}'}}, status=status.HTTP_400_BAD_REQUEST)\n\n        if not lat",
            text,
            count=1,
        )
        text = re.sub(
            r"\{'detail': '[^']*'\}, status=status\.HTTP_400_BAD_REQUEST\)\s*\n\n\s+qs = self\.get_queryset",
            f"{{'detail': '{NEARBY_ERR_LON}'}}, status=status.HTTP_400_BAD_REQUEST)\n\n        qs = self.get_queryset",
            text,
            count=1,
        )
    # Fix country filter list
    text = re.sub(
        r"\[['\"][^'\"]*['\"],\s*'CN',\s*'cn'\]",
        "['\u4e2d\u56fd', 'CN', 'cn']",
        text,
        count=1,
    )
    return text


def process_py(path: Path) -> bool:
    r = rel(path)
    text = read_text_safe(path)
    orig = text
    doc = guess_doc(r, path)
    text = fix_py_header(text, doc)
    text = fix_class_docstrings(text)
    text = fix_func_docstrings(text, r)
    text = fix_mojibake_strings(text, r)
    if text != orig:
        path.write_text(text, encoding="utf-8", newline="\n")
        return True
    return False


def process_js(path: Path) -> bool:
    r = rel(path)
    text = read_text_safe(path)
    orig = text
    doc = guess_doc(r, path)
    text = fix_js_header(text, path.name, doc)
    text = fix_mojibake_strings(text, r)
    if text != orig:
        path.write_text(text, encoding="utf-8", newline="\n")
        return True
    return False


def main():
    py_n = js_n = 0
    for base, exts in ((BACKEND, {".py"}), (FRONTEND_SRC, {".js", ".jsx"})):
        if not base.exists():
            continue
        for path in base.rglob("*"):
            if not path.is_file() or path.suffix not in exts:
                continue
            if any(p in SKIP_PARTS for p in path.parts):
                continue
            if path.name in SKIP_NAMES:
                continue
            if path.suffix == ".py":
                if r == "backend/system/views.py":
                    continue  # use scripts/apply_views_comments.py
                if process_py(path):
                    py_n += 1
                    print("py", rel(path))
            else:
                if process_js(path):
                    js_n += 1
                    print("js", rel(path))
    print("enhanced", py_n, js_n)


if __name__ == "__main__":
    main()
