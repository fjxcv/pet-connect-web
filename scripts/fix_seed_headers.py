# -*- coding: utf-8 -*-
"""Fix seed script headers: single UTF-8 module docstring only."""
from pathlib import Path

BACKEND = Path(__file__).resolve().parent.parent / "backend"

SEEDS = {
    "system/management/commands/seed_demo.py": "\u6f14\u793a\u6570\u636e\u79cd\u5b50\u811a\u672c\uff08\u7b54\u8fa9\u4e0d\u91cd\u70b9\u8bb2\u89e3\uff09\u3002",
    "system/management/commands/seed_test_data.py": "\u6d4b\u8bd5\u6570\u636e\u79cd\u5b50\u811a\u672c\uff08\u7b54\u8fa9\u4e0d\u91cd\u70b9\u8bb2\u89e3\uff09\u3002",
}

for rel, desc in SEEDS.items():
    p = BACKEND / rel
    text = p.read_text(encoding="utf-8")
    while text.startswith('"""'):
        end = text.index('"""', 3) + 3
        text = text[end:].lstrip("\n\r")
    if text.startswith("# -*- coding"):
        line_end = text.find("\n") + 1
        text = text[line_end:].lstrip("\n\r")
    while text.startswith('"""'):
        end = text.index('"""', 3) + 3
        text = text[end:].lstrip("\n\r")
    header = '"""\n\u6a21\u5757\u8bf4\u660e\uff1a' + desc + '\n"""\n\n'
    p.write_text(header + text, encoding="utf-8", newline="\n")
    print("fixed", rel)
