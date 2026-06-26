import json
import time
from io import BytesIO
from pathlib import Path

import torch
import torch.nn.functional as F
from PIL import Image
from torchvision import models, transforms

"""
MobileNetV3 推理。
"""

ML_DIR = Path(__file__).resolve().parent.parent / 'ml'
LABELS_PATH = ML_DIR / 'breed_labels.json'
WEIGHTS_PATH = ML_DIR / 'breed_classifier.pt'

_MODEL = None
_LABELS = None
_TRANSFORM = None
_NUM_CLASSES = 37


class BreedModelNotReadyError(Exception):
    pass


def model_paths():
    return {'labels': str(LABELS_PATH), 'weights': str(WEIGHTS_PATH)}


def is_model_ready() -> bool:
    """
    功能：检查 ml/breed_classifier.pt 和 breed_labels.json 是否存在。
    返回：bool
    """
    return WEIGHTS_PATH.is_file() and LABELS_PATH.is_file()


def _load_labels():
    global _LABELS
    if _LABELS is None:
        with open(LABELS_PATH, encoding='utf-8') as f:
            _LABELS = json.load(f)
    return _LABELS


def _build_model(num_classes: int):
    model = models.mobilenet_v3_small(weights=None)
    model.classifier[3] = torch.nn.Linear(model.classifier[3].in_features, num_classes)
    return model


def _load_model():
    """
    功能：延迟加载模型与预处理组件，并在首次调用时初始化全局单例。

    说明：
    - 仅在模型权重文件和标签文件都存在时才继续加载，避免运行时找不到文件。
    - 通过全局变量缓存 `_MODEL` 和 `_TRANSFORM`，避免每次推理都重新构建模型和预处理流水线。
    - 默认将模型加载到 CPU 上，适用于没有 GPU 的部署环境。
    """
    global _MODEL, _TRANSFORM

    # 先检查模型权重和标签文件是否已经准备好
    if not is_model_ready():
        raise BreedModelNotReadyError(
            'Breed model weights not found. Run: backend\\venv\\Scripts\\python.exe scripts\\train_breed_model.py'
        )

    # 如果已经初始化过，就直接复用缓存的模型和 transform
    if _MODEL is None:
        # 1) 读取标签 JSON，确定类别数量并给后续结果做映射
        labels = _load_labels()
        num_classes = len(labels)

        # 2) 构造 MobileNetV3-Small 模型结构
        _MODEL = _build_model(num_classes)

        # 3) 加载本地权重文件到 CPU，避免 GPU 依赖
        state = torch.load(WEIGHTS_PATH, map_location='cpu')
        _MODEL.load_state_dict(state)

        # 4) 将模型切换为评估模式，禁用 dropout / batchnorm 训练行为
        _MODEL.eval()

        # 5) 构建与训练数据一致的图像预处理流水线
        #    包括缩放、中心裁剪、张量化、以及 ImageNet 归一化
        _TRANSFORM = transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225],
            ),
        ])

    return _MODEL, _TRANSFORM


def predict_breeds(image_bytes: bytes, top_k: int = 4) -> list[dict]:
    """
    功能：MobileNetV3-Small CNN 推理，返回 Top-K 品种（breed_classifier 核心）。
    参数：image_bytes, top_k
    返回：(results_list, elapsed_ms)
    答辩重点：本地模型、无需外网、37 类中文标签
    """
    # 1) 加载标签映射（索引 -> 标签字典），标签文件为 JSON，包含中文名/英文名/物种等
    labels = _load_labels()

    # 2) 延迟加载模型和预处理 transform（单例），若模型文件或标签不存在会抛错
    model, transform = _load_model()

    # 3) 将输入的二进制图片转换为 PIL.Image 并统一为 RGB
    # 将 bytes 包装成文件对象以便 PIL 读取
    image = Image.open(BytesIO(image_bytes)).convert('RGB')

    # 4) 应用与训练时一致的预处理（Resize/CenterCrop/ToTensor/Normalize）
    # transform 返回 shape 为 [C, H, W] 的 tensor，unsqueeze(0)在batch维度上增加一维，变为 [1, C, H, W]
    tensor = transform(image).unsqueeze(0)

    # 5) 记录开始时间用于测量纯推理耗时（不含前处理与后处理）
    started = time.perf_counter()

    # 6) 关闭梯度计算以加速推理并节省内存（推理阶段不需要反向传播）
    with torch.no_grad():
        # 前向计算 logits（未归一化分数），shape 为 [1, num_classes]
        logits = model(tensor)
        # 使用 softmax 将 logits 转为概率分布，取 batch 第0个样本
        probs = F.softmax(logits, dim=1)[0]

    # 7) 计算推理耗时（毫秒），仅度量模型前向的时间段
    elapsed_ms = int((time.perf_counter() - started) * 1000)

    # 8) 选择实际返回的候选数（不超过标签总数和请求的 top_k）
    k = min(top_k, len(labels))
    # topk 返回概率与对应索引（按概率降序）
    top_probs, top_idx = probs.topk(k)

    # 9) 构建返回结果列表：将索引映射为标签字典，并格式化每项字段
    results = []
    # top_probs/top_idx 转为 Python 列表以便迭代并兼容序列化
    for prob, idx in zip(top_probs.tolist(), top_idx.tolist()):
        item = labels[idx]
        # 返回字段：中文名 `breed`、所属物种 `species`、置信度 `confidence`（四舍五入到 2 位小数）、英文名 `en`
        results.append({
            'breed': item['zh'],
            'species': item['species'],
            'confidence': round(float(prob), 2),
            'en': item.get('en'),
        })

    # 10) 返回 Top-K 列表和模型推理耗时（ms），上层会根据置信度进一步判断是否 low_confidence
    return results, elapsed_ms
