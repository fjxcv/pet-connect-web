"""
AI 图片加载。
"""

import base64
import io
import os
import urllib.error
import urllib.request
from urllib.parse import urlparse

from django.conf import settings
from PIL import Image


class ImageLoadError(Exception):
    pass


def _guess_ext(mime: str) -> str:
    return {
        'image/jpeg': '.jpg',
        'image/png': '.png',
        'image/webp': '.webp',
        'image/gif': '.gif',
        'image/bmp': '.bmp',
    }.get(mime, '.jpg')


def _bytes_to_data_url(image_bytes: bytes, mime: str = 'image/jpeg') -> str:
    encoded = base64.b64encode(image_bytes).decode('ascii')
    return f'data:{mime};base64,{encoded}'


def _compress_image_bytes(image_bytes: bytes, max_bytes: int = 750_000) -> tuple[bytes, str]:
    if len(image_bytes) <= max_bytes:
        mime = 'image/jpeg'
        try:
            with Image.open(io.BytesIO(image_bytes)) as img:
                fmt = (img.format or 'JPEG').upper()
                if fmt == 'PNG':
                    mime = 'image/png'
        except Exception:
            pass
        return image_bytes, mime

    with Image.open(io.BytesIO(image_bytes)) as img:
        img = img.convert('RGB')
        quality = 85
        while quality >= 40:
            buf = io.BytesIO()
            img.save(buf, format='JPEG', quality=quality, optimize=True)
            data = buf.getvalue()
            if len(data) <= max_bytes:
                return data, 'image/jpeg'
            quality -= 10
        w, h = img.size
        img = img.resize((max(1, int(w * 0.7)), max(1, int(h * 0.7))), Image.Resampling.LANCZOS)
        buf = io.BytesIO()
        img.save(buf, format='JPEG', quality=75, optimize=True)
        return buf.getvalue(), 'image/jpeg'


def _load_from_base64(image_base64: str) -> tuple[bytes, str, str]:
    """
    功能：解析 base64（支持 data: 前缀），压缩后返回 bytes/mime/filename。
    """
    raw = image_base64.strip()
    mime = 'image/jpeg'
    if raw.startswith('data:'):
        header, _, payload = raw.partition(',')
        if ';base64' in header:
            mime = header[5:].split(';')[0] or mime
        raw = payload
    try:
        image_bytes = base64.b64decode(raw, validate=False)
    except Exception as exc:
        raise ImageLoadError('Invalid base64 image data') from exc
    if not image_bytes:
        raise ImageLoadError('Empty image data')
    image_bytes, mime = _compress_image_bytes(image_bytes)
    filename = f'upload{_guess_ext(mime)}'
    return image_bytes, mime, filename


def _media_relative_path(url_path: str) -> str | None:
    media_prefix = settings.MEDIA_URL
    if not media_prefix.startswith('/'):
        media_prefix = '/' + media_prefix
    if url_path.startswith(media_prefix):
        return url_path[len(media_prefix):].lstrip('/')
    if url_path.startswith('/media/'):
        return url_path[len('/media/'):]
    return None


def _load_from_url(image_url: str, request=None) -> tuple[bytes, str, str]:
    """
    功能：支持 MEDIA 本地文件直读 + 外网 URL 下载（避免 localhost 给云 API 用）。
    """
    parsed = urlparse(image_url.strip())
    if not parsed.scheme and not parsed.path:
        raise ImageLoadError('image_url is required')

    rel = _media_relative_path(parsed.path)
    if rel:
        filepath = os.path.join(settings.MEDIA_ROOT, rel)
        if os.path.isfile(filepath):
            with open(filepath, 'rb') as fh:
                image_bytes = fh.read()
            ext = os.path.splitext(filepath)[1].lower()
            mime = {
                '.jpg': 'image/jpeg',
                '.jpeg': 'image/jpeg',
                '.png': 'image/png',
                '.webp': 'image/webp',
                '.gif': 'image/gif',
            }.get(ext, 'image/jpeg')
            image_bytes, mime = _compress_image_bytes(image_bytes)
            return image_bytes, mime, os.path.basename(filepath)
        raise ImageLoadError(f'Image file not found on server: {rel}')

    host = (parsed.hostname or '').lower()
    if host in ('localhost', '127.0.0.1', '0.0.0.0') and not rel:
        raise ImageLoadError(
            'Local image URL is not reachable by cloud APIs. Re-upload the image or use site media URL.'
        )

    req = urllib.request.Request(
        image_url,
        headers={'User-Agent': 'PawRescue/1.0'},
    )
    try:
        with urllib.request.urlopen(req, timeout=25) as resp:
            image_bytes = resp.read()
            mime = resp.headers.get_content_type() or 'image/jpeg'
    except urllib.error.URLError as exc:
        raise ImageLoadError(f'Failed to download image: {exc}') from exc

    if not image_bytes:
        raise ImageLoadError('Downloaded image is empty')
    filename = os.path.basename(parsed.path) or f'image{_guess_ext(mime)}'
    image_bytes, mime = _compress_image_bytes(image_bytes)
    return image_bytes, mime, filename


def load_image_for_ai(*, image_url: str = '', image_base64: str = '', request=None) -> dict:
    """
    功能：统一图片加载入口（base64 优先，URL 次之），返回 bytes + data_url 供 CNN/LLM。
    参数：image_url / image_base64 / request
    返回：dict（bytes, mime, filename, data_url）
    【权限】user/admin（breed_detect / AddPet 调用）
    """
    if image_base64:
        image_bytes, mime, filename = _load_from_base64(image_base64)
    elif image_url:
        image_bytes, mime, filename = _load_from_url(image_url, request=request)
    else:
        raise ImageLoadError('Provide image_url or image_base64')

    return {
        'bytes': image_bytes,
        'mime': mime,
        'filename': filename,
        'data_url': _bytes_to_data_url(image_bytes, mime),
    }
