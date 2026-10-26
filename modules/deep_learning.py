"""
深度学习算法模块 - 基于卷积神经网络的图像理解与生成

提供四类深度学习算法（统一签名 (image: BGR ndarray, params: dict) -> BGR ndarray）：
  1. image_classification  - 图像分类 (MobileNetV2, ImageNet 预训练)
  2. semantic_segmentation - 语义分割 (DeepLabV3, COCO 预训练)
  3. super_resolution       - 图像超分辨率 (SRCNN, 需先运行训练脚本)
  4. cifar10_classification - CIFAR-10 分类 (自定义 CIFAR10Net, 需先运行训练脚本)

设计要点：
  - 预训练模型通过 st.cache_resource 常驻内存，避免每次交互重复加载；
  - 需本地权重的算法（SRCNN / CIFAR10Net）在权重缺失时抛出带操作指引的异常，
    由 app.py 捕获并以 st.error 呈现；
  - 模型结构与标签常量见 modules.dl_models。
"""

import os
import urllib.request

import numpy as np
import cv2
import torch
import torch.nn.functional as F
import streamlit as st
from PIL import Image

from utils.image_io import to_grayscale, ensure_3channel
from modules.dl_models import (
    SRCNN, CIFAR10Net,
    VOC_CLASSES, VOC_PALETTE, CIFAR10_CLASSES,
    IMAGENET_MEAN, IMAGENET_STD, CIFAR10_MEAN, CIFAR10_STD,
    MODELS_DIR, DATA_DIR,
)

# ==================== 设备与标签 ====================

def _get_device():
    return torch.device("cuda" if torch.cuda.is_available() else "cpu")


_IMAGENET_URL = "https://raw.githubusercontent.com/pytorch/hub/master/imagenet_classes.txt"
_IMAGENET_CACHE = os.path.join(DATA_DIR, "imagenet_classes.txt")


def _load_imagenet_classes():
    """加载 ImageNet 1000 类名；本地缓存失败时尝试下载，仍失败则返回 None。"""
    if os.path.exists(_IMAGENET_CACHE):
        with open(_IMAGENET_CACHE, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip()]
    try:
        os.makedirs(DATA_DIR, exist_ok=True)
        urllib.request.urlretrieve(_IMAGENET_URL, _IMAGENET_CACHE)
        with open(_IMAGENET_CACHE, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip()]
    except Exception:
        return None

def _label_of(idx, classes):
    if classes is not None and 0 <= idx < len(classes):
        return classes[idx]
    return f"class {idx}"

# ==================== 模型加载（st.cache_resource 常驻内存） ====================

@st.cache_resource(show_spinner=False)
def _load_classifier():
    from torchvision import models
    device = _get_device()
    weights = models.MobileNet_V2_Weights.DEFAULT
    return models.mobilenet_v2(weights=weights).to(device).eval()

@st.cache_resource(show_spinner=False)
def _load_segmenter():
    from torchvision.models.segmentation import (
        deeplabv3_mobilenet_v3_large,
        DeepLabV3_MobileNet_V3_Large_Weights,
    )
    device = _get_device()
    weights = DeepLabV3_MobileNet_V3_Large_Weights.DEFAULT
    return deeplabv3_mobilenet_v3_large(weights=weights).to(device).eval()

@st.cache_resource(show_spinner=False)
def _load_srcnn(checkpoint: str):
    model = SRCNN().to(_get_device())
    model.load_state_dict(torch.load(checkpoint, map_location=_get_device()))
    return model.eval()

@st.cache_resource(show_spinner=False)
def _load_cifar10_model(checkpoint: str):
    model = CIFAR10Net(num_classes=10).to(_get_device())
    model.load_state_dict(torch.load(checkpoint, map_location=_get_device()))
    return model.eval()

def _require_checkpoint(filename: str, tip: str):
    """检查本地训练权重是否存在，缺失则抛出带指引的异常。"""
    path = os.path.join(MODELS_DIR, filename)
    if not os.path.exists(path):
        # 任务名由权重文件名推断：srcnn.pth -> srcnn，cifar10_cnn.pth -> cifar10
        task = "srcnn" if filename.startswith("srcnn") else "cifar10"
        raise RuntimeError(
            f"缺少训练权重 {filename}。请在项目根目录用项目环境运行：\n"
            f"  .venv\\Scripts\\python.exe -m modules.training --task {task}\n"
            f"（{tip}。首次运行需联网下载 CIFAR-10 数据集约 170MB 至 .datasets/；"
            f"必须使用 .venv 环境的解释器，系统 Python 未安装 torch）"
        )
    return path

