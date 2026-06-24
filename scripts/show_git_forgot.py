# -*- coding: utf-8 -*-
import subprocess
lines = subprocess.check_output(['git', 'show', 'HEAD:frontend/src/pages/ForgotPassword.js']).split(b'\n')
for line in lines:
    if b'setMessage' in line and b'useState' not in line and line.strip() != b"setMessage('');":
        print(line)
