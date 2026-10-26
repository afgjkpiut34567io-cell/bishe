"""
算法对比模块 - 同类算法同图并排对比 + 客观质量指标(PSNR/SSIM)
"""

import streamlit as st
import numpy as np
import cv2
from typing import Optional, Dict, Any, List

from utils.config import ALGORITHM_CATEGORIES, DEFAULT_PARAMS
from utils.image_io import bgr_to_rgb, Timer
from data.teaching_content import TEACHING_CONTENT, ALGORITHM_NAMES
from modules.registry import ALGORITHM_FUNCTIONS

# ==================== 客观质量指标 ====================

def compute_quality_metrics(
    original: np.ndarray,
    processed: np.ndarray,
) -> Optional[Dict[str, float]]:
    """
    计算处理前后图像的客观质量指标。

    尺寸不一致时（如缩放类算法）无法逐像素比较，返回 None。

    指标说明：
        - MSE  : 均方误差，越小越接近原图
        - PSNR : 峰值信噪比(dB)，越大越接近原图；图像完全一致时为 inf
        - SSIM : 结构相似度(-1~1，通常为正)，越接近1结构保持越好
    """
    a = _to_single(original)
    b = _to_single(processed)
    if a.shape != b.shape:
        return None
    if a.shape[0] < 7 or a.shape[1] < 7:
        # SSIM 使用 7x7 高斯窗，过小图像不计算
        return None

    a_f = a.astype(np.float64)
    b_f = b.astype(np.float64)

    mse = float(np.mean((a_f - b_f) ** 2))
    psnr = float("inf") if mse == 0 else 10.0 * float(np.log10(255.0 ** 2 / mse))
    ssim = _ssim_single(a, b)
    return {"mse": mse, "psnr": psnr, "ssim": ssim}

# SSIM 用 7x7 高斯窗缓存（仅需构建一次，对比模式下对每个算法复用）
_SSIM_WINDOW: Optional[np.ndarray] = None

def _get_ssim_window() -> np.ndarray:
    """懒加载并缓存 7x7、sigma=1.5 的二维高斯窗（float64）。"""
    global _SSIM_WINDOW
    if _SSIM_WINDOW is None:
        kernel_1d = cv2.getGaussianKernel(7, 1.5)
        _SSIM_WINDOW = (kernel_1d @ kernel_1d.T).astype(np.float64)
    return _SSIM_WINDOW

def _ssim_single(a: np.ndarray, b: np.ndarray) -> float:
    """
    单通道 SSIM（Wang et al. 2004 标准实现）
    高斯加权均值/方差/协方差 + 默认常数 C1=(0.01*255)^2, C2=(0.03*255)^2
    """
    a = a.astype(np.float64)
    b = b.astype(np.float64)

    window = _get_ssim_window()
    c1, c2 = (0.01 * 255) ** 2, (0.03 * 255) ** 2

    mu_a = cv2.filter2D(a, -1, window)
    mu_b = cv2.filter2D(b, -1, window)
    mu_aa, mu_bb, mu_ab = mu_a * mu_a, mu_b * mu_b, mu_a * mu_b
    saab = cv2.filter2D(a * b, -1, window) - mu_ab
    ca = cv2.filter2D(a * a, -1, window) - mu_aa
    cb = cv2.filter2D(b * b, -1, window) - mu_bb

    ssim_map = ((2 * mu_ab + c1) * (2 * saab + c2)) / (
        (mu_aa + mu_bb + c1) * (ca + cb + c2)
    )
    return float(ssim_map.mean())

def _to_single(img: np.ndarray) -> np.ndarray:
    """统一转为 uint8 单通道，便于逐像素比较"""
    if img.ndim == 2:
        return img
    if img.shape[2] == 1:
        return img[:, :, 0]
    return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

def format_metric(value: Optional[float], digits: int = 2, suffix: str = "") -> str:
    """把 inf / None 指标格式化为可读字符串"""
    if value is None:
        return "N/A"
    if value == float("inf"):
        return "∞"
    return f"{value:.{digits}f}{suffix}"

# ==================== 参数默认值组装 ====================

def build_category_params(algorithm_key: str) -> Dict[str, Any]:
    """
    为对比模式组装某算法的默认参数。

    优先取教学内容参数定义中的出厂默认值（args.value），
    缺失的字段再回退到全局 DEFAULT_PARAMS。
    """
    content = TEACHING_CONTENT.get(algorithm_key, {})
    params: Dict[str, Any] = {}
    for pdef in content.get("params", []):
        value = pdef.get("args", {}).get("value")
        if value is not None:
            params[pdef["name"]] = value
    merged = DEFAULT_PARAMS.get(algorithm_key, {}).copy()
    merged.update(params)
    return merged

