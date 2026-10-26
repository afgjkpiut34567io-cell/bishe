"""
算法注册表 - 集中维护 算法标识符 -> 处理函数 的映射
供 app.py 主流程与 ui/compare.py 对比模式共同使用，避免反向依赖主脚本。
"""

from typing import Callable, Dict

from modules.filters import (
    gaussian_blur, median_blur, mean_blur, bilateral_filter, box_filter,
)
from modules.enhancement import (
    histogram_equalization, clahe, contrast_brightness,
    gamma_correction, sharpening, unsharp_masking,
)
from modules.edge_detection import (
    canny_edge, sobel_edge, laplacian_edge, scharr_edge, prewitt_edge,
)
from modules.morphological import (
    erosion, dilation, opening, closing,
    morphological_gradient, top_hat, black_hat,
)
from modules.segmentation import (
    global_threshold, adaptive_threshold, otsu_threshold,
)
from modules.transforms import (
    resize_scale, rotation, affine_transform, fourier_transform,
    fourier_lowpass, fourier_highpass,
)

# 深度学习算法（可选依赖）。torch 未安装时优雅降级，不影响经典算法平台启动。
try:
    from modules.deep_learning import (
        image_classification, semantic_segmentation,
        super_resolution, cifar10_classification,
    )
    _DL_AVAILABLE = True
except Exception:
    _DL_AVAILABLE = False

    def _dl_unavailable(*args, **kwargs):
        raise RuntimeError(
            "深度学习算法不可用：请安装 torch/torchvision 后重启应用"
            "（参见 requirements-dl.txt）。"
        )

    image_classification = semantic_segmentation = _dl_unavailable
    super_resolution = cifar10_classification = _dl_unavailable

ALGORITHM_FUNCTIONS: Dict[str, Callable] = {
    # 滤波算法
    "gaussian_blur": gaussian_blur,
    "median_blur": median_blur,
    "mean_blur": mean_blur,
    "bilateral_filter": bilateral_filter,
    "box_filter": box_filter,
    # 图像增强
    "histogram_equalization": histogram_equalization,
    "clahe": clahe,
    "contrast_brightness": contrast_brightness,
    "gamma_correction": gamma_correction,
    "sharpening": sharpening,
    "unsharp_masking": unsharp_masking,
    # 边缘检测
    "canny_edge": canny_edge,
    "sobel_edge": sobel_edge,
    "laplacian_edge": laplacian_edge,
    "scharr_edge": scharr_edge,
    "prewitt_edge": prewitt_edge,
    # 形态学操作
    "erosion": erosion,
    "dilation": dilation,
    "opening": opening,
    "closing": closing,
    "morphological_gradient": morphological_gradient,
    "top_hat": top_hat,
    "black_hat": black_hat,
    # 阈值分割
    "global_threshold": global_threshold,
    "adaptive_threshold": adaptive_threshold,
    "otsu_threshold": otsu_threshold,
    # 图像变换
    "resize_scale": resize_scale,
    "rotation": rotation,
    "affine_transform": affine_transform,
    "fourier_transform": fourier_transform,
    "fourier_lowpass": fourier_lowpass,
    "fourier_highpass": fourier_highpass,
}

# 深度学习算法（torch 可用时才注册）
if _DL_AVAILABLE:
    ALGORITHM_FUNCTIONS.update({
        "image_classification": image_classification,
        "semantic_segmentation": semantic_segmentation,
        "super_resolution": super_resolution,
        "cifar10_classification": cifar10_classification,
    })
