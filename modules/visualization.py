"""
可视化辅助模块 - 使用Matplotlib进行算法步骤可视化
包含：直方图绘制、频域可视化、梯度方向图、步骤对比图
"""

import cv2
import numpy as np
import matplotlib
matplotlib.use("Agg")  # 非交互式后端
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from matplotlib.figure import Figure
from typing import List, Tuple, Optional
import io
from PIL import Image

from utils.image_io import to_grayscale

# ==================== 中文字体配置 ====================
def _setup_chinese_font():
    """检测并配置支持中文的字体"""
    # Windows常见中文字体
    cjk_candidates = [
        "Microsoft YaHei", "SimHei", "SimSun",
        "KaiTi", "FangSong", "Noto Sans CJK SC",
        "WenQuanYi Micro Hei", "WenQuanYi Zen Hei",
        "Source Han Sans SC", "AR PL UMing CN",
    ]
    available_fonts = {f.name for f in fm.fontManager.ttflist}

    for font_name in cjk_candidates:
        if font_name in available_fonts:
            plt.rcParams["font.sans-serif"] = [font_name, "DejaVu Sans"]
            plt.rcParams["axes.unicode_minus"] = False
            return font_name
    # 无中文字体时使用英文
    return None

_chinese_font = _setup_chinese_font()

# 根据是否有中文字体决定使用中文还是英文标签
_USE_CHINESE = _chinese_font is not None

# ==================== 标签映射 ====================
def _L(cn: str, en: str) -> str:
    """根据字体可用性返回中文或英文标签"""
    return cn if _USE_CHINESE else en

# ==================== Matplotlib全局样式配置 ====================
plt.rcParams.update({
    "figure.dpi": 120,
    "font.size": 10,
    "axes.titlesize": 12,
    "axes.labelsize": 10,
    "figure.titlesize": 14,
    "legend.fontsize": 9,
    "axes.grid": True,
    "grid.alpha": 0.3,
})

# 配色方案
COLORS = {
    "primary": "#2196F3",
    "secondary": "#FF9800",
    "accent": "#4CAF50",
    "warning": "#F44336",
    "dark": "#212121",
    "light": "#F5F5F5",
}

def _figure_to_image(fig: Figure) -> np.ndarray:
    """将Matplotlib Figure转换为OpenCV格式图像"""
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=120, bbox_inches="tight",
                facecolor="white", edgecolor="none")
    buf.seek(0)
    img_pil = Image.open(buf)
    img_np = np.array(img_pil)
    plt.close(fig)
    # RGB -> BGR for OpenCV
    return cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)

def plot_histogram_comparison(
    original: np.ndarray, processed: np.ndarray,
    title: str = "直方图对比"
) -> np.ndarray:
    """
    绘制处理前后的直方图对比
    """
    gray_orig = to_grayscale(original)
    gray_proc = to_grayscale(processed)

    fig, axes = plt.subplots(2, 2, figsize=(10, 6))

    # 原图
    rgb_orig = cv2.cvtColor(original, cv2.COLOR_BGR2RGB) if len(original.shape) == 3 else original
    axes[0, 0].imshow(rgb_orig, cmap="gray" if len(original.shape) == 2 else None)
    axes[0, 0].set_title(_L("原始图像", "Original Image"))
    axes[0, 0].axis("off")

    # 原图直方图
    axes[0, 1].hist(gray_orig.ravel(), bins=256, range=[0, 256],
                    color="#2196F3", alpha=0.7)
    axes[0, 1].set_title(_L("原始直方图", "Original Histogram"))
    axes[0, 1].set_xlim([0, 256])

    # 处理后图像
    rgb_proc = cv2.cvtColor(processed, cv2.COLOR_BGR2RGB) if len(processed.shape) == 3 else processed
    axes[1, 0].imshow(rgb_proc, cmap="gray" if len(processed.shape) == 2 else None)
    axes[1, 0].set_title(_L("处理后图像", "Processed Image"))
    axes[1, 0].axis("off")

    # 处理后直方图
    axes[1, 1].hist(gray_proc.ravel(), bins=256, range=[0, 256],
                    color="#FF9800", alpha=0.7)
    axes[1, 1].set_title(_L("处理后直方图", "Processed Histogram"))
    axes[1, 1].set_xlim([0, 256])

    fig.suptitle(title, fontsize=14, fontweight="bold")
    fig.tight_layout()
    return _figure_to_image(fig)

