"""
毕业论文插图生成脚本

程序化生成 10 张论文插图（图2-1 ~ 图6-2），复用系统真实算法输出 + matplotlib。
输出到 figures/ 目录，中文字体使用 SimHei 以匹配正文黑体。

用法：
    python build_thesis_figures.py
"""

import os
import sys

sys.stdout.reconfigure(encoding="utf-8")

import numpy as np
import cv2
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager

# ---- 中文字体（SimHei 匹配正文黑体） ----
_FONT = None
for _name in ("SimHei", "Microsoft YaHei", "SimSun"):
    if any(f.name == _name for f in font_manager.fontManager.ttflist):
        _FONT = _name
        break
if _FONT is None:
    _FONT = "DejaVu Sans"
plt.rcParams["font.sans-serif"] = [_FONT]
plt.rcParams["axes.unicode_minus"] = False

FIG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "figures")
os.makedirs(FIG_DIR, exist_ok=True)

DPI = 200
COLOR_PRIMARY = "#2C5F8A"
COLOR_ACCENT = "#E08A3C"


def _save(fig, name):
    path = os.path.join(FIG_DIR, name)
    fig.savefig(path, dpi=DPI, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"  [OK] {name}  ({os.path.getsize(path)//1024} KB)")


def _box(ax, xy, w, h, text, fc="#E8F0F8", ec=COLOR_PRIMARY, fs=11, bold=False):
    """在坐标轴上画一个带文字的圆角矩形框。"""
    from matplotlib.patches import FancyBboxPatch
    ax.add_patch(FancyBboxPatch(xy, w, h, boxstyle="round,pad=0.02",
                                fc=fc, ec=ec, lw=1.4))
    ax.text(xy[0] + w / 2, xy[1] + h / 2, text, ha="center", va="center",
            fontsize=fs, fontweight="bold" if bold else "normal")


def _arrow(ax, p0, p1, color=COLOR_PRIMARY):
    ax.annotate("", xy=p1, xytext=p0,
                arrowprops=dict(arrowstyle="-|>", color=color, lw=1.4))


# ==================== 图2-1 卷积示意 ====================
def fig2_1():
    fig, axes = plt.subplots(1, 3, figsize=(9, 3.4))
    # (a) 图像矩阵
    img_mat = np.array([
        [0, 0, 0, 0, 0],
        [0, 3, 4, 2, 0],
        [0, 1, 5, 4, 0],
        [0, 2, 3, 1, 0],
        [0, 0, 0, 0, 0],
    ])
    ax = axes[0]
    ax.imshow(img_mat, cmap="Greys", vmin=0, vmax=5)
    ax.set_xticks(range(5)); ax.set_yticks(range(5))
    ax.set_xticklabels([]); ax.set_yticklabels([])
    for i in range(5):
        for j in range(5):
            ax.text(j, i, str(img_mat[i, j]), ha="center", va="center",
                    color="white" if img_mat[i, j] <= 2 else "black", fontsize=9)
    ax.set_title("(a) 图像矩阵 f", fontsize=11)
    ax.grid(False)

    # (b) 卷积核
    kernel = np.array([[0, 1, 0], [1, -4, 1], [0, 1, 0]])
    ax = axes[1]
    ax.imshow(kernel, cmap="Greys", vmin=-4, vmax=4)
    ax.set_xticks(range(3)); ax.set_yticks(range(3))
    ax.set_xticklabels([]); ax.set_yticklabels([])
    for i in range(3):
        for j in range(3):
            ax.text(j, i, str(kernel[i, j]), ha="center", va="center",
                    color="white" if kernel[i, j] < 0 else "black", fontsize=9)
    ax.set_title("(b) 卷积核 w", fontsize=11)
    ax.grid(False)

    # (c) 卷积输出
    out = cv2.filter2D(img_mat.astype(np.float32), -1, kernel.astype(np.float32))
    ax = axes[2]
    im = ax.imshow(out, cmap="Greys")
    ax.set_xticks(range(5)); ax.set_yticks(range(5))
    ax.set_xticklabels([]); ax.set_yticklabels([])
    for i in range(5):
        for j in range(5):
            ax.text(j, i, f"{out[i, j]:.0f}", ha="center", va="center",
                    color="black", fontsize=8)
    ax.set_title("(c) 卷积结果 g = f * w", fontsize=11)
    ax.grid(False)
    fig.tight_layout()
    _save(fig, "fig2_1_卷积示意.png")


