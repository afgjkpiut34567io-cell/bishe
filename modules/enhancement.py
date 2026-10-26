"""
图像增强模块 - 改善图像视觉效果
包含：直方图均衡化、CLAHE、对比度/亮度调整、伽马校正、锐化、反锐化掩膜
"""

import cv2
import numpy as np
from typing import Dict, Any, Tuple, List

from utils.image_io import to_grayscale, ensure_3channel

def histogram_equalization(image: np.ndarray, params: Dict[str, Any]) -> np.ndarray:
    """
    直方图均衡化 - 通过拉伸像素强度分布来增强对比度

    原理：将原始图像的直方图变换为均匀分布的形式，
    使像素占据整个可能的灰度范围，从而增强整体对比度。

    适用于：整体偏暗或偏亮的图像、X光图像增强等
    """
    gray = to_grayscale(image)
    equalized = cv2.equalizeHist(gray)
    return ensure_3channel(equalized)

def clahe(image: np.ndarray, params: Dict[str, Any]) -> np.ndarray:
    """
    CLAHE - 自适应直方图均衡化（对比度受限）

    原理：将图像分成小块，对每块分别进行直方图均衡化，
    并限制对比度放大以抑制噪声放大。

    参数:
        clip_limit: 对比度限制阈值 (越大对比度越强)
        tile_grid_size: 分块大小 (像素)
    """
    clip_limit = params.get("clip_limit", 2.0)
    tile_grid = params.get("tile_grid_size", (8, 8))
    if isinstance(tile_grid, int):
        tile_grid = (tile_grid, tile_grid)

    gray = to_grayscale(image)
    clahe_obj = cv2.createCLAHE(
        clipLimit=clip_limit, tileGridSize=tile_grid
    )
    result = clahe_obj.apply(gray)
    return ensure_3channel(result)

def contrast_brightness(image: np.ndarray, params: Dict[str, Any]) -> np.ndarray:
    """
    对比度和亮度调整

    原理：对每个像素进行线性变换 new = alpha * old + beta
    alpha控制对比度（>1增强，<1减弱）
    beta控制亮度（>0变亮，<0变暗）

    参数:
        alpha: 对比度系数 (0.0-3.0)
        beta: 亮度偏移 (-100-100)
    """
    alpha = params.get("alpha", 1.0)
    beta = params.get("beta", 0)
    result = cv2.convertScaleAbs(image, alpha=alpha, beta=beta)
    return result

# 伽马校正查找表缓存：按 gamma 值缓存 256 元素 LUT，避免每次调用重建
_GAMMA_LUT_CACHE: Dict[float, np.ndarray] = {}

def gamma_correction(image: np.ndarray, params: Dict[str, Any]) -> np.ndarray:
    """
    伽马校正 - 非线性亮度调整

    原理：对像素值进行幂律变换 out = 255 * (in/255)^(1/gamma)
    gamma<1：提升暗部，图像变亮
    gamma>1：压缩亮部，图像变暗

    参数:
        gamma: 伽马值 (0.1-5.0)
    """
    gamma = params.get("gamma", 1.0)
    gamma = max(0.1, min(5.0, gamma))

    # 按 gamma 缓存查找表，参数相同时直接复用
    cache_key = round(gamma, 2)
    table = _GAMMA_LUT_CACHE.get(cache_key)
    if table is None:
        inv_gamma = 1.0 / gamma
        table = np.array(
            [(i / 255.0) ** inv_gamma * 255 for i in range(256)]
        ).astype(np.uint8)
        _GAMMA_LUT_CACHE[cache_key] = table

    return cv2.LUT(image, table)

