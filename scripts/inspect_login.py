# -*- coding: utf-8 -*-
import os
path = os.path.join(os.path.dirname(__file__), '..', 'frontend', 'src', 'pages', 'Login.js')
raw = open(path, 'rb').read()
idx = raw.find(b'setError')
print('first setError at', idx)
print(raw[idx:idx+120])
# try decode whole file as utf-8
try:
    t = raw.decode('utf-8')
    print('utf-8 ok, len', len(t))
except UnicodeDecodeError as e:
    print('utf-8 err', e)
# find non-utf8 regions
i = 0
while i < len(raw):
    try:
        raw[i:i+1].decode('utf-8')
        i += 1
    except:
        pass
# show line 31 area
lines = raw.split(b'\n')
for n, line in enumerate(lines[29:35], 30):
    print(n, line[:100])