# ==================== 图3-1 系统用例图 ====================
def fig3_1():
    fig, ax = plt.subplots(figsize=(9, 4.2))
    ax.set_xlim(0, 12); ax.set_ylim(0, 6)
    ax.axis("off")

    # 系统边界
    from matplotlib.patches import Rectangle
    ax.add_patch(Rectangle((1.5, 0.5), 9.5, 5.0, fill=False, ec="gray",
                           ls="--", lw=1.2))
    ax.text(11.0, 5.25, "交互式演示系统", ha="center", fontsize=11, color="gray")

    # 参与者
    ax.add_patch(plt.Circle((0.8, 3.2), 0.25, fc=COLOR_ACCENT, ec="k"))
    ax.plot([0.8, 0.8], [2.95, 2.3], color="k", lw=1.4)
    ax.plot([0.55, 1.05], [2.55, 2.55], color="k", lw=1.4)
    ax.plot([0.8, 0.6], [2.3, 1.9], color="k", lw=1.4)
    ax.plot([0.8, 1.0], [2.3, 1.9], color="k", lw=1.4)
    ax.text(0.8, 1.6, "用户", ha="center", fontsize=11)

    # 用例
    cases = [
        ("上传/选取图像", 3.2, 4.6),
        ("选择算法", 5.4, 4.6),
        ("调节参数", 7.6, 4.6),
        ("查看处理结果", 9.8, 4.6),
        ("查看步骤可视化", 4.3, 2.0),
        ("查看教学资料", 6.5, 2.0),
        ("下载结果", 8.7, 2.0),
    ]
    for text, cx, cy in cases:
        ax.add_patch(plt.Circle((cx, cy), 0.95, fill=False, ec=COLOR_PRIMARY, lw=1.4))
        ax.text(cx, cy, text, ha="center", va="center", fontsize=10)

    # 参与者 → 用例
    _arrow(ax, (1.05, 3.2), (2.25, 4.6))
    _arrow(ax, (1.05, 3.2), (3.35, 2.0))
    fig.tight_layout()
    _save(fig, "fig3_1_系统用例图.png")


# ==================== 图4-1 系统四层架构图 ====================
def fig4_1():
    fig, ax = plt.subplots(figsize=(9, 5.0))
    ax.set_xlim(0, 10); ax.set_ylim(0, 9)
    ax.axis("off")

    layers = [
        ("UI 层（界面层）", "侧边栏 · 结果预览 · 步骤可视化 · 教学面板", "#FBE9D0"),
        ("可视化层", "直方图对比 · 步骤网格 · 伽马曲线 · 频率分析", "#E8F0F8"),
        ("算法层", "滤波 · 增强 · 边缘检测 · 形态学 · 分割 · 变换（30 种算法）", "#EAF5EA"),
        ("工具层（基础支撑）", "图像读写 image_io · 性能计时 performance", "#F2F2F2"),
    ]
    y = 7.2
    for title, detail, fc in layers:
        _box(ax, (0.8, y), 8.4, 1.4, "", fc=fc, ec=COLOR_PRIMARY)
        ax.text(1.1, y + 1.05, title, fontsize=12, fontweight="bold", va="center")
        ax.text(1.1, y + 0.45, detail, fontsize=9.5, color="#333", va="center")
        y -= 1.75

    # 单向依赖箭头（自底向上）
    for yi in (1.2, 2.95, 4.7):
        _arrow(ax, (5.0, yi), (5.0, yi + 0.5))
    ax.text(6.2, 6.4, "上层调用下层接口\n（单向依赖）", fontsize=9, color=COLOR_PRIMARY, va="center")
    fig.tight_layout()
    _save(fig, "fig4_1_四层架构图.png")