def sharpening(image: np.ndarray, params: Dict[str, Any]) -> np.ndarray:
    """
    图像锐化 - 使用拉普拉斯算子增强边缘

    原理：从原图中减去拉普拉斯算子检测到的边缘（乘以强度系数），
    使边缘更加突出，图像更清晰。

    参数:
        strength: 锐化强度 (0.0-5.0)
    """
    strength = params.get("strength", 1.0)
    strength = max(0.0, min(5.0, strength))

    # 拉普拉斯锐化核：中心 = 4 + strength，四邻域 = -1
    # 注意：cv2.filter2D 默认不对核做归一化，直接卷积即可；
    # 此前先按核总和归一化再按中心归一化会互相抵消，导致锐化无效。
    kernel = np.array([
        [0, -1, 0],
        [-1, 4 + strength, -1],
        [0, -1, 0]
    ], dtype=np.float32)

    return cv2.filter2D(image, -1, kernel)

def unsharp_masking(image: np.ndarray, params: Dict[str, Any]) -> np.ndarray:
    """
    反锐化掩膜 (USM) - 专业图像锐化技术

    原理：
    1. 对原图进行高斯模糊
    2. 原图 - 模糊图 = 细节层（掩膜）
    3. 原图 + strength * 细节层 = 锐化结果

    参数:
        sigma: 高斯模糊程度 (控制"细节"的尺度)
        strength: 锐化强度
    """
    sigma = params.get("sigma", 1.0)
    strength = params.get("strength", 1.0)

    # 高斯模糊
    blurred = cv2.GaussianBlur(image, (0, 0), sigma)
    # 反锐化掩膜
    result = cv2.addWeighted(image, 1.0 + strength, blurred, -strength, 0)
    return result

def get_enhancement_steps(
    image: np.ndarray, algorithm: str, params: Dict[str, Any]
) -> List[Tuple[str, np.ndarray]]:
    """
    获取增强算法的中间步骤（用于教学可视化）
    """
    steps = []
    gray = to_grayscale(image)

    if algorithm == "histogram_equalization":
        steps.append(("原始灰度图", gray))
        steps.append(("直方图均衡化后", cv2.equalizeHist(gray)))

    elif algorithm == "clahe":
        steps.append(("原始灰度图", gray))
        # 对比：普通直方图均衡化
        steps.append(("普通直方图均衡化", cv2.equalizeHist(gray)))
        clip_limit = params.get("clip_limit", 2.0)
        tile_grid = params.get("tile_grid_size", (8, 8))
        if isinstance(tile_grid, int):
            tile_grid = (tile_grid, tile_grid)
        clahe_obj = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=tile_grid)
        steps.append(("CLAHE结果", clahe_obj.apply(gray)))

    elif algorithm == "gamma_correction":
        gamma = params.get("gamma", 1.0)
        # 展示不同gamma
        for g in [0.5, 1.0, 2.0]:
            inv = 1.0 / g
            table = np.array(
                [(i / 255.0) ** inv * 255 for i in range(256)]
            ).astype(np.uint8)
            label = f"γ = {g}" + (" (当前)" if abs(g - gamma) < 0.01 else "")
            steps.append((label, cv2.LUT(image, table)))

    elif algorithm == "sharpening":
        steps.append(("原始图像", image))
        strength = params.get("strength", 1.0)
        for s in [0.5, 1.0, 2.0]:
            kernel = np.array([
                [0, -1, 0],
                [-1, 4 + s, -1],
                [0, -1, 0]
            ], dtype=np.float32)
            label = f"锐化强度 s={s}" + (" (当前)" if abs(s - strength) < 0.01 else "")
            steps.append((label, cv2.filter2D(image, -1, kernel)))

    elif algorithm == "unsharp_masking":
        sigma_val = params.get("sigma", 1.0)
        strength_val = params.get("strength", 1.0)
        # 步骤1：原图
        steps.append(("① 原始图像", image))
        # 步骤2：高斯模糊
        blurred = cv2.GaussianBlur(image, (0, 0), sigma_val)
        steps.append(("② 高斯模糊 (σ={})".format(sigma_val), blurred))
        # 步骤3：细节层
        detail = cv2.subtract(image, blurred)
        steps.append(("③ 细节层 = 原图 - 模糊图", detail))
        # 步骤4：最终结果
        result = cv2.addWeighted(image, 1.0 + strength_val, blurred, -strength_val, 0)
        steps.append(("④ 最终锐化结果", result))

    return steps
