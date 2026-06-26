import json
import time

"""
品种识别编排。
"""

from common.breed_classifier import BreedModelNotReadyError, is_model_ready, model_paths, predict_breeds
from common.image_loader import load_image_for_ai

_LOW_CONFIDENCE_THRESHOLD = 0.35
_UNCERTAIN = '不确定'
_NONE = '无'


def _fallback_breeds_for_species(species: str) -> list[dict]:
    """
    功能：模型未就绪或置信度低时，返回物种默认候选品种。
    参数：species — 物种（猫/狗）
    返回：list[dict] — breed, confidence
    """
    s = (species or '').strip()
    if '猫' in s:
        return [
            {'breed': '中华田园猫', 'confidence': 0.45},
            {'breed': '混血个体（品种待确认）', 'confidence': 0.35},
        ]
    if '狗' in s:
        return [
            {'breed': '中华田园犬', 'confidence': 0.45},
            {'breed': '混血个体（品种待确认）', 'confidence': 0.35},
        ]
    return [
        {'breed': '混血个体（品种待确认）', 'confidence': 0.45},
        {'breed': '品种待进一步确认', 'confidence': 0.35},
    ]


def _ensure_breed_candidates(species: str, candidates: list[dict]) -> tuple[list[dict], bool]:
    """
    功能：合并 CNN 结果与 fallback，保证至少 2 个候选，置信度低时标记 low_confidence。
    参数：species, candidates
    返回：(merged_candidates, low_confidence_flag)
    """
    fallbacks = _fallback_breeds_for_species(species)
    if not candidates:
        return fallbacks[:2], True

    max_conf = max(c['confidence'] for c in candidates)
    if max_conf >= _LOW_CONFIDENCE_THRESHOLD:
        return candidates[:4], False

    primary = fallbacks[0]
    merged = [primary]
    for item in candidates:
        if item['breed'] != primary['breed']:
            merged.append(item)
    if len(merged) < 2 and len(fallbacks) > 1:
        secondary = fallbacks[1]
        if secondary['breed'] not in {m['breed'] for m in merged}:
            merged.append(secondary)
    return merged[:4], True


def _build_result_text(species: str, candidates: list[dict]) -> str:
    """
    功能：生成前端展示的推荐文本（Top1 + 置信度）。
    参数：species, candidates
    返回：str
    """
    if not candidates:
        return f'物种：{species}' if species else ''
    top = candidates[0]
    pct = int(top['confidence'] * 100)
    return f"推荐品种：{top['breed']}（置信度约 {pct}%）"


def _predictions_to_payload(predictions: list[dict]) -> dict:
    """
    功能：将 CNN Top-K 结果转换为统一 payload（含 low_confidence 标记）。
    参数：predictions — breed_classifier 返回的 list
    返回：dict（species/breed/breed_candidates/low_confidence 等）
    """
    if not predictions:
        species = _UNCERTAIN
        candidates, low_confidence = _ensure_breed_candidates(species, [])
    else:
        species_counts = {}
        for item in predictions:
            species_counts[item['species']] = species_counts.get(item['species'], 0) + item['confidence']
        species = max(species_counts, key=species_counts.get) if species_counts else _UNCERTAIN

        seen = set()
        candidates = []
        for item in predictions:
            key = item['breed']
            if key in seen:
                continue
            seen.add(key)
            candidates.append({'breed': item['breed'], 'confidence': item['confidence']})
        candidates, low_confidence = _ensure_breed_candidates(species, candidates)

    breed = candidates[0]['breed'] if candidates else _UNCERTAIN
    result_text = _build_result_text(species, candidates)

    return {
        'species': species,
        'breed': breed,
        'summary': '',
        'result': result_text,
        'breed_candidates': candidates,
        'low_confidence': low_confidence,
        'confidence': candidates[0]['confidence'] if candidates else 0.0,
    }


def detect_pet_breed(*, image_url: str = '', image_base64: str = '', description: str = '', request=None) -> dict:
    """
    功能：品种识别主流程（AddPet 调用）。
    1. 检查模型就绪 → 2. 加载图片 → 3. CNN 推理 → 4. 组装 payload
    参数：image_url / image_base64 / description / request
    返回：dict（result/breed/species/breed_candidates/low_confidence/debug_meta）
    【权限】user/admin（经 aiAPI.breedDetect）
    """
    if not is_model_ready():
        paths = model_paths()
        raise BreedModelNotReadyError(
            f'本地品种模型未就绪。请在项目根目录执行：'
            f'backend\\venv\\Scripts\\python.exe scripts\\download_breed_model.py'
            f'（或 scripts\\train_breed_model.py）。权重路径：{paths["weights"]}'
        )

    image = load_image_for_ai(
        image_url=image_url,
        image_base64=image_base64,
        request=request,
    )

    started = time.perf_counter()
    predictions, infer_ms = predict_breeds(image['bytes'], top_k=4)
    formatted = _predictions_to_payload(predictions)

    return {
        'result': formatted['result'],
        'breed': formatted['breed'],
        'species': formatted['species'],
        'summary': formatted['summary'],
        'breed_candidates': formatted['breed_candidates'],
        'low_confidence': formatted['low_confidence'],
        'confidence': formatted['confidence'],
        'vision_used': False,
        'model_source': 'local_cnn',
        'object_recognition': False,
        'object_labels': [],
        'object_error': '',
        'debug_meta': json.dumps({
            'filename': image['filename'],
            'bytes': len(image['bytes']),
            'infer_ms': infer_ms,
            'total_ms': int((time.perf_counter() - started) * 1000),
            'description': (description or '')[:80],
        }, ensure_ascii=False),
    }
