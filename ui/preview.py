"""
预览模块 - 显示处理前后的图像对比和处理性能指标
"""
import streamlit as st
import numpy as np
import cv2
import time
from typing import Optional, Tuple

from utils.image_io import (
    bgr_to_rgb, image_to_bytes, get_image_info, Timer
)
from utils.performance import ProcessingTimer
from ui.compare import compute_quality_metrics, format_metric

def render_preview_panel(
    original: np.ndarray,
    processed: Optional[np.ndarray],
    algorithm_name: str,
    elapsed_ms: float = 0.0,
    processing_timer: Optional[ProcessingTimer] = None,
):
    """
    渲染图像预览面板：原图 vs 处理后对比

    参数:
        original: 原始图像 (BGR)
        processed: 处理后的图像 (BGR)
        algorithm_name: 算法显示名称
        elapsed_ms: 本次处理耗时(ms)
        processing_timer: 性能统计器
    """
    st.header("📸 处理结果预览")

    if processed is None:
        # 只显示原图
        _display_single_image(original, "原始图像")
        return

    # ==================== 性能指标 ====================
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("⚡ 本次耗时", f"{elapsed_ms:.0f}ms",
                  delta=None if elapsed_ms <= 300 else f"{elapsed_ms - 300:.0f}ms 超标",
                  delta_color="off" if elapsed_ms <= 300 else "inverse")
    with col2:
        if processing_timer and processing_timer.history:
            st.metric("📊 平均耗时", f"{processing_timer.avg_time_ms:.0f}ms")
    with col3:
        if processing_timer and len(processing_timer.history) > 1:
            st.metric("📈 处理次数", len(processing_timer.history))
    with col4:
        # 响应状态
        status = "✅ 流畅" if elapsed_ms <= 300 else "⚠️ 稍慢"
        st.metric("📶 状态", status)

    # ==================== 原图 vs 处理后对比 ====================
    col_img1, col_img2 = st.columns(2)

    with col_img1:
        st.markdown("**📷 原始图像**")
        st.image(
            bgr_to_rgb(original),
            use_container_width=True,
        )
        info = get_image_info(original)
        st.caption(f"尺寸：{info['尺寸']} | 通道数：{info['通道数']}")

    with col_img2:
        st.markdown(f"**✨ 处理后 ({algorithm_name})**")
        # 判断结果是否是灰度图
        if len(processed.shape) == 2 or (
            len(processed.shape) == 3 and processed.shape[2] == 1
        ):
            st.image(processed, use_container_width=True, clamp=True)
        else:
            st.image(
                bgr_to_rgb(processed),
                use_container_width=True,
            )
        info = get_image_info(processed)
        st.caption(f"尺寸：{info['尺寸']} | 通道数：{info['通道数']}")

    # ==================== 客观质量指标 ====================
    metrics = compute_quality_metrics(original, processed)
    if metrics is not None:
        mcol1, mcol2, mcol3 = st.columns(3)
        with mcol1:
            st.metric("🎯 MSE 均方误差", format_metric(metrics["mse"], 1))
        with mcol2:
            st.metric("📏 PSNR 峰值信噪比", format_metric(metrics["psnr"], 2, " dB"))
        with mcol3:
            st.metric("🧬 SSIM 结构相似度", format_metric(metrics["ssim"], 4))
        st.caption(
            "指标衡量处理后与原图的逐像素相似度：MSE 越小 / PSNR、SSIM 越大越接近原图。"
            "边缘检测、阈值分割等输出二值图的算法数值天然偏低。"
        )
    else:
        st.caption("ℹ️ 处理后图像与原图尺寸不一致（如缩放、仿射变换），无法计算逐像素质量指标。")

    # ==================== 下载按钮 ====================
    render_download_button(processed, algorithm_name)

def _display_single_image(image: np.ndarray, caption: str):
    """显示单张图像（无对比时）"""
    st.image(bgr_to_rgb(image), caption=caption, use_container_width=True)

def render_download_button(processed: np.ndarray, algorithm_name: str):
    """渲染下载按钮行：PNG / JPG / TIFF 三种格式"""
    col_btn1, col_btn2, col_btn3 = st.columns(3)

    safe_name = algorithm_name.replace(" ", "_").replace("(", "").replace(")", "")

    with col_btn1:
        png_bytes = image_to_bytes(processed, "PNG")
        st.download_button(
            label="💾 下载 PNG",
            data=png_bytes,
            file_name=f"processed_{safe_name}.png",
            mime="image/png",
            use_container_width=True,
        )

    with col_btn2:
        jpg_bytes = image_to_bytes(processed, "JPG")
        st.download_button(
            label="💾 下载 JPG",
            data=jpg_bytes,
            file_name=f"processed_{safe_name}.jpg",
            mime="image/jpeg",
            use_container_width=True,
        )

    with col_btn3:
        # TIFF 无损下载
        tiff_bytes = image_to_bytes(processed, "TIFF")
        st.download_button(
            label="💾 下载 TIFF",
            data=tiff_bytes,
            file_name=f"processed_{safe_name}.tiff",
            mime="image/tiff",
            use_container_width=True,
        )

def render_image_info_expander(original: np.ndarray, processed: Optional[np.ndarray]):
    """渲染图像详细信息展开区域"""
    with st.expander("📋 图像详细信息"):
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**原始图像**")
            info = get_image_info(original)
            for k, v in info.items():
                st.text(f"{k}: {v}")

        if processed is not None:
            with col2:
                st.markdown("**处理后图像**")
                info = get_image_info(processed)
                for k, v in info.items():
                      st.text(f"{k}: {v}")
