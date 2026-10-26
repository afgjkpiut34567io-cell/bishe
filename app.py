"""
图像处理算法交互式演示与教学平台 - 主应用入口

基于 Streamlit + OpenCV + NumPy + Matplotlib 构建
"""

import streamlit as st
import numpy as np
import cv2
import time
from typing import Optional, Dict, Any, Callable

# ==================== 页面配置 ====================
st.set_page_config(
    page_title="图像处理算法交互式演示与教学平台",
    page_icon="🖼️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ==================== 导入模块 ====================
from utils.config import DEFAULT_PARAMS
from utils.image_io import (
    load_image, bgr_to_rgb, image_to_bytes,
    resize_for_preview, to_grayscale, ensure_3channel,
    Timer,
)
from utils.performance import ProcessingTimer

from data.teaching_content import TEACHING_CONTENT

# 算法模块（注册表见 modules/registry.py，与对比模式共享同一数据源）
from modules.registry import ALGORITHM_FUNCTIONS

# UI模块
from ui.sidebar import render_sidebar
from ui.preview import render_preview_panel, render_image_info_expander
from ui.steps import render_steps_visualization
from ui.teaching import render_teaching_panel, render_quick_guide
from ui.compare import render_compare_tab

# ==================== 示例图像生成 ====================
def _create_sample_image() -> np.ndarray:
    """
    生成内置示例图像 - 包含多种视觉元素的合成图像
    用于展示各种算法的效果。使用 NumPy 向量化替代逐像素循环，提升生成速度。
    """
    rng = np.random.default_rng(42)  # 固定种子，保证示例图每次一致
    h, w = 600, 800
    img = np.full((h, w, 3), 240, dtype=np.uint8)  # 浅灰背景

    # ---- 左侧：彩色渐变区域（向量化） ----
    gradient = np.linspace(0, 255, 400, dtype=np.uint8)
    img[50:250, 50:450, 0] = gradient                       # B
    img[50:250, 50:450, 1] = 255 - gradient                 # G
    img[50:250, 50:450, 2] = 128                            # R

    # ---- 右侧：几何图形 ----
    # 红色圆
    cv2.circle(img, (580, 150), 60, (50, 50, 220), -1)
    cv2.circle(img, (580, 150), 60, (0, 0, 0), 2)

    # 绿色矩形
    cv2.rectangle(img, (480, 250), (680, 350), (50, 180, 50), -1)
    cv2.rectangle(img, (480, 250), (680, 350), (0, 0, 0), 2)

    # 蓝色三角形
    pts = np.array([[530, 500], [630, 400], [730, 500]], dtype=np.int32)
    cv2.fillPoly(img, [pts], (200, 100, 50))
    cv2.polylines(img, [pts], True, (0, 0, 0), 2)

    # ---- 中间：文字 ----
    cv2.putText(img, "Image Processing", (200, 320),
                cv2.FONT_HERSHEY_SIMPLEX, 1.2, (30, 30, 30), 2)
    cv2.putText(img, "OpenCV + Streamlit", (200, 370),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (60, 60, 60), 2)

    # ---- 底部：灰度条纹（向量化） ----
    for i in range(8):
        val = i * 32
        x0, x1 = 50 + i * 90, 130 + i * 90
        cv2.rectangle(img, (x0, 500), (x1, 560), (val, val, val), -1)
        cv2.rectangle(img, (x0, 500), (x1, 560), (0, 0, 0), 1)

    # ---- 添加纹理（小圆点，向量化坐标生成） ----
    n_dots = 100
    xs = rng.integers(50, 750, size=n_dots)
    ys = rng.integers(50, 550, size=n_dots)
    radii = rng.integers(2, 6, size=n_dots)
    colors = rng.integers(30, 220, size=(n_dots, 3))
    for x, y, r, c in zip(xs, ys, radii, colors):
        cv2.circle(img, (int(x), int(y)), int(r), tuple(int(v) for v in c), -1)

    # ---- 添加椒盐噪声（向量化） ----
    n_noise = 300
    nx = rng.integers(0, w, size=n_noise)
    ny = rng.integers(0, h, size=n_noise)
    is_salt = rng.random(n_noise) < 0.5
    img[ny[is_salt], nx[is_salt]] = [255, 255, 255]
    img[ny[~is_salt], nx[~is_salt]] = [0, 0, 0]

    return img

# ==================== 会话状态初始化 ====================
def init_session_state():
    """初始化Streamlit会话状态"""
    defaults = {
        "original_image": None,
        "processed_image": None,
        "current_algorithm": None,
        "current_params": {},
        "processing_timer": ProcessingTimer(),
        "elapsed_ms": 0.0,
        "sample_image": None,
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


# ==================== 图像处理引擎 ====================
@st.cache_data(show_spinner=False)
def _run_algorithm(
    image: np.ndarray,
    algorithm_key: str,
    params: Dict[str, Any],
) -> tuple:
    """
    带缓存的算法执行核心。

    Streamlit 每次交互都会重跑脚本，若无缓存则拖动任一滑块都会
    对整幅图重新计算。st.cache_data 的哈希器可直接处理
    ndarray 与 dict（按内容哈希），无需手动序列化。

    注意：传入的 image 为只读语义——缓存命中时返回的可能是共享的
    数组对象，调用方不得原地修改。
    """
    algo_func = ALGORITHM_FUNCTIONS.get(algorithm_key)
    if algo_func is None:
        return image.copy(), 0.0

    with Timer() as timer:
        result = algo_func(image, params)

    if result.dtype != np.uint8:
        result = np.clip(result, 0, 255).astype(np.uint8)
    return result, timer.elapsed_ms

def process_image(
    image: np.ndarray,
    algorithm_key: str,
    params: Dict[str, Any],
) -> tuple:
    """
    执行图像处理算法并返回结果和耗时

    参数:
        image: 输入图像 (BGR)
        algorithm_key: 算法标识符
        params: 算法参数
    返回:
        (processed_image, elapsed_ms)
    """
    if ALGORITHM_FUNCTIONS.get(algorithm_key) is None:
        return image, 0.0

    try:
        # image.copy() 保护原图不被算法原地修改；
        # 结果不再二次拷贝——所有算法均返回新数组，且下游仅只读使用（显示/计算指标）。
        result, elapsed = _run_algorithm(image.copy(), algorithm_key, params)
        return result, elapsed
    except Exception as e:
        # 异常时返回原图并给出错误信息
        st.error(f"处理出错：{str(e)}")
        return image, 0.0

# ==================== 主页面布局 ====================
def main():
    """主应用入口"""
    init_session_state()

    # ==================== 侧边栏 ====================
    image, algorithm_key, params = render_sidebar()

    # 更新会话状态
    if image is not None:
        st.session_state.original_image = image

    # 判断是否使用示例图像
    if st.session_state.original_image is None:
        if st.session_state.sample_image is None:
            st.session_state.sample_image = _create_sample_image()
        st.session_state.original_image = st.session_state.sample_image

    original = st.session_state.original_image

    # ==================== 算法执行 ====================
    if algorithm_key and original is not None:
        # 合并默认参数和用户参数
        merged_params = DEFAULT_PARAMS.get(algorithm_key, {}).copy()
        merged_params.update(params)

        # 检查参数是否变化
        params_changed = (
            st.session_state.current_algorithm != algorithm_key
            or st.session_state.current_params != merged_params
        )

        if params_changed:
            processed, elapsed_ms = process_image(original, algorithm_key, merged_params)
            st.session_state.processed_image = processed
            st.session_state.current_algorithm = algorithm_key
            st.session_state.current_params = merged_params
            st.session_state.elapsed_ms = elapsed_ms
            st.session_state.processing_timer.record(elapsed_ms)

    processed = st.session_state.processed_image
    current_algo = st.session_state.current_algorithm
    elapsed_ms = st.session_state.elapsed_ms

    # 获取算法显示名称
    algo_display_name = ""
    if current_algo:
        content = TEACHING_CONTENT.get(current_algo, {})
        algo_display_name = content.get("name", current_algo)

    # ==================== 主内容区 ====================
    # 顶部标题
    if current_algo:
        st.title(f"🔬 {algo_display_name}")
    else:
        st.title("🖼️ 图像处理算法交互式演示与教学平台")

    # 如果没有选择算法，显示入门指南
    if not current_algo:
        render_quick_guide()
        # 仍然显示原图
        if original is not None:
            st.divider()
            st.header("📷 当前图像")
            st.image(bgr_to_rgb(resize_for_preview(original)),
                     use_container_width=True)
        return

    # ==================== 内容标签页 ====================
    tab1, tab2, tab3, tab4 = st.tabs([
        "📸 处理结果预览",
        "🔬 算法步骤可视化",
        "📚 教学面板",
        "🆚 算法对比",
    ])

    with tab1:
        render_preview_panel(
            original=original,
            processed=processed,
            algorithm_name=algo_display_name,
            elapsed_ms=elapsed_ms,
            processing_timer=st.session_state.processing_timer,
        )
        render_image_info_expander(original, processed)

    with tab2:
        render_steps_visualization(
            original=original,
            processed=processed,
            algorithm_key=current_algo,
            params=st.session_state.current_params,
        )

    with tab3:
        render_teaching_panel(
            algorithm_key=current_algo,
            params=st.session_state.current_params,
        )

    with tab4:
        render_compare_tab(
            original=original,
            current_algorithm=current_algo,
        )

    # ==================== 底部信息栏 ====================
    st.divider()
    col_footer1, col_footer2, col_footer3 = st.columns(3)
    with col_footer1:
        st.caption("🖼️ 图像处理算法交互式演示与教学平台 v1.0")
    with col_footer2:
        st.caption(f"⚡ 已集成 {len(ALGORITHM_FUNCTIONS)} 种算法 | 基于 OpenCV + Streamlit")
    with col_footer3:
        st.caption(f"📊 本次会话处理次数：{len(st.session_state.processing_timer.history)}")

# ==================== 启动 ====================
if __name__ == "__main__":
    main()