# ==================== 对比标签页 ====================

@st.cache_data(show_spinner=False)
def _process_for_compare(
    image: np.ndarray, algorithm_key: str, params: Dict[str, Any]
) -> tuple:
    """执行单个算法并计时（结果按 图像+算法+参数 缓存，重复切换分类不重算）"""
    algo_func = ALGORITHM_FUNCTIONS.get(algorithm_key)
    if algo_func is None:
        return image.copy(), 0.0
    try:
        with Timer() as timer:
            result = algo_func(image, params)
        if result.dtype != np.uint8:
            result = np.clip(result, 0, 255).astype(np.uint8)
        return result, timer.elapsed_ms
    except Exception:
        # 深度学习等算法可能因缺少依赖或权重而失败，容错返回原图
        return image.copy(), 0.0

def render_compare_tab(original: np.ndarray, current_algorithm: Optional[str]):
    """
    渲染"算法对比"标签页：选定分类后，该类全部算法在同一张图上
    以默认参数并行处理，输出结果网格 + 逐算法客观质量指标表。
    """
    st.header("🆚 同类算法并排对比")

    category_names = list(ALGORITHM_CATEGORIES.keys())
    default_idx = 0
    if current_algorithm:
        for i, cat in enumerate(category_names):
            if current_algorithm in ALGORITHM_CATEGORIES[cat]["algorithms"]:
                default_idx = i
                break

    selected_category = st.selectbox(
        "选择算法分类",
        category_names,
        index=default_idx,
        key="compare_category",
        help="对同一张图，用该类全部算法的默认参数分别处理并排对比",
    )

    algo_keys: List[str] = ALGORITHM_CATEGORIES[selected_category]["algorithms"]
    if not algo_keys:
        st.info("该分类暂无可对比的算法")
        return

    # 逐算法处理（结果由 st.cache_data 按图+参数缓存，重复切换分类不重算）
    rows = []
    results = []
    for key in algo_keys:
        params = build_category_params(key)
        processed, elapsed = _process_for_compare(original, key, params)
        metrics = compute_quality_metrics(original, processed)
        rows.append(
            {
                "算法": ALGORITHM_NAMES.get(key, key),
                "耗时(ms)": round(elapsed, 1),
                "MSE": round(metrics["mse"], 1) if metrics else None,
                "PSNR(dB)": round(metrics["psnr"], 2)
                if metrics and metrics["psnr"] != float("inf")
                else metrics["psnr"] if metrics
                else None,
                "SSIM": round(metrics["ssim"], 4) if metrics else None,
                "_processed": processed,
            }
        )
        results.append(processed)

    st.caption(
        "💡 MSE/PSNR/SSIM 为结果与原图的逐像素相似度（仅对平滑/增强类算法有意义；"
        "边缘检测、阈值分割等输出二值图的算法数值天然偏低）；尺寸改变类算法显示 N/A。"
    )

    # ==================== 结果网格 ====================
    per_row = 4 if len(algo_keys) > 4 else min(3, len(algo_keys))
    for start in range(0, len(rows), per_row):
        chunk = rows[start:start + per_row]
        cols = st.columns(per_row)
        for col, row in zip(cols, chunk):
            with col:
                st.markdown(f"**{row['算法']}**")
                img = row["_processed"]
                if img.ndim == 2 or img.shape[2] == 1:
                    st.image(img, use_container_width=True, clamp=True)
                else:
                    st.image(bgr_to_rgb(img), use_container_width=True)
                m_label = format_metric(row["MSE"], 1)
                p_label = format_metric(row["PSNR(dB)"], 2, " dB")
                s_label = format_metric(row["SSIM"], 4)
                st.caption(f"MSE {m_label} | PSNR {p_label} | SSIM {s_label}")

    # ==================== 指标汇总表 ====================
    st.subheader("📋 客观质量指标汇总")
    table = [
        {
            "算法": r["算法"],
            "耗时(ms)": r["耗时(ms)"],
            "MSE": format_metric(r["MSE"], 1),
            "PSNR(dB)": format_metric(r["PSNR(dB)"], 2),
            "SSIM": format_metric(r["SSIM"], 4),
        }
        for r in rows
    ]
    st.dataframe(table, use_container_width=True, hide_index=True)
