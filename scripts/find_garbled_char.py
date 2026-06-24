# -*- coding: utf-8 -*-
import re
GARBLED = re.compile(r'[\u9422\u7035\u93da\u7487\u5a09\u7ba0\u9550\u9352\u8e48\u6769\u6960\u9350\u7f51\u3220\u6f58]')
for f in ['frontend/src/pages/Register.js', 'frontend/src/pages/CommunityPublish.js', 'frontend/src/pages/CommunityPostEdit.js']:
    t = open(f, encoding='utf-8').read()
    for m in GARBLED.finditer(t):
        i = m.start()
        print(f, 'U+%04X' % ord(m.group()), repr(t[max(0,i-30):i+30]))
