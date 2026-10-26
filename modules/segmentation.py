"""
阈值分割模块 - 将图像分割为前景和背景
包含：全局阈值、自适应阈值、Otsu二值化
"""

import cv2
import numpy as np
from typing import Dict, Any, Tuple, List

from utils.image_io import to_grayscale, ensure_3channel

def global_threshold(image: np.ndarray, params: Dict[str, Any]) -> np.ndarray:
    """
    全局阈值分割 - 使用固定阈值进行二值化

    原理：将每个像素与阈值比较，
    pixel > threshold → maxval, pixel ≤ threshold → 0

    参数:
        thresh: 阈值 (0-255)
        maxval: 最大值 (通常是255)
    """
    gray = to_grayscale(image)
    thresh = params.get("thresh", 127)
    maxval = params.get("maxval", 255)
    _, result = cv2.threshold(gray, thresh, maxval, cv2.THRESH_BINARY)
    return ensure_3channel(result)

def adaptive_threshold(image: np.ndarray, params: Dict[str, Any]) -> np.ndarray:
    """
    自适应阈值分割 - 根据局部区域动态计算阈值

    原理：对图像每个像素，根据其邻域像素的统计值（均值或高斯加权均值）
    计算局部阈值。适用于光照不均匀的图像。

    参数:
        block_size: 邻域大小 (奇数，越大适应性越平滑)
        c: 从均值中减去的常数 (越大阈值越低，越亮)
    """
    gray = to_grayscale(image)
    block_size = params.get("block_size", 11)
    if block_size % 2 == 0:
        block_size += 1
    c = params.get("c", 2)

    result = cv2.adaptiveThreshold(
        gray, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        block_size, c
    )
    return ensure_3channel(result)

def otsu_threshold(image: np.ndarray, params: Dict[str, Any]) -> np.ndarray:
    """
    Otsu二值化 - 自动计算最优阈值

    原理：遍历所有可能的阈值，选择使类间方差最大的阈值。
    类间方差越大，说明前景和背景的分离程度越好。
    不需要手动指定阈值，适用于双峰直方图的图像。
    """
    gray = to_grayscale(image)
    _, result = cv2.threshold(
        gray, 0, 255,
        cv2.THRESH_BINARY + cv2.THRESH_OTSU
    )
    return ensure_3channel(result)

def get_otsu_threshold_value(image: np.ndarray) -> float:
    """获取Otsu算法计算出的最优阈值"""
    gray = to_grayscale(image)
    ret, _ = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return ret

def get_segmentation_steps(
    image: np.ndarray, algorithm: str, params: Dict[str, Any]
) -> List[Tuple[str, np.ndarray]]:
    """
    获取分割算法的中间步骤（用于教学可视化）
    """
    steps = []
    gray = to_grayscale(image)

    if algorithm == "global_threshold":
        thresh = params.get("thresh", 127)
        # 创建标记图：低于阈值红色，高于阈值绿色
        mask = gray > thresh
        marked = ensure_3channel(gray).copy()
        marked[~mask] = marked[~mask] * 0.5  # 暗化低于阈值的
        steps.append((f"阈值={thresh}：低于阈值(暗) vs 高于阈值(亮)", marked.astype(np.uint8)))

        _, binary = cv2.threshold(gray, thresh, 255, cv2.THRESH_BINARY)
        steps.append(("最终二值化结果", binary))

    elif algorithm == "adaptive_threshold":
        steps.append(("原始灰度图", gray))

        # 对比全局阈值
        _, global_bin = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
        steps.append(("全局阈值 (thresh=127) —— 不均匀光照下效果差", global_bin))

        block_size = params.get("block_size", 11)
        if block_size % 2 == 0:
            block_size += 1
        c = params.get("c", 2)

        # 展示局部阈值图
        adaptive_result = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY, block_size, c
        )
        steps.append((f"自适应阈值 (block={block_size}, C={c})", adaptive_result))

        # 不同block_size对比
        adaptive_large = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY, 31, c
        )
        steps.append(("自适应阈值 (block=31, 更大邻域)", adaptive_large))

    elif algorithm == "otsu_threshold":
        steps.append(("原始灰度图", gray))

        # 计算最优阈值
        otsu_val = get_otsu_threshold_value(image)
        _, otsu_bin = cv2.threshold(
            gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU
        )
        steps.append((f"Otsu最优阈值 = {otsu_val:.0f}", otsu_bin))

        # 对比不同固定阈值
        for t in [64, 128, 192]:
            _, bin_t = cv2.threshold(gray, t, 255, cv2.THRESH_BINARY)
            steps.append((f"固定阈值 threshold={t}", bin_t))

    return steps
