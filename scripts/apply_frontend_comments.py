# -*- coding: utf-8 -*-
"""Add section / export JSDoc comments to core frontend files."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

MODULES = ROOT / "frontend" / "src" / "api" / "modules.js"
SECTIONS = [
    ("export const portalAPI", "/** \u95e8\u6237\u9996\u9875\uff1a\u8f6e\u64ad\u56fe\u4e0e\u7edf\u8ba1\u6570\u636e */"),
    ("export const cmsAPI", "/** CMS \u5185\u5bb9\uff1a\u6587\u7ae0\u3001\u6536\u85cf\u4e0e\u516c\u544a */"),
    ("export const usersAPI", "/** \u7528\u6237\u516c\u5f00\u4e3b\u9875\u4e0e\u5c4f\u853d */"),
    ("export const lostFoundAPI", "/** \u5bfb\u5ba0\u8d44\u52a9\u5e16 */"),
    ("export const communityAPI", "/** \u793e\u533a\u52a8\u6001\u4e0e\u4e92\u52a8 */"),
    ("export const rescueAPI", "/** \u6551\u52a9\u4e8b\u4ef6\u4e0a\u62a5\u4e0e\u67e5\u8be2 */"),
    ("export const adminAPI", "/** \u540e\u53f0\u7ba1\u7406\uff1a\u770b\u677f\u3001\u5ba1\u6838\u3001\u914d\u7f6e\u4e0e AI \u65e5\u5fd7 */"),
    ("export const aiAPI", "/** AI \u8f85\u52a9\uff1a\u54c1\u79cd\u8bc6\u522b\u3001\u9886\u517b\u6587\u6848\u3001\u95ee\u7b54 */"),
    ("export const uploadAPI", "/** \u901a\u7528\u6587\u4ef6\u4e0a\u4f20 */"),
]

MANAGE_CTX = ROOT / "frontend" / "src" / "context" / "ManageModeContext.js"
MANAGE_PATCHES = [
    (
        "export const ManageModeProvider = ({ children }) => {",
        "/** \u63d0\u4f9b\u7ba1\u7406\u5458\u8eab\u4efd\u4e0e\u7ba1\u7406\u6a21\u5f0f\u5f00\u5173\uff08\u6301\u4e45\u5316\u5230 localStorage\uff09 */\n"
        "export const ManageModeProvider = ({ children }) => {",
    ),
    (
        "export const useManageMode = () => useContext(ManageModeContext);",
        "/** \u8bfb\u53d6\u7ba1\u7406\u6a21\u5f0f\u4e0a\u4e0b\u6587\uff1bcanManage = isAdmin && manageMode */\n"
        "export const useManageMode = () => useContext(ManageModeContext);",
    ),
]


def patch_sections(path: Path, sections: list[tuple[str, str]]) -> bool:
    text = path.read_text(encoding="utf-8")
    changed = False
    for marker, comment in sections:
        needle = f"\n{comment}\n{marker}"
        if marker in text and needle not in text:
            text = text.replace(f"\n{marker}", f"\n\n{comment}\n{marker}", 1)
            changed = True
    if changed:
        path.write_text(text, encoding="utf-8", newline="\n")
    return changed


def patch_replacements(path: Path, patches: list[tuple[str, str]]) -> bool:
    text = path.read_text(encoding="utf-8")
    changed = False
    for old, new in patches:
        if old in text and new not in text:
            text = text.replace(old, new, 1)
            changed = True
    if changed:
        path.write_text(text, encoding="utf-8", newline="\n")
    return changed


def main():
    n = 0
    if patch_sections(MODULES, SECTIONS):
        print("modules.js")
        n += 1
    if patch_replacements(MANAGE_CTX, MANAGE_PATCHES):
        print("ManageModeContext.js")
        n += 1
    print("frontend core", n)


if __name__ == "__main__":
    main()
