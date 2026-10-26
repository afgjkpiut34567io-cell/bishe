"""
侧边栏模块 - 算法选择、分类导航、参数面板、文件上传
"""

import streamlit as st
import numpy as np
from typing import Optional, Dict, Any, Tuple, Callable

from utils.config import (
    ALGORITHM_CATEGORIES, DEFAULT_PARAMS, SUPPORTED_FORMATS_UPLOAD
)
from data.teaching_content import TEACHING_CONTENT, ALGORITHM_NAMES
from utils.image_io import load_image

def render_sidebar() -> Tuple[
    Optional[np.ndarray],  # uploaded image
    Optional[str],          # selected algorithm key
    Dict[str, Any],         # algorithm parameters
]:
    """
    渲染侧边栏，返回 (上传的图像, 选中的算法, 参数字典)
    """
    with st.sidebar:
        st.title("🖼️ 图像处理平台")

        # ==================== 图像上传区 ====================
        uploaded_file = render_upload_section()

        # 加载图像
        image = None
        load_error = None
        if uploaded_file is not None:
            image, load_error = load_image(uploaded_file)
            if load_error:
                st.error(load_error)

        # ==================== 算法选择区 ====================
        algorithm_key = render_algorithm_selection(image)

        # ==================== 参数面板 ====================
        params = render_params_panel(algorithm_key)

        # ==================== 侧边栏底部信息 ====================
        render_sidebar_footer(image)

    return image, algorithm_key, params

def render_upload_section():
    """渲染图像上传区域"""
    st.header("📤 上传图像")

    # 示例图像选择
    use_sample = st.checkbox("使用示例图像", value=True,
                             help="使用内置示例图像进行算法演示")

    uploaded_file = None
    if not use_sample:
        uploaded_file = st.file_uploader(
            "选择图像文件",
            type=SUPPORTED_FORMATS_UPLOAD,
            help=f"支持格式：{', '.join(SUPPORTED_FORMATS_UPLOAD).upper()}"
        )

    if use_sample:
        st.caption("✅ 当前使用内置示例图像")
    elif uploaded_file is not None:
        st.caption(f"✅ 已加载：{uploaded_file.name}")
    else:
        st.caption("⚠️ 请上传图像或使用示例图像")

    return uploaded_file

def render_algorithm_selection(image: Optional[np.ndarray]) -> Optional[str]:
    """渲染算法分类导航和选择"""
    st.header("🔧 算法选择")

    # 分类下拉
    category_names = list(ALGORITHM_CATEGORIES.keys())
    selected_category = st.selectbox(
        "算法分类",
        category_names,
        format_func=lambda x: x,
        help="选择一个算法类别"
    )

    # 当前分类的算法
    cat_info = ALGORITHM_CATEGORIES[selected_category]
    algo_keys = cat_info["algorithms"]

    # 算法选择
    algo_display_names = [ALGORITHM_NAMES.get(k, k) for k in algo_keys]
    selected_display = st.selectbox(
        "具体算法",
        algo_display_names,
        help="选择一个具体的图像处理算法"
    )

    # 反查key
    idx = algo_display_names.index(selected_display)
    algorithm_key = algo_keys[idx]

    return algorithm_key

def render_params_panel(algorithm_key: Optional[str]) -> Dict[str, Any]:
    """根据选中的算法渲染参数面板

    通过 session_state 中的重置计数器控制所有参数控件的 key，
    点击「恢复默认」时计数器自增，控件被重建并回到默认值。
    """
    if algorithm_key is None:
        st.info("👈 请先在左侧选择一个算法")
        return {}

    st.header("⚙️ 参数调节")

    # 获取算法教学内容
    content = TEACHING_CONTENT.get(algorithm_key, {})
    param_defs = content.get("params", [])

    if not param_defs:
        st.caption("该算法无可调节参数（使用默认最优参数）")
        return DEFAULT_PARAMS.get(algorithm_key, {})

    # 重置计数器：点击恢复默认时 +1，迫使所有带 key 的控件重建
    reset_key = f"_reset_{algorithm_key}"
    if reset_key not in st.session_state:
        st.session_state[reset_key] = 0
    reset_suffix = st.session_state[reset_key]

    params = {}
    for pdef in param_defs:
        name = pdef["name"]
        label = pdef["label"]
        ptype = pdef["type"]
        args = pdef.get("args", {})
        key = f"{algorithm_key}_{name}_{reset_suffix}"

        if ptype == "slider":
            params[name] = st.slider(
                label,
                min_value=args.get("min_value", 0),
                max_value=args.get("max_value", 100),
                value=args.get("value", 0),
                step=args.get("step", 1),
                help=pdef.get("explanation", ""),
                key=key,
            )
            # 处理元组类型参数（如 ksize）
            if isinstance(args.get("value"), tuple):
                params[name] = (params[name], params[name])

        elif ptype == "select_slider":
            options = args.get("options", [])
            default_idx = options.index(args.get("value", options[0])) if args.get("value") in options else 0
            params[name] = st.select_slider(
                label,
                options=options,
                value=options[default_idx],
                help=pdef.get("explanation", ""),
                key=key,
            )

        elif ptype == "radio":
            options = args.get("options", [])
            format_func = args.get("format_func", None)
            params[name] = st.radio(
                label,
                options=options,
                index=options.index(args.get("value", options[0])),
                format_func=format_func,
                horizontal=True,
                help=pdef.get("explanation", ""),
                key=key,
            )

        elif ptype == "selectbox":
            options = args.get("options", [])
            default = args.get("value", options[0] if options else "")
            params[name] = st.selectbox(
                label,
                options=options,
                index=options.index(default) if default in options else 0,
                help=pdef.get("explanation", ""),
                key=key,
            )

        elif ptype == "number_input":
            params[name] = st.number_input(
                label,
                min_value=args.get("min_value", 0),
                max_value=args.get("max_value", 100),
                value=args.get("value", 0),
                step=args.get("step", 1),
                help=pdef.get("explanation", ""),
                key=key,
            )

    # 恢复默认参数按钮
    if st.button("↩️ 恢复默认参数", use_container_width=True,
                 help="将当前算法的所有参数重置为默认值"):
        st.session_state[reset_key] += 1
        st.rerun()

    return params

def render_sidebar_footer(image: Optional[np.ndarray]):
    """渲染侧边栏底部信息"""
    st.divider()

    if image is not None:
        h, w = image.shape[:2]
        st.caption(f"📐 图像尺寸：{w} × {h} px")

    st.caption("💡 提示：调整参数后处理结果自动更新")
    st.caption("📚 点击「教学面板」标签查看算法详解")

    # 算法统计
    total_algo = sum(
        len(v["algorithms"])
        for v in ALGORITHM_CATEGORIES.values()
    )
    st.caption(f"🔢 已集成 {total_algo} 种算法")