# ==================== 图4-2 系统数据流图 ====================
def fig4_2():
    fig, ax = plt.subplots(figsize=(9.5, 3.0))
    ax.set_xlim(0, 13); ax.set_ylim(0, 3)
    ax.axis("off")

    steps = [
        ("图像输入", "上传/示例\nBGR→NumPy"),
        ("算法选择", "类别→算法"),
        ("参数调节", "滑块/下拉\n实时更新"),
        ("算法执行", "registry 分发\n计时"),
        ("结果展示", "预览·可视化"),
        ("结果输出", "下载 PNG/JPG"),
    ]
    n = len(steps)
    bw = 1.85
    gap = 0.32
    x = 0.4
    for i, (title, detail) in enumerate(steps):
        _box(ax, (x, 0.9), bw, 1.4, "", fc="#E8F0F8" if i % 2 == 0 else "#EAF5EA",
             ec=COLOR_PRIMARY)
        ax.text(x + bw / 2, 1.9, title, ha="center", va="center", fontsize=11, fontweight="bold")
        ax.text(x + bw / 2, 1.15, detail, ha="center", va="center", fontsize=8.5, color="#333")
        if i < n - 1:
            _arrow(ax, (x + bw + 0.02, 1.6), (x + bw + gap - 0.02, 1.6))
        x += bw + gap
    fig.tight_layout()
    _save(fig, "fig4_2_数据流图.png")


# ==================== 图4-3 界面布局示意图 ====================
def fig4_3():
    fig, ax = plt.subplots(figsize=(9, 5.2))
    ax.set_xlim(0, 12); ax.set_ylim(0, 8)
    ax.axis("off")

    # 侧边栏
    _box(ax, (0.4, 0.4), 3.6, 7.2, "", fc="#F5F5F5", ec="#888")
    ax.text(2.2, 7.3, "侧边栏", ha="center", fontsize=11, fontweight="bold")
    sub = [("图像上传区", 6.2), ("算法导航区", 4.6), ("参数配置区", 2.4)]
    for name, yy in sub:
        _box(ax, (0.7, yy - 0.7), 3.0, 1.0, name, fc="white", ec=COLOR_PRIMARY, fs=9.5)
    ax.text(2.2, 0.8, "使用示例图像", ha="center", fontsize=8, color="#666")

    # 主内容区
    _box(ax, (4.3, 0.4), 7.3, 7.2, "", fc="white", ec=COLOR_PRIMARY)
    ax.text(8.0, 7.3, "主内容区（标签页）", ha="center", fontsize=11, fontweight="bold")
    tabs = [("原图/结果预览", 5.9), ("算法对比", 4.4), ("步骤可视化", 2.9), ("教学面板", 1.4)]
    for name, yy in tabs:
        _box(ax, (4.7, yy - 0.55), 3.2, 0.9, name, fc="#E8F0F8", ec=COLOR_PRIMARY, fs=9)
    ax.text(8.0, 0.8, "性能/信息栏：耗时 · 尺寸", ha="center", fontsize=8.5, color="#666")
    fig.tight_layout()
    _save(fig, "fig4_3_界面布局图.png")


# ==================== 图5-1 示例图像 ====================
def _load_sample():
    import app
    return app._create_sample_image()


def fig5_1():
    img = _load_sample()  # BGR
    rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.imshow(rgb)
    ax.axis("off")
    fig.tight_layout(pad=0.2)
    _save(fig, "fig5_1_示例图像.png")


# ==================== 算法效果对比（图5-2 / 5-3） ====================
def _run(key, params):
    from modules import registry
    fn = registry.ALGORITHM_FUNCTIONS[key]
    return fn(_load_sample(), params)


def _alg_grid(items, name, cols=3):
    """items: [(标题, BGR图)]，其中第一项为原图。"""
    fig, axes = plt.subplots(2, cols, figsize=(11, 7))
    for ax, (title, img) in zip(axes.ravel(), items):
        ax.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        ax.set_title(title, fontsize=10)
        ax.axis("off")
    # 隐藏多余子图
    for ax in axes.ravel()[len(items):]:
        ax.axis("off")
    fig.tight_layout(pad=0.4)
    _save(fig, name)


def fig5_2():
    orig = _load_sample()
    items = [
        ("原图", orig),
        ("高斯滤波", _run("gaussian_blur", {"ksize": (7, 7), "sigma_x": 2.0})),
        ("中值滤波", _run("median_blur", {"ksize": 7})),
        ("双边滤波", _run("bilateral_filter", {"d": 9, "sigma_color": 75, "sigma_space": 75})),
        ("直方图均衡化", _run("histogram_equalization", {})),
        ("伽马校正 γ=1.8", _run("gamma_correction", {"gamma": 1.8})),
    ]
    _alg_grid(items, "fig5_2_滤波与增强对比.png")


