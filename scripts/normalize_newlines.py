# -*- coding: utf-8 -*-
"""Normalize line endings and collapse excessive blank lines in source files."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCAN = [ROOT / "backend", ROOT / "frontend" / "src"]
SKIP = {"migrations", "__pycache__", "venv", "node_modules"}
EXTS = {".py", ".js", ".jsx"}


def normalize(path: Path) -> bool:
    raw = path.read_bytes()
    if raw.startswith(b"\xef\xbb\xbf"):
        raw = raw[3:]
    for enc in ("utf-8", "gbk"):
        try:
            text = raw.decode(enc)
            break
        except UnicodeDecodeError:
            continue
    else:
        return False
    fixed = text.replace("\r\n", "\n").replace("\r", "\n")
    fixed = re.sub(r"\n{3,}", "\n\n", fixed)
    if not fixed.endswith("\n"):
        fixed += "\n"
    if fixed != text.replace("\r\n", "\n").replace("\r", "\n"):
        path.write_text(fixed, encoding="utf-8", newline="\n")
        return True
    if text != fixed:
        path.write_text(fixed, encoding="utf-8", newline="\n")
        return True
    return False


def main():
    n = 0
    for base in SCAN:
        if not base.exists():
            continue
        for path in base.rglob("*"):
            if not path.is_file() or path.suffix not in EXTS:
                continue
            if any(p in SKIP for p in path.parts):
                continue
            if normalize(path):
                n += 1
                print(path.relative_to(ROOT))
    print("normalized", n)


if __name__ == "__main__":
    main()
