"""
步骤可视化模块 - 展示算法的中间处理步骤和数据变化曲线
"""

import streamlit as st
import numpy as np
import cv2
from typing import Optional, Dict, Any, List, Tuple

from modules.visualization import (
    plot_histogram_comparison,
    plot_steps_grid,
    plot_gamma_curves,
    plot_frequency_analysis,
)
from utils.image_io import to_grayscale

# 导入各模块的步骤函数
from modules.filters import get_filter_steps
from modules.enhancement import get_enhancement_steps
from modules.edge_detection import get_edge_steps
from modules.morphological import get_morphology_steps
from modules.segmentation import get_segmentation_steps
from modules.transforms import get_transform_steps

# 深度学习步骤函数（可选依赖，torch 缺失时为 None）
try:
    from modules.deep_learning import get_dl_steps
except Exception:
    get_dl_steps = None

# 步骤函数查找表
STEPS_FUNCTIONS = {
    # 滤波
    "gaussian_blur": get_filter_steps,
    "median_blur": get_filter_steps,
    "mean_blur": get_filter_steps,
    "bilateral_filter": get_filter_steps,
    "box_filter": get_filter_steps,
    # 增强
    "histogram_equalization": get_enhancement_steps,
    "clahe": get_enhancement_steps,
    "contrast_brightness": get_enhancement_steps,
    "gamma_correction": get_enhancement_steps,
    "sharpening": get_enhancement_steps,
    "unsharp_masking": get_enhancement_steps,
    # 边缘检测
    "canny_edge": get_edge_steps,
    "sobel_edge": get_edge_steps,
    "laplacian_edge": get_edge_steps,
    "scharr_edge": get_edge_steps,
    "prewitt_edge": get_edge_steps,
    # 形态学
    "erosion": get_morphology_steps,
    "dilation": get_morphology_steps,
    "opening": get_morphology_steps,
    "closing": get_morphology_steps,
    "morphological_gradient": get_morphology_steps,
    "top_hat": get_morphology_steps,
    "black_hat": get_morphology_steps,
    # 分割
    "global_threshold": get_segmentation_steps,
    "adaptive_threshold": get_segmentation_steps,
    "otsu_threshold": get_segmentation_steps,
    # 变换
    "resize_scale": get_transform_steps,
    "rotation": get_transform_steps,
    "affine_transform": get_transform_steps,
    "fourier_transform": get_transform_steps,
    "fourier_lowpass": get_transform_steps,
    "fourier_highpass": get_transform_steps,
}

# 深度学习算法的步骤函数（torch 可用时注册）
if get_dl_steps is not None:
    STEPS_FUNCTIONS.update({
        "image_classification": get_dl_steps,
        "semantic_segmentation": get_dl_steps,
        "super_resolution": get_dl_steps,
        "cifar10_classification": get_dl_steps,
    })

def render_steps_visualization(
    original: np.ndarray,
    processed: Optional[np.ndarray],
    algorithm_key: str,
    params: Dict[str, Any],
):
    """
    渲染算法步骤可视化页面

    参数:
        original: 原始图像 (BGR)
        processed: 处理后的图像 (BGR)
        algorithm_key: 算法标识符
        params: 算法参数
    """
    st.header("🔬 算法步骤可视化")

    if processed is None:
        st.info("请先上传图像并选择算法")
        return

    # ==================== Tab 1: 处理步骤 ====================
    tab1, tab2, tab3 = st.tabs(["📋 处理步骤", "📊 直方图分析", "📈 数据曲线"])

    with tab1:
        _render_processing_steps(original, algorithm_key, params)

    with tab2:
        _render_histogram_analysis(original, processed, algorithm_key)

    with tab3:
        _render_data_curves(original, algorithm_key, params)

