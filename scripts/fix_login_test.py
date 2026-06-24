# -*- coding: utf-8 -*-
import os
path = os.path.join(os.path.dirname(__file__), '..', 'frontend', 'src', 'pages', 'Login.js')
with open(path, 'r', encoding='utf-8') as f:
    original = f.read()
print('has 9422:', '\u9422' in original)
print('sample:', repr(original[900:950]))
try:
    fixed = original.encode('gbk').decode('utf-8')
    print('fixed sample:', repr(fixed[900:950]))
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(fixed)
    print('OK')
except Exception as e:
    print('FAIL', e)
