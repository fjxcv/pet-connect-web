import base64
import hashlib
import hmac
import json
import os
import ssl
import urllib.error
import urllib.request
from datetime import datetime
from time import mktime
from urllib.parse import urlencode, urlparse
from wsgiref.handlers import format_date_time


class LLMNotConfiguredError(Exception):
    pass


class LLMRequestError(Exception):
    pass


def _spark_configured():
    return all(
        os.getenv(name, '').strip()
        for name in ('SPARK_APP_ID', 'SPARK_API_KEY', 'SPARK_API_SECRET')
    )


def _spark_auth_url(api_key, api_secret, ws_url):
    parsed = urlparse(ws_url)
    host = parsed.netloc
    path = parsed.path or '/'
    date = format_date_time(mktime(datetime.now().timetuple()))
    signature_origin = f'host: {host}\ndate: {date}\nGET {path} HTTP/1.1'
    signature_sha = hmac.new(
        api_secret.encode('utf-8'),
        signature_origin.encode('utf-8'),
        digestmod=hashlib.sha256,
    ).digest()
    signature = base64.b64encode(signature_sha).decode('utf-8')
    authorization_origin = (
        f'api_key="{api_key}", algorithm="hmac-sha256", '
        f'headers="host date request-line", signature="{signature}"'
    )
    authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode('utf-8')
    return f'{ws_url}?{urlencode({"authorization": authorization, "date": date, "host": host})}'


def _normalize_messages(messages):
    normalized = []
    for item in messages:
        role = item.get('role')
        content = item.get('content')
        if isinstance(content, list):
            parts = []
            for block in content:
                if isinstance(block, dict) and block.get('type') == 'text':
                    parts.append(str(block.get('text', '')))
            content = '\n'.join(part for part in parts if part)
        if role in ('system', 'user', 'assistant') and content:
            normalized.append({'role': role, 'content': str(content)})
    return normalized


def _spark_chat_completion(messages, max_tokens=1024):
    app_id = os.getenv('SPARK_APP_ID', '').strip()
    api_key = os.getenv('SPARK_API_KEY', '').strip()
    api_secret = os.getenv('SPARK_API_SECRET', '').strip()
    ws_url = os.getenv('SPARK_WS_URL', 'wss://spark-api.xf-yun.com/x2').strip()
    domain = os.getenv('SPARK_DOMAIN', 'spark-x').strip()
    thinking_type = os.getenv('SPARK_THINKING', 'disabled').strip() or 'disabled'

    text_messages = _normalize_messages(messages)
    if not text_messages:
        raise LLMRequestError('Spark request has no valid messages')

    body = {
        'header': {
            'app_id': app_id,
            'uid': 'pawrescue',
        },
        'parameter': {
            'chat': {
                'domain': domain,
                'max_tokens': max_tokens,
                'temperature': 0.7,
                'thinking': {'type': thinking_type},
            },
        },
        'payload': {
            'message': {
                'text': text_messages,
            },
        },
    }

    auth_url = _spark_auth_url(api_key, api_secret, ws_url)
    try:
        import websocket
    except ImportError as exc:
        raise LLMNotConfiguredError(
            '\u7f3a\u5c11 websocket-client \u4f9d\u8d56\uff0c\u8bf7\u5728 backend '
            '\u865a\u62df\u73af\u5883\u4e2d\u6267\u884c: pip install websocket-client'
        ) from exc

    ws = None
    answer_parts = []
    try:
        ws = websocket.create_connection(
            auth_url,
            sslopt={'cert_reqs': ssl.CERT_NONE},
            timeout=90,
        )
        ws.send(json.dumps(body, ensure_ascii=False))
        while True:
            raw = ws.recv()
            if not raw:
                break
            data = json.loads(raw)
            header = data.get('header') or {}
            code = header.get('code', -1)
            if code != 0:
                raise LLMRequestError(
                    f'Spark WS error {code}: {header.get("message", "")}'
                )
            text_list = (data.get('payload') or {}).get('choices', {}).get('text') or []
            for item in text_list:
                content = item.get('content')
                if content:
                    answer_parts.append(content)
            if header.get('status') == 2:
                break
    except LLMRequestError:
        raise
    except Exception as exc:
        raise LLMRequestError(f'Spark WS connection error: {exc}') from exc
    finally:
        if ws is not None:
            try:
                ws.close()
            except Exception:
                pass

    answer = ''.join(answer_parts).strip()
    if not answer:
        raise LLMRequestError('Spark returned empty content')
    return answer


def _http_chat_completion(messages, max_tokens=1024):
    api_key = os.getenv('LLM_API_KEY', '').strip()
    if not api_key:
        raise LLMNotConfiguredError(
            '\u672a\u914d\u7f6e LLM\uff0c\u8bf7\u5728 backend/.env \u4e2d\u8bbe\u7f6e '
            'SPARK_APP_ID/SPARK_API_KEY/SPARK_API_SECRET \u6216 LLM_API_KEY\u3002'
        )
    base = os.getenv('LLM_API_BASE', 'https://api.openai.com/v1').rstrip('/')
    model = os.getenv('LLM_MODEL', 'gpt-4o-mini')
    url = f'{base}/chat/completions'
    payload = json.dumps({
        'model': model,
        'messages': messages,
        'max_tokens': max_tokens,
        'temperature': 0.7,
    }).encode('utf-8')
    req = urllib.request.Request(
        url,
        data=payload,
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {api_key}',
        },
        method='POST',
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            body = json.loads(resp.read().decode('utf-8'))
    except urllib.error.HTTPError as exc:
        err_body = exc.read().decode('utf-8', errors='replace')
        raise LLMRequestError(f'LLM HTTP {exc.code}: {err_body[:500]}') from exc
    except urllib.error.URLError as exc:
        raise LLMRequestError(f'LLM connection error: {exc}') from exc
    choices = body.get('choices') or []
    if not choices:
        raise LLMRequestError('LLM returned empty choices')
    content = choices[0].get('message', {}).get('content', '')
    return (content or '').strip()


def _chat_completion(messages, max_tokens=1024):
    if _spark_configured():
        return _spark_chat_completion(messages, max_tokens=max_tokens)
    return _http_chat_completion(messages, max_tokens=max_tokens)


def chat(messages, max_tokens=1024):
    return _chat_completion(messages, max_tokens=max_tokens)


def chat_vision(image_data_url: str, user_text: str, system_prompt: str, max_tokens=512):
    messages = [
        {'role': 'system', 'content': system_prompt},
        {
            'role': 'user',
            'content': [
                {'type': 'text', 'text': user_text},
                {'type': 'image_url', 'image_url': {'url': image_data_url}},
            ],
        },
    ]
    return _chat_completion(messages, max_tokens=max_tokens)
