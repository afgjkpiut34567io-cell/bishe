"""
边缘检测模块 - 检测图像中亮度变化显著的边缘
包含：Canny、Sobel、Laplacian、Scharr、Prewitt算子
"""

import cv2
import numpy as np
from typing import Dict, Any, Tuple, List

from utils.image_io import to_grayscale, ensure_3channel

def canny_edge(image: np.ndarray, params: Dict[str, Any]) -> np.ndarray:
    """
    Canny边缘检测 - 经典的多级边缘检测算法

    原理：
    1. 高斯滤波降噪
    2. 计算梯度幅值和方向
    3. 非极大值抑制（细化边缘）
    4. 双阈值检测和边缘连接

    参数:
        threshold1: 低阈值 (弱边缘下限)
        threshold2: 高阈值 (强边缘下限)
    """
    gray = to_grayscale(image)
    t1 = params.get("threshold1", 50)
    t2 = params.get("threshold2", 150)
    edges = cv2.Canny(gray, t1, t2)
    return ensure_3channel(edges)

def sobel_edge(image: np.ndarray, params: Dict[str, Any]) -> np.ndarray:
    """
    Sobel边缘检测 - 基于一阶导数的边缘检测算子

    原理：使用两个3×3核分别计算x和y方向的梯度近似值，
    结合得到梯度幅值。Sobel算子对噪声有一定抑制能力。

    参数:
        ksize: Sobel核大小 (3/5/7)
        dx: X方向导数阶数
        dy: Y方向导数阶数
    """
    gray = to_grayscale(image)
    ksize = params.get("ksize", 3)
    if ksize % 2 == 0:
        ksize += 1
    dx = params.get("dx", 1)
    dy = params.get("dy", 1)

    if dx == 1 and dy == 1:
        # 同时计算X和Y方向
        grad_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=ksize)
        grad_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=ksize)
        abs_x = cv2.convertScaleAbs(grad_x)
        abs_y = cv2.convertScaleAbs(grad_y)
        result = cv2.addWeighted(abs_x, 0.5, abs_y, 0.5, 0)
    elif dx == 1:
        result = cv2.convertScaleAbs(cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=ksize))
    else:
        result = cv2.convertScaleAbs(cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=ksize))

    return ensure_3channel(result)

def laplacian_edge(image: np.ndarray, params: Dict[str, Any]) -> np.ndarray:
    """
    Laplacian边缘检测 - 基于二阶导数的边缘检测算子

    原理：计算图像的二阶导数，边缘出现在二阶导数过零点处。
    Laplacian算子对噪声敏感，通常需要先进行高斯平滑。

    参数:
        ksize: 核大小 (1/3/5/7)
    """
    gray = to_grayscale(image)
    ksize = params.get("ksize", 3)
    if ksize % 2 == 0:
        ksize += 1

    laplacian = cv2.Laplacian(gray, cv2.CV_64F, ksize=ksize)
    result = cv2.convertScaleAbs(laplacian)
    return ensure_3channel(result)

def scharr_edge(image: np.ndarray, params: Dict[str, Any]) -> np.ndarray:
    """
    Scharr边缘检测 - Sobel算子的改进版本

    原理：使用优化的3×3核，对旋转对称性更好，
    比Sobel算子精度更高，适用于检测细小边缘。

    参数:
        dx: X方向导数阶数
        dy: Y方向导数阶数
    """
    gray = to_grayscale(image)
    dx = params.get("dx", 1)
    dy = params.get("dy", 0)

    if dx == 1 and dy == 0:
        grad = cv2.Scharr(gray, cv2.CV_64F, 1, 0)
    elif dx == 0 and dy == 1:
        grad = cv2.Scharr(gray, cv2.CV_64F, 0, 1)
    else:
        # 同时显示X和Y方向
        grad_x = cv2.Scharr(gray, cv2.CV_64F, 1, 0)
        grad_y = cv2.Scharr(gray, cv2.CV_64F, 0, 1)
        abs_x = cv2.convertScaleAbs(grad_x)
        abs_y = cv2.convertScaleAbs(grad_y)
        result = cv2.addWeighted(abs_x, 0.5, abs_y, 0.5, 0)
        return ensure_3channel(result)

    result = cv2.convertScaleAbs(grad)
    return ensure_3channel(result)

