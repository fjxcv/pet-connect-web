# -*- coding: utf-8 -*-
"""Scan frontend JS for mojibake / invalid UTF-8."""
import os
import re

ROOT = os.path.join(os.path.dirname(__file__), '..', 'frontend', 'src')

# Garbled when UTF-8 read as GBK
GARBLED = re.compile(r'[\u9422\u7035\u93da\u7487\u5a09\u7ba0\u9550\u9352\u8e48\u6769\u6960\u9350\u7f51\u3220\u6f58]')
# Latin-1 misread UTF-8
LATIN = re.compile(r'[\u00c0-\u00ff]{3,}')
# Replacement char
BAD = '\ufffd'

for dirpath, _, files in os.walk(ROOT):
    for fn in files:
        if not fn.endswith(('.js', '.jsx')):
            continue
        path = os.path.join(dirpath, fn)
        try:
            raw = open(path, 'rb').read()
        except OSError:
            continue
        try:
            text = raw.decode('utf-8')
        except UnicodeDecodeError as e:
            print('INVALID_UTF8', path, e)
            continue
        issues = []
        if GARBLED.search(text):
            issues.append('gbk_mojibake')
        if BAD in text:
            issues.append('replacement_char')
        if LATIN.search(text) and 'axios' not in path:
            m = LATIN.search(text)
            issues.append('latin_blob:' + repr(text[m.start():m.start()+40]))
        if issues:
            rel = os.path.relpath(path, ROOT)
            print(rel, '|', ', '.join(issues))
