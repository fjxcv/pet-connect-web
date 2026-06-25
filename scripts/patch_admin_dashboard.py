# -*- coding: utf-8 -*-
"""Apply AdminDashboard user-management patch without corrupting UTF-8."""
from __future__ import annotations

import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PATH = os.path.join(ROOT, 'frontend', 'src', 'pages', 'AdminDashboard.js')

FAIL = '\u66f4\u65b0\u5931\u8d25'
SET_ADMIN = '\u8bbe\u4e3a\u7ba1\u7406\u5458'
IS_ADMIN = '\u5df2\u4e3a\u7ba1\u7406\u5458'

OLD_HANDLE = (
    "  const handleUserUpdate = async (userId, data) => {\n"
    "    try {\n"
    "      await adminAPI.updateUser(userId, data);\n"
    "      loadTabData('users');\n"
    "    } catch (err) {\n"
    "      alert('\u66f4\u65b0\u5931\u8d25');\n"
    "      console.error(err);\n"
    "    }\n"
    "  };"
)

NEW_HANDLE = (
    "  const handleUserUpdate = async (userId, data) => {\n"
    "    try {\n"
    "      const res = await adminAPI.updateUser(userId, data);\n"
    "      setUsers((prev) => prev.map((u) => (u.id === userId ? res.data : u)));\n"
    "    } catch (err) {\n"
    f"      alert(getApiError(err) || '{FAIL}');\n"
    "      console.error(err);\n"
    "    }\n"
    "  };"
)

OLD_BUTTON = (
    "                  <button type=\"button\" className=\"btn btn-outline-primary\" "
    "onClick={() => handleUserUpdate(user.id, { role: 'admin' })}>"
    f"{SET_ADMIN}</button>"
)

NEW_BUTTON = (
    "                  <button\n"
    "                    type=\"button\"\n"
    "                    className=\"btn btn-outline-primary\"\n"
    "                    disabled={user.profile?.role === 'admin'}\n"
    "                    onClick={() => handleUserUpdate(user.id, { role: 'admin' })}\n"
    "                  >\n"
    f"                    {{user.profile?.role === 'admin' ? '{IS_ADMIN}' : '{SET_ADMIN}'}}\n"
    "                  </button>"
)


def main():
    text = open(PATH, 'r', encoding='utf-8').read()
    changed = False
    if OLD_HANDLE in text:
        text = text.replace(OLD_HANDLE, NEW_HANDLE, 1)
        changed = True
    if OLD_BUTTON in text:
        text = text.replace(OLD_BUTTON, NEW_BUTTON, 1)
        changed = True
    if not changed:
        print('already patched', PATH)
        return
    open(PATH, 'w', encoding='utf-8', newline='\n').write(text)
    raw = open(PATH, 'rb').read()
    assert b'\xe7\x94\xa8\xe6\x88\xb7\xe7\xae\xa1\xe7\x90\x86' in raw
    assert IS_ADMIN.encode('utf-8') in raw
    print('patched', PATH)


if __name__ == '__main__':
    main()
