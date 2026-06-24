# -*- coding: utf-8 -*-
"""
Restore corrupted Chinese UI sources to valid UTF-8.

Run from paw-rescue repo root:
  D:\\Anaconda\\python.exe scripts\\fix_chinese_encoding.py

Some editors on Windows save UTF-8 Chinese as GBK, which breaks the browser.
This script restores known-good copies from git and rewrites auth pages safely.
"""
from __future__ import annotations

import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

RESTORE_PATHS = [
    'frontend/src/constants/site.js',
    'frontend/public/index.html',
    'frontend/src/pages/Register.js',
    'frontend/src/pages/UserProfile.js',
    'frontend/src/pages/AccountCenter.js',
]


def run_git_restore():
    for rel in RESTORE_PATHS:
        subprocess.check_call(['git', 'checkout', 'HEAD', '--', rel], cwd=ROOT)
        print('restored', rel)


def run_auth_writer():
    script = os.path.join(ROOT, 'scripts', 'write_auth_pages_utf8.py')
    subprocess.check_call([sys.executable, script], cwd=ROOT)


def verify():
    checks = {
        'frontend/src/constants/site.js': b'\xe6\x9a\x96\xe7\x88\xaa\xe6\x95\x91\xe5\x8a\xa9',
        'frontend/src/pages/Login.js': b'\xe6\xac\xa2\xe8\xbf\x8e\xe4\xbd\xbf\xe7\x94\xa8',
        'frontend/src/pages/ForgotPassword.js': b'\xe6\x89\xbe\xe5\x9b\x9e\xe5\xaf\x86\xe7\xa0\x81',
        'frontend/src/pages/Register.js': b'\xe6\xb3\xa8\xe5\x86\x8c\xe5\x89\x8d',
        'frontend/public/index.html': b'\xe6\x9a\x96\xe7\x88\xaa',
    }
    ok = True
    for rel, needle in checks.items():
        path = os.path.join(ROOT, rel)
        raw = open(path, 'rb').read()
        try:
            raw.decode('utf-8')
        except UnicodeDecodeError:
            print('FAIL utf-8 decode', rel)
            ok = False
            continue
        if needle not in raw:
            print('FAIL missing text', rel)
            ok = False
        else:
            print('OK', rel)
    return ok


def main():
    os.chdir(ROOT)
    run_git_restore()
    run_auth_writer()
    if not verify():
        sys.exit(1)
    print('done: restart frontend dev server and hard-refresh browser (Ctrl+F5)')


if __name__ == '__main__':
    main()
