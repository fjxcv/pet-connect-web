# -*- coding: utf-8 -*-
import os
root = os.path.join(os.path.dirname(__file__), '..', 'frontend', 'src', 'pages')
for fn in ['Register.js', 'ForgotPassword.js', 'UserProfile.js', 'Login.js']:
    raw = open(os.path.join(root, fn), 'rb').read()
    for enc in ('utf-8', 'gbk', 'gb18030'):
        try:
            t = raw.decode(enc)
            print(fn, enc, 'OK', 'len', len(t))
            idx = t.find('setError')
            if idx >= 0:
                print('  ', repr(t[idx:idx+60]))
            idx2 = t.find('ROLE_LABELS')
            if idx2 >= 0:
                print('  ', repr(t[idx2:idx2+120]))
            break
        except Exception as e:
            print(fn, enc, 'ERR', str(e)[:60])
