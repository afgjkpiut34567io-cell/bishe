"""
深度学习可视化模块 - CNN 特征图与 Grad-CAM 热力图

面向教学演示，直观呈现卷积神经网络内部表征：
  - 特征图可视化：提取并网格化展示若干卷积层的激活响应，观察
    "浅层检测边缘纹理 → 深层编码语义" 的层次特征提取过程；
  - Grad-CAM：基于梯度加权定位网络关注区域，解释分类依据。

所有绘图函数返回 BGR 格式的 numpy 图像，供 Streamlit/Matplotlib 直接展示。
"""

import numpy as np
import cv2
import torch
import torch.nn as nn
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from modules.visualization import _figure_to_image, _L, COLORS

def _find_conv_layers(model: nn.Module, k: int = 4):
    """返回模型中 Conv2d 层的名称列表（等间隔抽样 k 个，含首尾）。"""
    names = [n for n, m in model.named_modules() if isinstance(m, nn.Conv2d)]
    if not names:
        return []
    if len(names) <= k:
        return names
    idx = np.linspace(0, len(names) - 1, k).astype(int)
    return [names[i] for i in idx]

def _extract_activations(model: nn.Module, input_tensor, layer_names):
    """通过前向 hook 提取指定卷积层的激活输出（不参与梯度）。"""
    activations = {}
    handles = []

    def make_hook(name):
        def hook(module, inp, out):
            activations[name] = out.detach()
        return hook

    for name, module in model.named_modules():
        if name in layer_names:
            handles.append(module.register_forward_hook(make_hook(name)))

    model.eval()
    with torch.inference_mode():
        model(input_tensor)
    for h in handles:
        h.remove()
    return activations

def plot_feature_maps(model: nn.Module, input_tensor, cols: int = 8, max_maps: int = 8) -> np.ndarray:
    """
    提取若干卷积层的特征图并以网格可视化，返回 BGR 图像。

    参数:
        model: 已加载的模型（eval 模式）
        input_tensor: 已预处理的输入张量 (1, C, H, W)，位于正确设备
        cols / max_maps: 每行展示的通道数与每个卷积层展示的最大通道数
    """
    layer_names = _find_conv_layers(model, k=4)
    acts = _extract_activations(model, input_tensor, layer_names)

    rows = []
    for name in layer_names:
        if name not in acts:
            continue
        feat = acts[name][0].float()                     # (C, H, W)
        n = min(feat.shape[0], max_maps)
        feat = feat[:n]
        feat = (feat - feat.min()) / (feat.max() - feat.min() + 1e-8)
        rows.append((name, feat))

    if not rows:
        return np.full((200, 400, 3), 255, dtype=np.uint8)

    n_rows = len(rows)
    fig, axes = plt.subplots(n_rows, cols, figsize=(cols * 1.4, n_rows * 1.7))
    if n_rows == 1:
        axes = axes[None, :]

    for r, (name, feat) in enumerate(rows):
        for c in range(cols):
            ax = axes[r, c]
            if c < feat.shape[0]:
                ax.imshow(feat[c].cpu().numpy(), cmap="viridis")
            ax.axis("off")
        short = name.split(".")[-1] if "." in name else name
        axes[r, 0].set_ylabel(short, fontsize=8, rotation=0, labelpad=24, va="center")

    fig.suptitle(_L("CNN 各层特征图可视化", "CNN Feature Maps"), fontsize=13, fontweight="bold")
    fig.tight_layout()
    return _figure_to_image(fig)

def compute_grad_cam(model: nn.Module, input_tensor, target_class=None):
    """
    计算 Grad-CAM 热力图。

    返回 (cam 热力图 H×W, 目标类别下标)。cam 已归一化到 [0, 1]。
    """
    names = [n for n, m in model.named_modules() if isinstance(m, nn.Conv2d)]
    if not names:
        raise RuntimeError("模型中没有卷积层，无法计算 Grad-CAM")
    last_conv = names[-1]

    activations = {}
    gradients = {}

    def forward_hook(module, inp, out):
        activations["value"] = out

    def backward_hook(module, grad_in, grad_out):
        gradients["value"] = grad_out[0]

    module = dict(model.named_modules())[last_conv]
    fh = module.register_forward_hook(forward_hook)
    bh = module.register_full_backward_hook(backward_hook)

    model.eval()
    x = input_tensor.clone().requires_grad_(True)
    logits = model(x)
    if target_class is None:
        target_class = int(logits.argmax(dim=1))
    model.zero_grad()
    logits[0, target_class].backward()

    fh.remove()
    bh.remove()

    acts = activations["value"][0]          # (C, H, W)
    grads = gradients["value"][0]           # (C, H, W)
    weights = grads.mean(dim=(1, 2))        # (C,) 通道重要性权重
    cam = torch.relu((weights.view(-1, 1, 1) * acts).sum(dim=0))
    cam = cam - cam.min()
    cam = cam / (cam.max() + 1e-8)
    return cam.detach().cpu().numpy(), target_class

def plot_grad_cam(original_bgr: np.ndarray, model: nn.Module, input_tensor, target_class=None) -> np.ndarray:
    """生成 Grad-CAM 热力图叠加原图的并排对比图，返回 BGR 图像。"""
    cam, _ = compute_grad_cam(model, input_tensor, target_class)

    rgb = cv2.cvtColor(original_bgr, cv2.COLOR_BGR2RGB) if original_bgr.ndim == 3 else original_bgr
    h, w = original_bgr.shape[:2]
    cam_resized = cv2.resize(cam, (w, h))

    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    axes[0].imshow(rgb)
    axes[0].set_title(_L("原始图像", "Original Image"))
    axes[0].axis("off")
    axes[1].imshow(rgb)
    axes[1].imshow(cam_resized, cmap="jet", alpha=0.5)
    axes[1].set_title(_L("Grad-CAM 关注区域", "Grad-CAM Attention"))
    axes[1].axis("off")
    fig.tight_layout()
    return _figure_to_image(fig)
