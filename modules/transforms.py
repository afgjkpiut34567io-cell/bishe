"""
图像变换模块 - 几何变换和频域变换
包含：缩放、旋转、仿射变换、傅里叶变换
"""

import cv2
import numpy as np
from typing import Dict, Any, Tuple, List

from utils.image_io import to_grayscale, ensure_3channel

def resize_scale(image: np.ndarray, params: Dict[str, Any]) -> np.ndarray:
    """
    图像缩放

    原理：通过插值算法改变图像分辨率。

    参数:
        scale: 缩放比例 (0.1-3.0)
    """
    scale = params.get("scale", 0.5)
    scale = max(0.1, min(3.0, scale))
    h, w = image.shape[:2]
    new_w = int(w * scale)
    new_h = int(h * scale)
    return cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_CUBIC)

def rotation(image: np.ndarray, params: Dict[str, Any]) -> np.ndarray:
    """
    图像旋转

    原理：绕图像中心旋转指定角度。

    参数:
        angle: 旋转角度 (-180° ~ 180°)
        scale: 旋转缩放比例
    """
    angle = params.get("angle", 0)
    scale = params.get("scale", 1.0)
    h, w = image.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, scale)
    result = cv2.warpAffine(image, M, (w, h))
    return result

def affine_transform(image: np.ndarray, params: Dict[str, Any]) -> np.ndarray:
    """
    仿射变换 - 组合旋转、缩放和平移

    原理：使用3个点定义的映射关系进行线性变换，
    保持平行线仍然平行。

    参数:
        angle: 旋转角度
        scale: 缩放比例
        tx: X方向平移 (像素)
        ty: Y方向平移 (像素)
    """
    angle = params.get("angle", 0)
    scale = params.get("scale", 1.0)
    tx = params.get("tx", 0)
    ty = params.get("ty", 0)

    h, w = image.shape[:2]
    center = (w // 2, h // 2)

    # 旋转+缩放矩阵，再叠加平移量到最后一列
    M = cv2.getRotationMatrix2D(center, angle, scale)
    M[0, 2] += tx
    M[1, 2] += ty

    result = cv2.warpAffine(image, M, (w, h))
    return result

def fourier_transform(image: np.ndarray, params: Dict[str, Any]) -> np.ndarray:
    """
    傅里叶变换 - 将图像从空间域转换到频率域

    原理：任何信号都可以表示为不同频率正弦波的叠加。
    傅里叶变换将图像分解为不同频率成分：
    - 低频：图像中变化缓慢的部分（平滑区域）
    - 高频：图像中变化剧烈的部分（边缘、噪声）

    返回: 频域幅度谱的对数值（可视化用）
    """
    gray = to_grayscale(image)

    # 傅里叶变换
    dft = cv2.dft(np.float32(gray), flags=cv2.DFT_COMPLEX_OUTPUT)
    # 将零频率移到中心
    dft_shift = np.fft.fftshift(dft)
    # 计算幅度谱
    magnitude = cv2.magnitude(dft_shift[:, :, 0], dft_shift[:, :, 1])
    # 对数变换以增强可见性
    magnitude_log = np.log(1 + magnitude)
    # 归一化到0-255
    magnitude_norm = (magnitude_log / magnitude_log.max() * 255).astype(np.uint8)

    return ensure_3channel(magnitude_norm)

def fourier_lowpass(image: np.ndarray, params: Dict[str, Any]) -> np.ndarray:
    """
    傅里叶低通滤波 - 仅保留低频成分（平滑图像）

    原理：在频域中用圆形掩膜保留中心低频区域，滤除高频噪声。
    截止频率越小，平滑效果越强。

    参数:
        cutoff_ratio: 截止频率比例 (0.01-0.5)
    """
    cutoff_ratio = float(params.get("cutoff_ratio", 0.1))
    cutoff_ratio = max(0.01, min(0.5, cutoff_ratio))
    gray = to_grayscale(image)
    h, w = gray.shape

    # 傅里叶变换
    dft = cv2.dft(np.float32(gray), flags=cv2.DFT_COMPLEX_OUTPUT)
    dft_shift = np.fft.fftshift(dft)

    # 创建低通掩膜
    mask = np.zeros((h, w, 2), np.float32)
    cy, cx = h // 2, w // 2
    radius = int(min(h, w) * cutoff_ratio)
    cv2.circle(mask, (cx, cy), radius, (1, 1), -1)

    # 应用掩膜
    dft_filtered = dft_shift * mask

    # 逆变换
    dft_ishift = np.fft.ifftshift(dft_filtered)
    img_back = cv2.idft(dft_ishift)
    img_back = cv2.magnitude(img_back[:, :, 0], img_back[:, :, 1])
    img_back = (img_back / img_back.max() * 255).astype(np.uint8)

    return ensure_3channel(img_back)

def fourier_highpass(image: np.ndarray, params: Dict[str, Any]) -> np.ndarray:
    """
    傅里叶高通滤波 - 仅保留高频成分（提取边缘）

    原理：在频域中去除中心低频区域，保留高频边缘信息。
    截止频率越小，保留的低频越少，边缘提取越激进。

    参数:
        cutoff_ratio: 截止频率比例 (0.01-0.5)
    """
    cutoff_ratio = float(params.get("cutoff_ratio", 0.1))
    cutoff_ratio = max(0.01, min(0.5, cutoff_ratio))
    gray = to_grayscale(image)
    h, w = gray.shape

    dft = cv2.dft(np.float32(gray), flags=cv2.DFT_COMPLEX_OUTPUT)
    dft_shift = np.fft.fftshift(dft)

    # 创建高通掩膜
    mask = np.ones((h, w, 2), np.float32)
    cy, cx = h // 2, w // 2
    radius = int(min(h, w) * cutoff_ratio)
    cv2.circle(mask, (cx, cy), radius, (0, 0), -1)

    dft_filtered = dft_shift * mask
    dft_ishift = np.fft.ifftshift(dft_filtered)
    img_back = cv2.idft(dft_ishift)
    img_back = cv2.magnitude(img_back[:, :, 0], img_back[:, :, 1])
    img_back = (img_back / img_back.max() * 255).astype(np.uint8)

    return ensure_3channel(img_back)

def get_transform_steps(
    image: np.ndarray, algorithm: str, params: Dict[str, Any]
) -> List[Tuple[str, np.ndarray]]:
    """
    获取变换算法的中间步骤（用于教学可视化）
    """
    steps = []

    if algorithm == "resize_scale":
        scale = params.get("scale", 0.5)
        h, w = image.shape[:2]
        steps.append((f"原图 ({w}×{h})", image))
        for s in [0.25, 0.5, 1.5]:
            new_w = int(w * s)
            new_h = int(h * s)
            label = f"缩放 {s}× ({new_w}×{new_h})"
            if abs(s - scale) < 0.001:
                label += "（当前）"
            resized = cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_CUBIC)
            steps.append((label, resized))

    elif algorithm == "rotation":
        angle = params.get("angle", 0)
        h, w = image.shape[:2]
        center = (w // 2, h // 2)
        for a in [15, 45, 90]:
            M = cv2.getRotationMatrix2D(center, a, 1.0)
            rotated = cv2.warpAffine(image, M, (w, h))
            label = f"旋转 {a}°"
            if abs(a - abs(angle)) < 1:
                label += "（当前）"
            steps.append((label, rotated))

    elif algorithm in ("fourier_transform", "fourier_lowpass", "fourier_highpass"):
        gray = to_grayscale(image)

        # 原图
        steps.append(("原始灰度图", gray))

        # 幅度谱
        dft = cv2.dft(np.float32(gray), flags=cv2.DFT_COMPLEX_OUTPUT)
        dft_shift = np.fft.fftshift(dft)
        magnitude = cv2.magnitude(dft_shift[:, :, 0], dft_shift[:, :, 1])
        magnitude_log = np.log(1 + magnitude)
        magnitude_norm = (magnitude_log / magnitude_log.max() * 255).astype(np.uint8)
        steps.append(("频域幅度谱 (中心=低频, 边缘=高频)", magnitude_norm))

        cutoff = params.get("cutoff_ratio", 0.1)

        # 低通滤波
        lowpass = fourier_lowpass(image, {"cutoff_ratio": cutoff})
        steps.append((f"低通滤波 (截止={cutoff}, 保留低频=平滑图像)", lowpass))

        # 高通滤波
        highpass = fourier_highpass(image, {"cutoff_ratio": cutoff})
        steps.append((f"高通滤波 (截止={cutoff}, 保留高频=提取边缘)", highpass))

    return steps
