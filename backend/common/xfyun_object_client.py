"""
模块说明：源码：backend/common/xfyun_object_client.py
"""

import base64
import hashlib
import json
import os
import time
import urllib.error
import urllib.request

class XfyunObjectNotConfiguredError(Exception):
    pass

class XfyunObjectRequestError(Exception):
    pass

def _is_configured() -> bool:
    return bool(
        os.getenv('XFYUN_OBJECT_API_KEY', '').strip()
        and os.getenv('XFYUN_OBJECT_APP_ID', '').strip()
    )

def recognize_object(image_bytes: bytes, image_name: str, *, image_url: str = '') -> list[dict]:
    app_id = os.getenv('XFYUN_OBJECT_APP_ID', '').strip()
    api_key = os.getenv('XFYUN_OBJECT_API_KEY', '').strip()
    api_url = os.getenv(
        'XFYUN_OBJECT_API_URL',
        'http://tupapi.xfyun.cn/v1/currency',
    ).strip()
    if not app_id or not api_key:
        raise XfyunObjectNotConfiguredError(
            'XFYUN_OBJECT_APP_ID / XFYUN_OBJECT_API_KEY not configured in backend/.env'
        )
    param = {'image_name': image_name or 'image.jpg'}
    if image_url:
        param['image_url'] = image_url
    x_param = base64.b64encode(
        json.dumps(param, ensure_ascii=False).encode('utf-8')
    ).decode('ascii')
    cur_time = str(int(time.time()))
    checksum = hashlib.md5(
        (api_key + cur_time + x_param).encode('utf-8')
    ).hexdigest()
    headers = {
        'X-Appid': app_id,
        'X-CurTime': cur_time,
        'X-Param': x_param,
        'X-CheckSum': checksum,
    }
    body = b'' if image_url else image_bytes
    req = urllib.request.Request(api_url, data=body, headers=headers, method='POST')
    try:
        with urllib.request.urlopen(req, timeout=8) as resp:
            payload = json.loads(resp.read().decode('utf-8'))
    except urllib.error.HTTPError as exc:
        err = exc.read().decode('utf-8', errors='replace')
        raise XfyunObjectRequestError(f'Xfyun object HTTP {exc.code}: {err[:400]}') from exc
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        raise XfyunObjectRequestError(f'Xfyun object connection error: {exc}') from exc
    if str(payload.get('code')) != '0':
        raise XfyunObjectRequestError(
            f"Xfyun object error {payload.get('code')}: {payload.get('desc', '')}"
        )
    items = []
    for row in payload.get('data') or []:
        labels = row.get('labels') or []
        rates = row.get('rates') or []
        for idx, label in enumerate(labels[:5]):
            rate = rates[idx] if idx < len(rates) else row.get('rate')
            items.append({
                'label': label,
                'rate': float(rate) if rate is not None else 0.0,
            })
        if not items and row.get('label', -1) >= 0:
            items.append({
                'label': row.get('label'),
                'rate': float(row.get('rate') or 0),
            })
        break
    return items

