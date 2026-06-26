# -*- coding: utf-8 -*-
"""Batch add Chinese file headers for PawRescue sources."""
from __future__ import annotations
import json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BACKEND = ROOT / "backend"
FRONTEND_SRC = ROOT / "frontend" / "src"
SKIP_PARTS = {"migrations", "__pycache__", "venv", "node_modules"}
SKIP_NAMES = {"setupTests.js", "reportWebVitals.js", "App.test.js", "test_api.py", "original_views.py"}
DOCS_PATH = Path(__file__).with_name("annotate_docs.json")
MARKER_PY = "\u6a21\u5757\u8bf4\u660e\uff1a"
MARKER_JS = "@module PawRescue"

# Built-in detailed docs (ASCII source, Unicode via escapes) when JSON file missing/corrupt
BUILTIN_DOCS = {
    "files": {
        "backend/system/views.py": "\u667a\u80fd\u540e\u53f0\u7ba1\u7406\u4e0e AI \u8f85\u52a9 API \u89c6\u56fe\u3002",
        "backend/system/models.py": "\u540e\u53f0\u6cbb\u7406 ORM\uff1a\u64cd\u4f5c\u65e5\u5fd7\u3001\u5185\u5bb9\u5904\u7f6e\u3001\u5e73\u53f0\u914d\u7f6e\u3001AI \u8c03\u7528\u65e5\u5fd7\u3002",
        "backend/system/moderation_apply.py": "\u5185\u5bb9\u5904\u7f6e\u8054\u52a8\uff1a\u5ba1\u6838\u52a8\u4f5c\u540c\u6b65\u5230\u4e1a\u52a1\u8868\u3002",
        "backend/common/permissions.py": "DRF \u6743\u9650\u7c7b\uff1a\u7ba1\u7406\u5458\u5224\u5b9a\u3001\u5c01\u7981\u62e6\u622a\u3002",
        "backend/common/ai_quota.py": "AI \u8c03\u7528\u914d\u989d\u68c0\u67e5\u4e0e\u7528\u91cf\u7edf\u8ba1\u3002",
        "backend/common/llm_client.py": "\u5927\u8bed\u8a00\u6a21\u578b\u7edf\u4e00\u5c01\u88c5\u3002",
        "backend/common/breed_detect.py": "\u54c1\u79cd\u8bc6\u522b\u4e1a\u52a1\u7f16\u6392\u3002",
        "backend/common/breed_classifier.py": "MobileNetV3 \u672c\u5730\u63a8\u7406\u3002",
        "backend/common/utils.py": "\u901a\u7528\u5de5\u5177\uff1a\u5ba1\u8ba1\u65e5\u5fd7\u3001IP \u63d0\u53d6\u3002",
        "backend/pets/views.py": "\u5ba0\u7269\u6863\u6848\u4e0e\u9886\u517b API\u3002",
        "backend/accounts/views.py": "\u7528\u6237\u8ba4\u8bc1 API\u3002",
        "frontend/src/context/ManageModeContext.js": "\u7ba1\u7406\u5458\u6a21\u5f0f\u4e0a\u4e0b\u6587\u3002",
        "frontend/src/components/AdminManageBar.js": "\u524d\u53f0\u7ba1\u7406\u5de5\u5177\u6761\u3002",
        "frontend/src/components/AiAssistantWidget.js": "\u667a\u80fd\u517b\u5ba0\u95ee\u7b54\u6302\u4ef6\u3002",
        "frontend/src/pages/AdminDashboard.js": "\u7ba1\u7406\u540e\u53f0\u4e3b\u9875\u3002",
        "frontend/src/pages/AddPet.js": "\u6dfb\u52a0\u5ba0\u7269\u6863\u6848\u9875\u3002",
        "frontend/src/App.js": "React \u6839\u7ec4\u4ef6\u4e0e\u8def\u7531\u3002",
        "frontend/src/api/modules.js": "REST API \u6a21\u5757\u5316\u5c01\u88c5\u3002",
    },
    "classes": {
        "AdminDashboardView": "\u8fd0\u8425\u6570\u636e\u770b\u677f\u3002",
        "AdminUserViewSet": "\u540e\u53f0\u7528\u6237\u7ba1\u7406\u3002",
        "AdminModerationViewSet": "\u5185\u5bb9\u5ba1\u6838\u4e0e\u8054\u52a8\u3002",
        "AdminConfigViewSet": "\u5e73\u53f0\u914d\u7f6e\u3002",
        "AiBreedDetectView": "AI \u54c1\u79cd\u8bc6\u522b\u3002",
        "AiAdoptCopyView": "AI \u9886\u517b\u6587\u6848\u3002",
        "AiQaView": "AI \u667a\u80fd\u95ee\u7b54\u3002",
        "AdminAiLogViewSet": "AI \u8c03\u7528\u65e5\u5fd7\u3002",
        "PetProfileViewSet": "\u5ba0\u7269\u6863\u6848 ViewSet\u3002",
        "IsAdminRole": "\u7ba1\u7406\u5458\u6743\u9650\u3002",
        "IsActiveUser": "\u6d3b\u8dc3\u7528\u6237\u6743\u9650\u3002",
    },
}


