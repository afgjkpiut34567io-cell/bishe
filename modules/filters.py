"""
滤波算法模块 - 空间域图像滤波
包含：高斯滤波、中值滤波、均值滤波、双边滤波、方框滤波
"""

import cv2
import numpy as np
from typing import Dict, Any, Tuple, List

from utils.image_io import to_grayscale

def gaussian_blur(image: np.ndarray, params: Dict[str, Any]) -> np.ndarray:
    """
    高斯滤波 - 使用高斯核对图像进行平滑处理

    原理：使用符合高斯分布的权重模板对图像进行卷积，中心点权重最大，
    离中心越远权重越小。高斯滤波对高斯噪声有很好的抑制效果。

    参数:
        ksize: 核大小 (奇数，越大平滑效果越强)
        sigma_x: X方向标准差 (越大模糊越强)
    """
    ksize = params.get("ksize", (5, 5))
    sigma_x = params.get("sigma_x", 1.0)
    if isinstance(ksize, int):
        ksize = (ksize, ksize)
    # 确保核大小为奇数
    ksize = (ksize[0] | 1, ksize[1] | 1)
    return cv2.GaussianBlur(image, ksize, sigmaX=sigma_x, sigmaY=sigma_x)

def median_blur(image: np.ndarray, params: Dict[str, Any]) -> np.ndarray:
    """
    中值滤波 - 使用邻域像素中值替换中心像素

    原理：将滤波器窗口内所有像素值排序，取中间值替换中心像素。
    对椒盐噪声有极佳的去除效果，同时能较好保留边缘。

    参数:
        ksize: 核大小 (奇数，越大去噪效果越强)
    """
    ksize = params.get("ksize", 5)
    if ksize % 2 == 0:
        ksize += 1
    return cv2.medianBlur(image, ksize)

def mean_blur(image: np.ndarray, params: Dict[str, Any]) -> np.ndarray:
    """
    均值滤波 - 使用邻域像素平均值替换中心像素

    原理：将滤波器窗口内所有像素值取平均值，是最简单的线性滤波器。
    计算速度快但会模糊边缘。

    参数:
        ksize: 核大小 (越大平滑效果越强)
    """
    ksize = params.get("ksize", (5, 5))
    if isinstance(ksize, int):
        ksize = (ksize, ksize)
    return cv2.blur(image, ksize)

def bilateral_filter(image: np.ndarray, params: Dict[str, Any]) -> np.ndarray:
    """
    双边滤波 - 同时考虑空间距离和像素值差异的非线性滤波

    原理：在高斯滤波的基础上增加了像素值相似度权重，
    使滤波器在平滑区域时也能保留边缘信息。是"保边去噪"的经典算法。

    参数:
        d: 滤波直径 (越大影响范围越大)
        sigma_color: 颜色空间标准差 (越大颜色越混合)
        sigma_space: 坐标空间标准差 (越大空间影响越大)
    """
    d = params.get("d", 9)
    sigma_color = params.get("sigma_color", 75)
    sigma_space = params.get("sigma_space", 75)
    return cv2.bilateralFilter(image, d, sigma_color, sigma_space)

def box_filter(image: np.ndarray, params: Dict[str, Any]) -> np.ndarray:
    """
    方框滤波 - 使用均匀权重核进行滤波

    原理：与均值滤波类似，但可以通过参数控制是否归一化。
    归一化时为均值滤波，不归一化时仅求和。

    参数:
        ksize: 核大小
    """
    ksize = params.get("ksize", (5, 5))
    if isinstance(ksize, int):
        ksize = (ksize, ksize)
    return cv2.boxFilter(image, -1, ksize, normalize=True)

def get_filter_steps(
    image: np.ndarray, algorithm: str, params: Dict[str, Any]
) -> List[Tuple[str, np.ndarray]]:
    """
    获取滤波算法的中间步骤（用于教学可视化）
    """
    steps = []
    gray = to_grayscale(image)

    if algorithm == "gaussian_blur":
        ksize = params.get("ksize", (5, 5))
        if isinstance(ksize, int):
            ksize = (ksize, ksize)
        ksize = (ksize[0] | 1, ksize[1] | 1)
        sigma = params.get("sigma_x", 1.0)

        # 生成高斯核可视化
        kernel = cv2.getGaussianKernel(ksize[0], sigma)
        kernel_2d = kernel @ kernel.T
        kernel_vis = (kernel_2d / kernel_2d.max() * 255).astype(np.uint8)
        steps.append(("高斯核权重分布", kernel_vis))

        # 水平方向滤波
        h_blur = cv2.GaussianBlur(gray, (ksize[0], 1), sigmaX=sigma)
        steps.append(("水平方向滤波", h_blur))

        steps.append(("垂直方向滤波（最终结果）",
                      cv2.GaussianBlur(gray, ksize, sigmaX=sigma)))

    elif algorithm == "median_blur":
        ksize = params.get("ksize", 5)
        if ksize % 2 == 0:
            ksize += 1

        # 添加椒盐噪声示例
        noisy = gray.copy()
        salt_pepper_amount = 0.05
        num_salt = int(salt_pepper_amount * noisy.size * 0.5)
        num_pepper = int(salt_pepper_amount * noisy.size * 0.5)
        coords_salt = [np.random.randint(0, i - 1, num_salt) for i in gray.shape]
        coords_pepper = [np.random.randint(0, i - 1, num_pepper) for i in gray.shape]
        noisy[coords_salt[0], coords_salt[1]] = 255
        noisy[coords_pepper[0], coords_pepper[1]] = 0
        steps.append(("添加椒盐噪声", noisy))

        # 小窗口 vs 大窗口
        steps.append(("中值滤波 (3×3)", cv2.medianBlur(noisy.copy(), 3)))
        steps.append((f"中值滤波 ({ksize}×{ksize})", cv2.medianBlur(noisy.copy(), ksize)))

    elif algorithm == "bilateral_filter":
        # 空间域滤波
        steps.append(("高斯滤波(仅空间域)", cv2.GaussianBlur(gray, (9, 9), 5)))
        steps.append(("双边滤波(空间+颜色)", bilateral_filter(image, params)))

    return steps