# ==================== 预处理辅助 ====================

def _preprocess_imagenet(rgb: np.ndarray, size: int, device) -> torch.Tensor:
    """ImageNet 风格预处理：缩放 → 归一化 → 转 (1,3,H,W) 张量。"""
    img = Image.fromarray(rgb).resize((size, size), Image.BILINEAR)
    arr = np.asarray(img, dtype=np.float32) / 255.0
    arr = (arr - np.array(IMAGENET_MEAN, dtype=np.float32)) / np.array(IMAGENET_STD, dtype=np.float32)
    return torch.from_numpy(arr).permute(2, 0, 1).unsqueeze(0).to(device)

def _render_topk(image: np.ndarray, labels, probs) -> np.ndarray:
    """在图像下方绘制 Top-K 分类结果（标签 + 置信度柱状条），返回 BGR 图像。"""
    h, w = image.shape[:2]
    n = len(labels)
    panel_h = 34 * n + 48
    panel_w = max(w, 480)
    canvas = np.full((h + panel_h, panel_w, 3), 255, dtype=np.uint8)
    canvas[:h, :w] = image

    cv2.putText(canvas, "Top-K Classification", (12, h + 26),
                cv2.FONT_HERSHEY_SIMPLEX, 0.75, (20, 20, 20), 2)
    bar_x = 300
    bar_max = panel_w - bar_x - 20
    for i in range(n):
        y = h + 52 + i * 34
        conf = float(probs[i])
        cv2.putText(canvas, f"{i + 1}. {labels[i]}", (12, y),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (40, 40, 40), 1)
        cv2.putText(canvas, f"{conf * 100:.1f}%", (bar_x - 8, y),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, (40, 40, 40), 1)
        bw = max(4, int(bar_max * conf))
        cv2.rectangle(canvas, (bar_x, y - 13), (bar_x + bw, y), (33, 150, 243), -1)
    return canvas

# ==================== 算法 1：图像分类 ====================

def image_classification(image: np.ndarray, params: dict) -> np.ndarray:
    top_k = int(params.get("top_k", 3))
    device = _get_device()
    model = _load_classifier()

    rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    inp = _preprocess_imagenet(rgb, 224, device)
    with torch.inference_mode():
        logits = model(inp)
    probs = F.softmax(logits[0], dim=0)
    top_probs, top_idx = torch.topk(probs, top_k)

    classes = _load_imagenet_classes()
    labels = [_label_of(int(i), classes) for i in top_idx.cpu().tolist()]
    return _render_topk(image, labels, top_probs.cpu().tolist())

# ==================== 算法 2：语义分割 ====================

def semantic_segmentation(image: np.ndarray, params: dict) -> np.ndarray:
    opacity = float(params.get("opacity", 0.5))
    device = _get_device()
    model = _load_segmenter()

    rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    inp = _preprocess_imagenet(rgb, 520, device)
    with torch.inference_mode():
        out = model(inp)["out"][0]               # (21, H, W)
    pred = torch.argmax(out, dim=0).cpu().numpy().astype(np.uint8)

    h, w = image.shape[:2]
    pred_resized = cv2.resize(pred, (w, h), interpolation=cv2.INTER_NEAREST)
    colorized = VOC_PALETTE[pred_resized]        # (H, W, 3) BGR
    return cv2.addWeighted(image, 1 - opacity, colorized, opacity, 0)

# ==================== 算法 3：图像超分辨率 ====================