def load_docs():
    if DOCS_PATH.exists():
        try:
            return json.loads(read_text_safe(DOCS_PATH))
        except json.JSONDecodeError:
            pass
    return BUILTIN_DOCS

def rel(path: Path) -> str:
    return str(path.relative_to(ROOT)).replace("\\", "/")

def guess_doc(r, path, files):
    if r in files:
        return files[r]
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
        }
        return mapping.get(name, f"\u6e90\u7801\uff1a{r}")
    if r.startswith("frontend/src/pages/"):
        return f"\u9875\u9762\u7ec4\u4ef6\uff1a{path.stem}\u3002"
    if r.startswith("frontend/src/components/"):
        return f"\u53ef\u590d\u7528\u7ec4\u4ef6\uff1a{path.stem}\u3002"
    return f"\u6e90\u7801\uff1a{r}"

def read_text_safe(path: Path) -> str:
    raw = path.read_bytes()
    for enc in ("utf-8", "utf-8-sig", "gbk"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", errors="replace")


def has_py_header(text):
    return MARKER_PY in text[:800]

def has_js_header(text):
    return MARKER_JS in text[:600]

def annotate_py(path, data):
    text = read_text_safe(path)
    changed = False
    r = rel(path)
    if not has_py_header(text) and not text.startswith('"""'):
        doc = guess_doc(r, path, data["files"])
        text = f'"""\n{MARKER_PY}{doc}\n"""\n\n' + text
        changed = True
    for cls, cdoc in data.get("classes", {}).items():
        pat = rf"(class {cls}\([^\)]*\):)\n(?!\s+\"\"\")"
        text, n = re.subn(pat, rf'\1\n    """{cdoc}"""\n', text, count=1)
        if n:
            changed = True
    if changed:
        path.write_text(text, encoding="utf-8")
    return changed

def annotate_js(path, data):
    text = read_text_safe(path)
    if has_js_header(text):
        return False
    r = rel(path)
    doc = guess_doc(r, path, data["files"])
    header = f"/**\n * @file {path.name}\n * @module PawRescue\n * @description {doc}\n */\n\n"
    path.write_text(header + text, encoding="utf-8")
    return True

def main():
    data = load_docs()
    py_n = js_n = 0
    for base, exts in ((BACKEND, {".py"}), (FRONTEND_SRC, {".js", ".jsx"})):
        if not base.exists():
            continue
        for path in base.rglob("*"):
            if not path.is_file() or path.suffix not in exts:
                continue
            if any(p in SKIP_PARTS for p in path.parts):
                continue
            if path.name in SKIP_NAMES or path.name == "annotate_zh_comments.py":
                continue
            if path.suffix == ".py":
                if annotate_py(path, data):
                    py_n += 1
                    print("py", rel(path))
            else:
                if annotate_js(path, data):
                    js_n += 1
                    print("js", rel(path))
    print("done", py_n, js_n)

if __name__ == "__main__":
    main()