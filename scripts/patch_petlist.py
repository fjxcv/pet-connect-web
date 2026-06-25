# -*- coding: utf-8 -*-
"""Restore PetList.js from good UTF-8 git revision and apply age-input patches."""
from __future__ import annotations

import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TARGET = os.path.join(ROOT, 'frontend', 'src', 'pages', 'PetList.js')
BASE_REV = 'eddf621'

AGE_STATE = """
  // \u672c\u5730\u8f93\u5165\u72b6\u6001\uff1a\u4ec5\u5728\u56de\u8f66\u6216\u5931\u7126\u65f6\u624d\u63d0\u4ea4\u5230\u4e0a\u9762\u7684\u7b5b\u9009\u72b6\u6001\uff0c\u907f\u514d\u6bcf\u6b21\u6309\u952e\u90fd\u89e6\u53d1 API \u8bf7\u6c42
  const [ageMinInput, setAgeMinInput] = useState(searchParams.get('age_min') || '');
  const [ageMaxInput, setAgeMaxInput] = useState(searchParams.get('age_max') || '');
"""

AGE_HANDLERS = """
  const handleCustomAgeInput = (setter) => (event) => {
    const next = event.target.value.replace(/[^\\d]/g, '');
    setter(next);
  };

  const handleConfirmAge = () => {
    setCustomAgeMin(ageMinInput);
    setCustomAgeMax(ageMaxInput);
  };
"""

CUSTOM_AGE_INPUTS = """              <>
                <div className="col-6 col-md-2">
                  <input
                    type="text"
                    inputMode="numeric"
                    pattern="[0-9]*"
                    className="form-control"
                    placeholder="\u6700\u5c0f\u6708\u9f84"
                    value={ageMinInput}
                    onChange={handleCustomAgeInput(setAgeMinInput)}
                    onKeyDown={(e) => e.key === 'Enter' && handleConfirmAge()}
                    onBlur={handleConfirmAge}
                  />
                </div>
                <div className="col-6 col-md-2">
                  <input
                    type="text"
                    inputMode="numeric"
                    pattern="[0-9]*"
                    className="form-control"
                    placeholder="\u6700\u5927\u6708\u9f84"
                    value={ageMaxInput}
                    onChange={handleCustomAgeInput(setAgeMaxInput)}
                    onKeyDown={(e) => e.key === 'Enter' && handleConfirmAge()}
                    onBlur={handleConfirmAge}
                  />
                </div>
              </>"""


def load_base() -> str:
    raw = subprocess.check_output(
        ['git', '-C', ROOT, 'show', f'{BASE_REV}:frontend/src/pages/PetList.js']
    )
    return raw.decode('utf-8')


def patch(content: str) -> str:
    needle = '.test(status)) return status;'
    idx = content.find(needle)
    if idx == -1:
        raise SystemExit('formatHealthStatus regex not found')
    start = content.rfind('if (/', 0, idx)
    if start == -1:
        raise SystemExit('formatHealthStatus regex start not found')
    end = idx + len(needle)
    content = (
        content[:start]
        + "if (/[\\u4e00-\\u9fff]/.test(status)) return status;"
        + content[end:]
    )

    marker = "  const [customAgeMax, setCustomAgeMax] = useState(searchParams.get('age_max') || '');\n"
    if marker not in content:
        raise SystemExit('customAgeMax state marker not found')
    content = content.replace(marker, marker + AGE_STATE)

    search_handler = "  const handleConfirmSearch = () => {\n    setSearch(searchText.trim());\n  };\n"
    if search_handler not in content:
        raise SystemExit('handleConfirmSearch block not found')
    content = content.replace(search_handler, search_handler + AGE_HANDLERS)

    clear_block = "    setCustomAgeMax('');\n    setNearbyMode(false);"
    if clear_block not in content:
        raise SystemExit('clearFilters block not found')
    content = content.replace(
        clear_block,
        "    setCustomAgeMax('');\n    setAgeMinInput('');\n    setAgeMaxInput('');\n    setNearbyMode(false);",
    )

    old_inputs = re.search(
        r"\) : \(\s*<>\s*<div className=\"col-6 col-md-2\">.*?onChange=\{\(e\) => setCustomAgeMax\(e\.target\.value\)\}\s*/>\s*</div>\s*</>\s*\)",
        content,
        re.S,
    )
    if not old_inputs:
        raise SystemExit('custom age input JSX not found')
    content = content[: old_inputs.start()] + ') : (\n' + CUSTOM_AGE_INPUTS + '\n            )' + content[old_inputs.end() :]

    return content


def main():
    content = patch(load_base())
    with open(TARGET, 'w', encoding='utf-8', newline='\n') as f:
        f.write(content)

    raw = open(TARGET, 'rb').read()
    assert b'\xe7\x8b\x97' in raw, 'missing dog label UTF-8'
    assert b'ageMinInput' in raw
    assert b'handleConfirmAge' in raw
    assert b'handleCustomAgeInput' in raw
    assert b'\\u4e00-\\u9fff' in raw
    print('patched', TARGET)


if __name__ == '__main__':
    main()
