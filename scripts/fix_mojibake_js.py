# -*- coding: utf-8 -*-
"""Fix UTF-8 Chinese mis-decoded as GBK in JS source files."""
from __future__ import annotations

import os

ROOT = os.path.join(os.path.dirname(__file__), '..', 'frontend', 'src')

PRIORITY_FILES = [
    'pages/Login.js',
    'pages/Register.js',
    'pages/UserProfile.js',
    'pages/AccountCenter.js',
]

# Chars typical of UTF-8 misread as GBK (not normal simplified Chinese UI copy)
MOJIBAKE_MARKERS = (
    '\u9422', '\u7035', '\u93da', '\u7487', '\u5a09', '\u7ba0',
    '\u9550', '\u9352', '\u8e48', '\u6769', '\u6960', '\u9350',
    '\u7f51', '\u3220', '\u6f58', '\u9422', '\u9352', '\u7f51',
)


def has_mojibake(text: str) -> bool:
    return any(m in text for m in MOJIBAKE_MARKERS)


def fix_file(path: str) -> bool:
    with open(path, 'r', encoding='utf-8') as f:
        original = f.read()
    if not has_mojibake(original):
        return False
    try:
        fixed = original.encode('gbk').decode('utf-8')
    except (UnicodeDecodeError, UnicodeEncodeError) as exc:
        print('SKIP %s: %s' % (path, exc))
        return False
    if fixed == original:
        return False
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(fixed)
    print('FIXED %s' % path)
    return True


def main():
    count = 0
    seen = set()
    for rel in PRIORITY_FILES:
        path = os.path.join(ROOT, rel.replace('/', os.sep))
        seen.add(path)
        if os.path.isfile(path) and fix_file(path):
            count += 1
    pages_dir = os.path.join(ROOT, 'pages')
    for fn in os.listdir(pages_dir):
        path = os.path.join(pages_dir, fn)
        if path in seen or not fn.endswith('.js'):
            continue
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        if has_mojibake(content) and fix_file(path):
            count += 1
    utils_dir = os.path.join(ROOT, 'utils')
    if os.path.isdir(utils_dir):
        for fn in os.listdir(utils_dir):
            path = os.path.join(utils_dir, fn)
            if not fn.endswith('.js'):
                continue
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            if has_mojibake(content) and fix_file(path):
                count += 1
    print('Done. Fixed %d file(s).' % count)


if __name__ == '__main__':
    main()