def fig5_3():
    orig = _load_sample()
    items = [
        ("原图", orig),
        ("Canny 边缘检测", _run("canny_edge", {"threshold1": 50, "threshold2": 150})),
        ("Sobel 边缘检测", _run("sobel_edge", {"ksize": 3, "dx": 1, "dy": 1})),
        ("腐蚀", _run("erosion", {"ksize": 5, "iterations": 1})),
        ("膨胀", _run("dilation", {"ksize": 5, "iterations": 1})),
        ("形态学梯度", _run("morphological_gradient", {"ksize": 3})),
    ]
    _alg_grid(items, "fig5_3_边缘与形态学对比.png")


# ==================== 图6-1 耗时对比（柱状图） ====================
def fig6_1():
    data = [
        ("傅里叶变换", 15.8), ("双边滤波", 12.5), ("Canny", 3.8),
        ("自适应阈值", 2.6), ("CLAHE", 2.3), ("Sobel", 2.1),
        ("中值滤波", 1.5), ("高斯滤波", 1.2), ("Otsu", 1.0),
        ("腐蚀", 0.9), ("直方图均衡", 0.8), ("伽马校正", 0.4),
    ]
    data.sort(key=lambda x: x[1])
    names = [d[0] for d in data]
    vals = [d[1] for d in data]
    fig, ax = plt.subplots(figsize=(8.5, 4.6))
    colors = [COLOR_ACCENT if v > 3 else COLOR_PRIMARY for v in vals]
    bars = ax.barh(names, vals, color=colors, edgecolor="white")
    ax.set_xlabel("中位数耗时 (ms)", fontsize=11)
    ax.set_xlim(0, 18)
    for b, v in zip(bars, vals):
        ax.text(v + 0.2, b.get_y() + b.get_height() / 2, f"{v:.1f}",
                va="center", fontsize=9)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.tight_layout()
    _save(fig, "fig6_1_耗时对比图.png")


# ==================== 图6-2 耗时-分辨率关系 ====================
def _measure(key, params, resolutions):
    """实测算法在不同分辨率下的中位数耗时(ms)。"""
    from modules import registry
    import time, statistics
    fn = registry.ALGORITHM_FUNCTIONS[key]
    base = _load_sample()
    out = []
    for (w, h) in resolutions:
        img = cv2.resize(base, (w, h))
        # 预热
        fn(img, params)
        samples = []
        for _ in range(5):
            t0 = time.perf_counter()
            fn(img, params)
            samples.append((time.perf_counter() - t0) * 1000)
        out.append(round(statistics.median(samples), 2))
    return out


def fig6_2():
    res = [(640, 480), (800, 600), (1280, 960)]
    labels = ["640×480", "800×600", "1280×960"]
    algos = [
        ("高斯滤波", "gaussian_blur", {"ksize": (7, 7), "sigma_x": 2.0}),
        ("Canny", "canny_edge", {"threshold1": 50, "threshold2": 150}),
        ("双边滤波", "bilateral_filter", {"d": 9, "sigma_color": 75, "sigma_space": 75}),
        ("傅里叶变换", "fourier_transform", {}),
    ]
    fig, ax = plt.subplots(figsize=(8, 4.6))
    markers = ["o", "s", "^", "D"]
    for (label, key, params), mk in zip(algos, markers):
        ts = _measure(key, params, res)
        ax.plot(range(len(res)), ts, marker=mk, label=label, linewidth=1.8)
    ax.set_xticks(range(len(res)))
    ax.set_xticklabels(labels, fontsize=10)
    ax.set_ylabel("中位数耗时 (ms)", fontsize=11)
    ax.set_xlabel("图像分辨率（像素）", fontsize=11)
    ax.legend(fontsize=9)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.tight_layout()
    _save(fig, "fig6_2_耗时分辨率关系.png")


def main():
    print("开始生成论文插图...")
    fig2_1()
    fig3_1()
    fig4_1()
    fig4_2()
    fig4_3()
    fig5_1()
    fig5_2()
    fig5_3()
    fig6_1()
    fig6_2()
    print("全部插图生成完成。")


if __name__ == "__main__":
    main()
