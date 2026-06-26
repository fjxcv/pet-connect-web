"""
LLM 封装模块。

此模块提供统一的对话能力入口，支持讯飞星火 Spark WebSocket 方式和 OpenAI 兼容的 HTTP 方式。
视图层负责 AI 配额、身份权限和调用日志，这里只负责将消息发送到可用的 LLM 后端并返回文本结果。
"""

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
    """
    功能：检查 .env 是否配置了讯飞星火（Spark）三要素。
    返回：bool
    """
    return all(
        os.getenv(name, '').strip()
        for name in ('SPARK_APP_ID', 'SPARK_API_KEY', 'SPARK_API_SECRET')
    )


def _spark_auth_url(api_key, api_secret, ws_url):
    """
    功能：生成讯飞星火 WebSocket 鉴权 URL（HMAC-SHA256 签名）。
    参数：api_key, api_secret, ws_url
    返回：带 authorization 的完整 URL
    """
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
    """
    功能：将多模态 messages 规范化为纯文本 role/content 列表（兼容 vision）。
    参数：messages — OpenAI 格式消息列表
    返回：规范化后的列表
    """
    normalized = []
    for item in messages:
        role = item.get('role')
        content = item.get('content')
        # 如果当前消息使用多模态形式（例如 chat_vision），只提取 text 块内容
        if isinstance(content, list):
            parts = []
            for block in content:
                if isinstance(block, dict) and block.get('type') == 'text':
                    parts.append(str(block.get('text', '')))
            content = '\n'.join(part for part in parts if part)
        # 仅保留 system/user/assistant 角色且非空内容
        if role in ('system', 'user', 'assistant') and content:
            normalized.append({'role': role, 'content': str(content)})
    return normalized


def _spark_chat_completion(messages, max_tokens=1024):
    """
    功能：通过讯飞星火 WebSocket 完成对话（支持 thinking 参数）。
    参数：messages, max_tokens
    返回：assistant 回复文本
    【权限】user/admin（经 chat 入口）
    """
    app_id = os.getenv('SPARK_APP_ID', '').strip()
    api_key = os.getenv('SPARK_API_KEY', '').strip()
    api_secret = os.getenv('SPARK_API_SECRET', '').strip()
    ws_url = os.getenv('SPARK_WS_URL', 'wss://spark-api.xf-yun.com/x2').strip()
    domain = os.getenv('SPARK_DOMAIN', 'spark-x').strip()
    thinking_type = os.getenv('SPARK_THINKING', 'disabled').strip() or 'disabled'

    # 将 OpenAI 格式消息转换成 Spark WebSocket 可识别的纯文本消息列表
    text_messages = _normalize_messages(messages)
    if not text_messages:
        raise LLMRequestError('Spark request has no valid messages')

    # 构造 Spark WebSocket 请求体，包含会话参数、模型配置和消息负载
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

    # 生成 Spark WebSocket 鉴权 URL，包含 authorization/date/host 参数
    auth_url = _spark_auth_url(api_key, api_secret, ws_url)
    try:
        import websocket
    except ImportError as exc:
        raise LLMNotConfiguredError(
            '缺少 websocket-client 依赖，请在 backend 虚拟环境中执行: pip install websocket-client'
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
    """
    功能：通过 OpenAI 兼容 HTTP 接口完成对话（.env LLM_API_KEY）。
    参数：messages, max_tokens
    返回：assistant 回复文本
    """
    # 如果没有配置 Spark，则走 OpenAI 兼容的 HTTP 接口
    api_key = os.getenv('LLM_API_KEY', '').strip()
    if not api_key:
        raise LLMNotConfiguredError(
            '未配置 LLM，请在 backend/.env 中设置 SPARK_APP_ID/SPARK_API_KEY/SPARK_API_SECRET 或 LLM_API_KEY。'
        )
    base = os.getenv('LLM_API_BASE', 'https://api.openai.com/v1').rstrip('/')
    model = os.getenv('LLM_MODEL', 'gpt-4o-mini')
    url = f'{base}/chat/completions'
    # 构造 OpenAI 风格的请求体
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
    """
    功能：统一入口，优先 Spark，否则走 HTTP。
    参数：messages, max_tokens
    返回：文本回复
    """
    if _spark_configured():
        return _spark_chat_completion(messages, max_tokens=max_tokens)
    return _http_chat_completion(messages, max_tokens=max_tokens)


def chat(messages, max_tokens=1024):
    """
    功能：对外暴露的对话入口（breed 文案、问答等调用）。
    参数：messages（OpenAI 格式）, max_tokens
    返回：str — assistant 内容
    【权限】user/admin（配额检查在视图层）
    """
    return _chat_completion(messages, max_tokens=max_tokens)


def chat_vision(image_data_url: str, user_text: str, system_prompt: str, max_tokens=512):
    """
    功能：多模态 vision 调用（当前 breed_detect 未启用，仅预留）。
    参数：image_data_url, user_text, system_prompt, max_tokens
    返回：str
    【权限】user/admin
    """
    # 组装多模态消息：system 指令 + user 内容块，包含文字和图片 URL
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
