# -*- coding: utf-8 -*-
"""Remove spurious blank lines between every code line (batch annotation artifact)."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCAN = [ROOT / "backend", ROOT / "frontend" / "src"]
SKIP = {"migrations", "__pycache__", "venv", "node_modules"}
EXTS = {".py", ".js", ".jsx"}


def is_corrupted(text: str) -> bool:
    lines = text.split("\n")
    if len(lines) < 30:
        return False
    empty = sum(1 for l in lines if not l.strip())
    return empty / len(lines) > 0.33


def fix_text(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    # Remove blank line between two non-empty lines
    prev = text
    while True:
        text = re.sub(r"([^\n])\n\n([^\n])", r"\1\n\2", text)
        if text == prev:
            break
        prev = text
    # Restore PEP8 / style blank lines before top-level class/function (Python)
    text = re.sub(r"\n(class )", r"\n\n\1", text)
    text = re.sub(r"\n(def )", r"\n\n\1", text)
    text = re.sub(r"\n(export )", r"\n\n\1", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    if not text.endswith("\n"):
        text += "\n"
    return text


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
            try:
                text = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            if not is_corrupted(text):
                continue
            fixed = fix_text(text)
            if fixed != text:
                path.write_text(fixed, encoding="utf-8", newline="\n")
                n += 1
                print(path.relative_to(ROOT))
    print("fixed", n)


if __name__ == "__main__":
    main()