def _render_processing_steps(
    original: np.ndarray,
    algorithm_key: str,
    params: Dict[str, Any],
):
    """渲染步骤网格"""
    step_func = STEPS_FUNCTIONS.get(algorithm_key)

    if step_func is None:
        st.info("该算法暂无步骤可视化")
        return

    try:
        steps = step_func(original, algorithm_key, params)
    except Exception:
        st.info("该算法的步骤可视化暂不可用")
        return

    if not steps:
        st.info("该算法暂无中间步骤展示")
        return

    st.caption(f"共 {len(steps)} 个步骤")

    # 使用Matplotlib绘制步骤网格
    step_image = plot_steps_grid(steps, cols=3, title="")
    st.image(
        cv2.cvtColor(step_image, cv2.COLOR_BGR2RGB),
        use_container_width=True,
    )

def _render_histogram_analysis(
    original: np.ndarray,
    processed: Optional[np.ndarray],
    algorithm_key: str,
):
    """渲染直方图分析"""
    if processed is None:
        return

    st.subheader("直方图对比分析")

    # 直方图对比图
    hist_comparison = plot_histogram_comparison(
        original, processed,
        title="处理前后直方图对比"
    )
    st.image(
        cv2.cvtColor(hist_comparison, cv2.COLOR_BGR2RGB),
        use_container_width=True,
    )

    # 解释文字
    gray_orig = to_grayscale(original)
    gray_proc = to_grayscale(processed)

    col1, col2 = st.columns(2)
    with col1:
        st.metric("原图标准差", f"{gray_orig.std():.1f}",
                  help="标准差反映像素值的离散程度，越大对比度越高")
    with col2:
        st.metric("处理后标准差", f"{gray_proc.std():.1f}",
                  delta=f"{gray_proc.std() - gray_orig.std():.1f}",
                  help="标准差变化反映对比度的改变")

def _render_data_curves(
    original: np.ndarray,
    algorithm_key: str,
    params: Dict[str, Any],
):
    """渲染数据曲线（伽马曲线、频率能量分布等）"""
    if algorithm_key == "gamma_correction":
        st.subheader("伽马校正曲线")
        gamma_val = params.get("gamma", 1.0)
        curve_img = plot_gamma_curves(current_gamma=gamma_val)
        st.image(
            cv2.cvtColor(curve_img, cv2.COLOR_BGR2RGB),
            use_container_width=True,
        )

    elif algorithm_key == "fourier_transform":
        st.subheader("频率域分析")
        freq_img = plot_frequency_analysis(original)
        st.image(
            cv2.cvtColor(freq_img, cv2.COLOR_BGR2RGB),
            use_container_width=True,
        )

    elif algorithm_key in ("histogram_equalization", "clahe"):
        st.subheader("累积分布函数 (CDF)")

        gray = to_grayscale(original)
        hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
        cdf = hist.cumsum()
        cdf_normalized = cdf / cdf[-1] * 255

        # 使用Matplotlib
        from modules.visualization import _figure_to_image
        import matplotlib.pyplot as plt

        fig, axes = plt.subplots(1, 2, figsize=(10, 3.5))

        axes[0].bar(range(256), hist.ravel(), width=1, color="#2196F3", alpha=0.7)
        axes[0].set_title("灰度直方图")
        axes[0].set_xlabel("像素值")
        axes[0].set_ylabel("频数")

        axes[1].plot(cdf_normalized, color="#FF9800", linewidth=2)
        axes[1].set_title("累积分布函数 (CDF)")
        axes[1].set_xlabel("像素值")
        axes[1].set_ylabel("累积概率")
        axes[1].fill_between(range(256), cdf_normalized.ravel(),
                              alpha=0.2, color="#FF9800")

        fig.tight_layout()
        cdf_img = _figure_to_image(fig)
        st.image(
            cv2.cvtColor(cdf_img, cv2.COLOR_BGR2RGB),
            use_container_width=True,
        )

    else:
        st.info("该算法暂无特殊数据曲线，请查看「处理步骤」和「直方图分析」标签页")