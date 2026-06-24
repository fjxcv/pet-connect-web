# -*- coding: utf-8 -*-
import os

files = [
    'src/constants/site.js',
    'src/pages/ForgotPassword.js',
    'src/pages/Login.js',
    'src/pages/Register.js',
    'src/pages/UserProfile.js',
    'src/pages/AccountCenter.js',
    'src/pages/CommunityPublish.js',
    'src/pages/CommunityPostEdit.js',
    'public/index.html',
]
root = os.path.join(os.path.dirname(__file__), '..', 'frontend')
for rel in files:
    path = os.path.join(root, rel.replace('/', os.sep))
    raw = open(path, 'rb').read()
    try:
        t = raw.decode('utf-8')
        ok = 'utf-8'
    except UnicodeDecodeError:
        try:
            t = raw.decode('gbk')
            ok = 'gbk-only'
        except UnicodeDecodeError:
            t = raw.decode('utf-8', errors='replace')
            ok = 'utf-8-replace'
    # sample chinese line
    for line in t.splitlines()[:15]:
        if any(ord(c) > 127 for c in line):
            print(rel, ok, line[:80])
            break
    else:
        print(rel, ok, 'no-cjk-in-first-15')