def super_resolution(image: np.ndarray, params: dict) -> np.ndarray:
    scale = int(params.get("scale", 2))
    device = _get_device()
    checkpoint = _require_checkpoint("srcnn.pth", "训练 SRCNN 超分辨率模型")
    model = _load_srcnn(checkpoint)

    gray = to_grayscale(image)
    h, w = gray.shape
    lr = cv2.resize(gray, (w // scale, h // scale), interpolation=cv2.INTER_AREA)
    lr_up = cv2.resize(lr, (w, h), interpolation=cv2.INTER_CUBIC)

    x = torch.from_numpy(lr_up.astype(np.float32) / 255.0).unsqueeze(0).unsqueeze(0).to(device)
    with torch.inference_mode():
        sr = model(x)
    sr = torch.clamp(sr, 0, 1).squeeze().cpu().numpy()
    sr = (sr * 255).astype(np.uint8)

    if image.ndim == 3:
        ycrcb = cv2.cvtColor(image, cv2.COLOR_BGR2YCrCb)
        ycrcb[:, :, 0] = sr
        return cv2.cvtColor(ycrcb, cv2.COLOR_YCrCb2BGR)
    return sr

# ==================== 算法 4：CIFAR-10 分类（自定义训练模型） ====================

def cifar10_classification(image: np.ndarray, params: dict) -> np.ndarray:
    top_k = int(params.get("top_k", 3))
    device = _get_device()
    checkpoint = _require_checkpoint("cifar10_cnn.pth", "训练 CIFAR-10 分类网络")
    model = _load_cifar10_model(checkpoint)

    rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    img = Image.fromarray(rgb).resize((32, 32), Image.BILINEAR)
    arr = np.asarray(img, dtype=np.float32) / 255.0
    arr = (arr - np.array(CIFAR10_MEAN, dtype=np.float32)) / np.array(CIFAR10_STD, dtype=np.float32)
    x = torch.from_numpy(arr).permute(2, 0, 1).unsqueeze(0).to(device)

    with torch.inference_mode():
        logits = model(x)
    probs = F.softmax(logits[0], dim=0)
    top_probs, top_idx = torch.topk(probs, top_k)
    labels = [CIFAR10_CLASSES[int(i)] for i in top_idx.cpu().tolist()]
    return _render_topk(image, labels, top_probs.cpu().tolist())

# ==================== 步骤可视化（教学面板 Tab2） ====================

def get_dl_steps(image: np.ndarray, algorithm: str, params: dict):
    """
    返回深度学习算法的中间步骤列表 [(名称, BGR 图像), ...]。
    供 ui/steps.py 的步骤可视化标签页调用。
    """
    if algorithm == "image_classification":
        return _classification_steps(image, params)
    if algorithm == "semantic_segmentation":
        return _segmentation_steps(image, params)
    if algorithm == "super_resolution":
        return _sr_steps(image, params)
    if algorithm == "cifar10_classification":
        return _cifar10_steps(image, params)
    return []

def _classification_steps(image, params):
    from modules.dl_visualization import plot_feature_maps, plot_grad_cam
    device = _get_device()
    model = _load_classifier()
    inp = _preprocess_imagenet(cv2.cvtColor(image, cv2.COLOR_BGR2RGB), 224, device)

    steps = [("原始图像", image)]
    try:
        steps.append(("各层特征图", plot_feature_maps(model, inp)))
    except Exception:
        pass
    try:
        steps.append(("Grad-CAM 热力图", plot_grad_cam(image, model, inp)))
    except Exception:
        pass
    steps.append(("分类结果", image_classification(image, params)))
    return steps

def _segmentation_steps(image, params):
    result = semantic_segmentation(image, params)
    return [("原始图像", image), ("语义分割结果", result)]

def _sr_steps(image, params):
    scale = int(params.get("scale", 2))
    gray = to_grayscale(image)
    h, w = gray.shape
    lr = cv2.resize(gray, (w // scale, h // scale), interpolation=cv2.INTER_AREA)
    lr_up = cv2.resize(lr, (w, h), interpolation=cv2.INTER_CUBIC)
    result = super_resolution(image, params)
    return [
        ("低分辨率 LR", ensure_3channel(lr)),
        ("双三次放大", ensure_3channel(lr_up)),
        ("SRCNN 超分结果", result),
    ]

def _cifar10_steps(image, params):
    from modules.dl_visualization import plot_feature_maps
    device = _get_device()
    checkpoint = _require_checkpoint("cifar10_cnn.pth", "训练 CIFAR-10 分类网络")
    model = _load_cifar10_model(checkpoint)

    rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    small = cv2.resize(rgb, (32, 32))
    arr = np.asarray(small, dtype=np.float32) / 255.0
    arr = (arr - np.array(CIFAR10_MEAN, dtype=np.float32)) / np.array(CIFAR10_STD, dtype=np.float32)
    x = torch.from_numpy(arr).permute(2, 0, 1).unsqueeze(0).to(device)

    steps = [
        ("原始图像", image),
        ("输入 (32×32)", ensure_3channel(cv2.resize(image, (96, 96)))),
    ]
    try:
        steps.append(("各层特征图", plot_feature_maps(model, x)))
    except Exception:
        pass
    steps.append(("分类结果", cifar10_classification(image, params)))
    return steps
