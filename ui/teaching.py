"""
教学面板模块 - 展示算法原理、核心代码、参数解释和应用场景
"""

import streamlit as st
from typing import Optional, Dict, Any

from data.teaching_content import TEACHING_CONTENT

def render_teaching_panel(
    algorithm_key: Optional[str],
    params: Optional[Dict[str, Any]] = None,
):
    """
    渲染教学面板

    参数:
        algorithm_key: 算法标识符
        params: 当前参数值（用于高亮显示）
    """
    st.header("📚 教学面板")

    if algorithm_key is None:
        st.info("👈 请先在左侧选择一个算法，然后查看其教学资料")
        return

    content = TEACHING_CONTENT.get(algorithm_key)
    if content is None:
        st.warning("该算法的教学资料正在编写中...")
        return

    # 算法名称
    st.subheader(f"📖 {content['name']}")

    # 分类标签
    st.caption(f"📂 所属类别：{content['category']}")

    # ==================== 标签页 ====================
    tab_principle, tab_code, tab_params, tab_scenarios = st.tabs([
        "💡 算法原理",
        "💻 代码实现",
        "⚙️ 参数详解",
        "🎯 应用场景",
    ])

    with tab_principle:
        _render_principle(content)

    with tab_code:
        _render_code(content)

    with tab_params:
        _render_parameter_details(content, algorithm_key, params)

    with tab_scenarios:
        _render_scenarios(content)

def _render_principle(content: Dict[str, Any]):
    """渲染算法原理"""
    principle = content.get("principle", "")
    if principle:
        st.markdown(principle, unsafe_allow_html=False)
    else:
        st.info("该算法的原理说明正在编写中...")

def _render_code(content: Dict[str, Any]):
    """渲染核心代码"""
    code = content.get("code", "")
    if code:
        st.markdown("### 核心代码实现")
        st.code(code.strip(), language="python")

        # 添加依赖说明
        st.caption("💡 以上代码使用 OpenCV (cv2) 和 NumPy 实现，核心逻辑清晰易懂")
        st.caption("💡 实际平台代码中包含更完善的错误处理和参数验证")
    else:
        st.info("代码示例正在编写中...")

def _render_parameter_details(
    content: Dict[str, Any],
    algorithm_key: str,
    current_params: Optional[Dict[str, Any]],
):
    """渲染参数详解"""
    param_defs = content.get("params", [])

    if not param_defs:
        st.info("该算法没有可调节参数，使用内部最优默认值")
        return

    for i, pdef in enumerate(param_defs):
        name = pdef.get("name", "")
        label = pdef.get("label", f"参数{i+1}")
        explanation = pdef.get("explanation", "")

        # 当前值
        current_val = "未设置"
        if current_params and name in current_params:
            current_val = str(current_params[name])

        # 参数卡片
        with st.container():
            col_icon, col_content = st.columns([0.05, 0.95])

            with col_icon:
                st.markdown("🔹")

            with col_content:
                st.markdown(f"**{label}** `{name}`")
                st.caption(f"当前值：{current_val}")
                if explanation:
                    st.markdown(explanation)

            if i < len(param_defs) - 1:
                st.divider()

def _render_scenarios(content: Dict[str, Any]):
    """渲染应用场景"""
    scenarios = content.get("scenarios", [])

    if not scenarios:
        st.info("应用场景说明正在编写中...")
        return

    st.markdown("### 典型应用场景")
    for scenario in scenarios:
        st.markdown(f"- {scenario}")

    st.divider()
    st.caption("💡 这些场景展示了算法在工业界和学术界的实际应用价值")

def render_quick_guide():
    """渲染快速入门指南"""
    st.header("🚀 快速入门指南")

    with st.expander("📖 如何使用本平台？", expanded=True):
        st.markdown("""
        ### 三步上手

        1. **📤 上传图像**
           - 使用左侧面板上传您的图像文件（支持 JPG/PNG/BMP/TIFF）
           - 或勾选「使用示例图像」直接体验

        2. **🔧 选择算法**
           - 从左栏分类中选择一个算法类别（如"滤波算法"）
           - 然后选择具体算法（如"高斯滤波"）

        3. **⚙️ 调节参数**
           - 在左侧参数面板中拖动滑块
           - 右侧预览区会**实时更新**处理结果
           - 切换到「教学面板」查看算法原理

        ### 界面说明
        | 区域 | 功能 |
        |------|------|
        | 📸 处理结果预览 | 原图 vs 处理后对比，性能指标 |
        | 🔬 算法步骤可视化 | 中间处理步骤、直方图、数据曲线 |
        | 📚 教学面板 | 算法原理、代码实现、参数详解、应用场景 |
        """)

    with st.expander("🎯 推荐学习路径"):
        st.markdown("""
        ### 初学者路径
        1. 📊 **滤波算法**（高斯滤波 → 中值滤波 → 均值滤波）
           → 理解卷积和空间滤波的基本概念
        2. 🎨 **图像增强**（对比度亮度 → 直方图均衡化 → CLAHE）
           → 理解直方图和像素值变换
        3. 📏 **边缘检测**（Sobel → Canny → Laplacian）
           → 理解梯度和边缘检测原理
        4. 🔲 **形态学操作**（腐蚀 → 膨胀 → 开闭运算）
           → 理解基于形状的图像处理

        ### 进阶路径
        1. 🌟 **双边滤波** → 理解保边滤波的高级概念
        2. 🔍 **反锐化掩膜** → 专业级图像锐化
        3. 🔄 **傅里叶变换** → 频率域分析
        4. 🎯 **Otsu二值化** → 自动阈值算法
        """)

    with st.expander("📊 算法速查表"):
        from utils.config import ALGORITHM_CATEGORIES
        for cat_name, cat_info in ALGORITHM_CATEGORIES.items():
            st.markdown(f"**{cat_name}**")
            from data.teaching_content import ALGORITHM_NAMES
            algos = [
                f"`{ALGORITHM_NAMES.get(k, k)}`"
                for k in cat_info["algorithms"]
            ]
            st.markdown(" · ".join(algos))
