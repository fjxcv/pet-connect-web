# -*- coding: utf-8 -*-
"""Write frontend/src/constants/site.js as valid UTF-8 using unicode escapes."""
from __future__ import annotations

import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PATH = os.path.join(ROOT, 'frontend', 'src', 'constants', 'site.js')

CONTENT = f"""export const SITE_NAME = '{chr(0x6696)}{chr(0x722a)}{chr(0x6551)}{chr(0x52a9)}';

export const ADOPTION_STATUS = {{available:'{chr(0x53ef)}{chr(0x9886)}{chr(0x517b)}',pending:'{chr(0x7533)}{chr(0x8bf7)}{chr(0x4e2d)}',adopted:'{chr(0x5df2)}{chr(0x9886)}{chr(0x517b)}'}};
export const ONLINE_STATUS = {{pending:'{chr(0x5f85)}{chr(0x5ba1)}{chr(0x6838)}',approved:'{chr(0x5df2)}{chr(0x901a)}{chr(0x8fc7)}',rejected:'{chr(0x5df2)}{chr(0x62d2)}{chr(0x7edd)}',need_material:'{chr(0x9700)}{chr(0x8865)}{chr(0x6750)}{chr(0x6599)}'}};
export const ARTICLE_TYPES = {{science:'{chr(0x79d1)}{chr(0x666e)}',announcement:'{chr(0x516c)}{chr(0x544a)}',law:'{chr(0x6cd5)}{chr(0x89c4)}',rescue_case:'{chr(0x6551)}{chr(0x52a9)}{chr(0x6848)}{chr(0x4f8b)}'}};
export const POST_CATEGORIES = {{general:'{chr(0x7efc)}{chr(0x5408)}{chr(0x8ba8)}{chr(0x8bba)}',rescue_share:'{chr(0x6551)}{chr(0x52a9)}{chr(0x5206)}{chr(0x4eab)}',help_request:'{chr(0x6c42)}{chr(0x52a9)}{chr(0x63d0)}{chr(0x95ee)}',pet_experience:'{chr(0x517b)}{chr(0x5ba0)}{chr(0x7ecf)}{chr(0x9a8c)}'}};
export const LOST_FOUND_TYPE = {{lost:'{chr(0x5bfb)}{chr(0x5ba0)}',found:'{chr(0x62db)}{chr(0x9886)}'}};
export const LOST_FOUND_STATUS = {{searching:'{chr(0x5bfb)}{chr(0x627e)}{chr(0x4e2d)}',found:'{chr(0x5df2)}{chr(0x627e)}{chr(0x5230)}',cancelled:'{chr(0x5df2)}{chr(0x53d6)}{chr(0x6d88)}'}};
export const RESCUE_STATUS = {{pending_rescue:'{chr(0x5f85)}{chr(0x6551)}{chr(0x52a9)}',in_medical:'{chr(0x533b)}{chr(0x7597)}{chr(0x4e2d)}',recovering:'{chr(0x6062)}{chr(0x590d)}{chr(0x4e2d)}',awaiting_adoption:'{chr(0x5f85)}{chr(0x9886)}{chr(0x517b)}',rescued:'{chr(0x6551)}{chr(0x52a9)}{chr(0x6210)}{chr(0x529f)}',abandoned:'{chr(0x5df2)}{chr(0x7ec8)}{chr(0x6b62)}'}};
export const SIZE_CATEGORY = {{small:'{chr(0x5c0f)}{chr(0x578b)}',medium:'{chr(0x4e2d)}{chr(0x578b)}',large:'{chr(0x5927)}{chr(0x578b)}'}};
export const HEALTH_STATUS = {{healthy:'{chr(0x5065)}{chr(0x5eb7)}',minor_injury:'{chr(0x8f7b)}{chr(0x5fae)}{chr(0x4f24)}{chr(0x75c5)}',severe_injury:'{chr(0x4e25)}{chr(0x91cd)}{chr(0x4f24)}{chr(0x75c5)}'}};
"""


def main():
    open(PATH, 'w', encoding='utf-8', newline='\n').write(CONTENT)
    raw = open(PATH, 'rb').read()
    assert b'\xe6\x9a\x96\xe7\x88\xaa\xe6\x95\x91\xe5\x8a\xa9' in raw
    assert b'\xe5\xbe\x85\xe5\xae\xa1\xe6\xa0\xb8' in raw
    print('wrote', PATH)


if __name__ == '__main__':
    main()