def plot_steps_grid(
    steps: List[Tuple[str, np.ndarray]],
    cols: int = 3,
    title: str = "算法步骤可视化"
) -> np.ndarray:
    """
    将算法步骤以网格形式可视化

    参数:
        steps: (步骤名称, 图像) 的列表
        cols: 每行列数
        title: 总标题
    返回: 包含步骤网格的BGR格式图像
    """
    n = len(steps)
    rows = (n + cols - 1) // cols

    fig, axes = plt.subplots(rows, cols, figsize=(4 * cols, 3.5 * rows))
    if rows == 1 and cols == 1:
        axes = np.array([[axes]])
    elif rows == 1:
        axes = axes.reshape(1, -1)
    elif cols == 1:
        axes = axes.reshape(-1, 1)

    for idx, (step_name, img) in enumerate(steps):
        r, c = idx // cols, idx % cols
        ax = axes[r, c]

        # 显示图像
        if len(img.shape) == 2:
            ax.imshow(img, cmap="gray")
        else:
            rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            ax.imshow(rgb)

        ax.set_title(step_name, fontsize=9)
        ax.axis("off")

    # 隐藏多余的子图
    for idx in range(n, rows * cols):
        r, c = idx // cols, idx % cols
        axes[r, c].axis("off")

    fig.suptitle(title, fontsize=14, fontweight="bold", y=1.01)
    fig.tight_layout()
    return _figure_to_image(fig)

def plot_gamma_curves(current_gamma: float = 1.0) -> np.ndarray:
    """
    绘制伽马校正曲线
    """
    fig, ax = plt.subplots(figsize=(8, 4))

    x = np.linspace(0, 1, 256)
    gamma_values = [0.25, 0.5, 1.0, 2.0, 4.0]

    for g in gamma_values:
        y = x ** (1.0 / g)
        label = f"γ = {g}"
        lw = 2.5 if abs(g - current_gamma) < 0.01 else 1.2
        alpha = 1.0 if abs(g - current_gamma) < 0.01 else 0.5
        ax.plot(x, y, label=label, linewidth=lw, alpha=alpha)

    ax.set_xlabel(_L("输入像素值 (归一化)", "Input Pixel Value (normalized)"))
    ax.set_ylabel(_L("输出像素值 (归一化)", "Output Pixel Value (normalized)"))
    ax.set_title(_L("伽马校正曲线", "Gamma Correction Curve"), fontweight="bold")
    ax.legend(loc="lower right")
    ax.set_xlim([0, 1])
    ax.set_ylim([0, 1])
    ax.set_aspect("equal")
    ax.grid(True, alpha=0.3)

    fig.tight_layout()
    return _figure_to_image(fig)

def plot_frequency_analysis(image: np.ndarray) -> np.ndarray:
    """
    绘制傅里叶频率域分析图
    """
    gray = to_grayscale(image)

    # 傅里叶变换
    dft = cv2.dft(np.float32(gray), flags=cv2.DFT_COMPLEX_OUTPUT)
    dft_shift = np.fft.fftshift(dft)
    magnitude = cv2.magnitude(dft_shift[:, :, 0], dft_shift[:, :, 1])
    magnitude_log = np.log(1 + magnitude)

    fig, axes = plt.subplots(1, 3, figsize=(12, 3.5))

    # 原图
    axes[0].imshow(gray, cmap="gray")
    axes[0].set_title(_L("原始图像 (空间域)", "Original Image (Spatial Domain)"))
    axes[0].axis("off")

    # 幅度谱
    im = axes[1].imshow(magnitude_log, cmap="hot")
    axes[1].set_title(_L("频率幅度谱 (对数)", "Frequency Magnitude Spectrum (log)"))
    axes[1].axis("off")
    plt.colorbar(im, ax=axes[1], fraction=0.046, pad=0.04)

    # 频率分布示意
    h, w = gray.shape
    y, x = np.mgrid[-h//2:h//2, -w//2:w//2]
    distances = np.sqrt(x**2 + y**2)

    # 按距离聚合频率能量
    max_dist = int(min(h, w) / 2)
    freq_energy = []
    for d in range(1, max_dist, 2):
        mask = (distances >= d) & (distances < d + 2)
        if mask.any():
            freq_energy.append(magnitude_log[mask].mean())

    axes[2].plot(range(1, len(freq_energy) + 1), freq_energy,
                 color="#2196F3", linewidth=2)
    axes[2].set_xlabel(_L("频率 (低频→高频)", "Frequency (Low→High)"))
    axes[2].set_ylabel(_L("平均幅度 (log)", "Avg Magnitude (log)"))
    axes[2].set_title(_L("频率能量分布", "Frequency Energy Distribution"))
    axes[2].fill_between(range(len(freq_energy)), freq_energy,
                          alpha=0.2, color="#2196F3")

    fig.tight_layout()
    return _figure_to_image(fig)