def prewitt_edge(image: np.ndarray, params: Dict[str, Any]) -> np.ndarray:
    """
    Prewitt边缘检测 - 经典的一阶导数边缘检测算子

    原理：与Sobel类似但使用不同的核权重，
    Prewitt核没有强调中心像素的权重，计算更简单但精度略低。
    """
    gray = to_grayscale(image)

    # Prewitt X核
    kernel_x = np.array([[-1, 0, 1],
                          [-1, 0, 1],
                          [-1, 0, 1]], dtype=np.float32)
    # Prewitt Y核
    kernel_y = np.array([[-1, -1, -1],
                          [0, 0, 0],
                          [1, 1, 1]], dtype=np.float32)

    grad_x = cv2.filter2D(gray, cv2.CV_64F, kernel_x)
    grad_y = cv2.filter2D(gray, cv2.CV_64F, kernel_y)

    abs_x = cv2.convertScaleAbs(grad_x)
    abs_y = cv2.convertScaleAbs(grad_y)
    result = cv2.addWeighted(abs_x, 0.5, abs_y, 0.5, 0)
    return ensure_3channel(result)

def get_edge_steps(
    image: np.ndarray, algorithm: str, params: Dict[str, Any]
) -> List[Tuple[str, np.ndarray]]:
    """
    获取边缘检测算法的中间步骤（用于教学可视化）
    """
    steps = []
    gray = to_grayscale(image)

    if algorithm == "canny_edge":
        t1 = params.get("threshold1", 50)
        t2 = params.get("threshold2", 150)

        # 步骤1：高斯降噪
        blurred = cv2.GaussianBlur(gray, (5, 5), 1.4)
        steps.append(("① 高斯降噪", blurred))

        # 步骤2：梯度幅值
        grad_x = cv2.Sobel(blurred, cv2.CV_64F, 1, 0, ksize=3)
        grad_y = cv2.Sobel(blurred, cv2.CV_64F, 0, 1, ksize=3)
        magnitude = np.sqrt(grad_x ** 2 + grad_y ** 2)
        magnitude = (magnitude / magnitude.max() * 255).astype(np.uint8)
        steps.append(("② 梯度幅值", magnitude))

        # 步骤3：非极大值抑制 + 双阈值
        edges = cv2.Canny(blurred, t1, t2)
        steps.append(("③ 非极大值抑制+双阈值", edges))

        # 对比不同阈值
        steps.append((f"低阈值={t1}, 高阈值={t2}（当前）", edges))
        steps.append(("低阈值=50, 高阈值=100", cv2.Canny(blurred, 50, 100)))

    elif algorithm == "sobel_edge":
        ksize = params.get("ksize", 3)
        if ksize % 2 == 0:
            ksize += 1

        # X方向梯度
        grad_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=ksize)
        abs_x = cv2.convertScaleAbs(grad_x)
        steps.append(("X方向梯度 Gx（检测垂直边缘）", abs_x))

        # Y方向梯度
        grad_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=ksize)
        abs_y = cv2.convertScaleAbs(grad_y)
        steps.append(("Y方向梯度 Gy（检测水平边缘）", abs_y))

        # 合并
        combined = cv2.addWeighted(abs_x, 0.5, abs_y, 0.5, 0)
        steps.append(("合并结果 |G| = √(Gx²+Gy²)", combined))

    elif algorithm == "laplacian_edge":
        ksize = params.get("ksize", 3)
        if ksize % 2 == 0:
            ksize += 1

        # 先平滑再求二阶导
        blurred = cv2.GaussianBlur(gray, (5, 5), 1.0)
        steps.append(("高斯平滑后", blurred))

        lap = cv2.Laplacian(blurred, cv2.CV_64F, ksize=ksize)
        lap_abs = cv2.convertScaleAbs(lap)
        steps.append(("Laplacian结果", lap_abs))

    elif algorithm == "scharr_edge":
        grad_x = cv2.Scharr(gray, cv2.CV_64F, 1, 0)
        abs_x = cv2.convertScaleAbs(grad_x)
        steps.append(("Scharr X方向", abs_x))

        grad_y = cv2.Scharr(gray, cv2.CV_64F, 0, 1)
        abs_y = cv2.convertScaleAbs(grad_y)
        steps.append(("Scharr Y方向", abs_y))

        combined = cv2.addWeighted(abs_x, 0.5, abs_y, 0.5, 0)
        steps.append(("合并结果", combined))

    return steps
