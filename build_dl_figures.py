"""
深度学习算法论文插图生成脚本

生成 3 张深度学习相关插图（复用真实模型输出）：
  图5-4 深度学习图像理解算法处理效果（图像分类 + 语义分割）
  图5-5 超分辨率重建与 CIFAR-10 分类效果
  图5-6 深度学习模型训练过程曲线（CIFAR-10 + SRCNN）

输出到 figures/，使用 SimHei 中文字体，DPI=200。
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

# 中文字体
for fp in [r"C:\Windows\Fonts\simhei.ttf", r"C:\Windows\Fonts\msyh.ttc"]:
    if os.path.exists(fp):
        font_manager.fontManager.addfont(fp)
plt.rcParams["font.sans-serif"] = ["SimHei", "Microsoft YaHei"]
plt.rcParams["axes.unicode_minus"] = False

FIG_DIR = "figures"
os.makedirs(FIG_DIR, exist_ok=True)

# 导入项目模块（示例图 + 深度学习算法）
import app  # noqa: E402
from modules.deep_learning import (  # noqa: E402
    image_classification, semantic_segmentation,
    super_resolution, cifar10_classification,
)

def bgr2rgb(img):
    return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

def _save(fig, name):
    path = os.path.join(FIG_DIR, name)
    fig.savefig(path, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"[OK] {path}")

# ==================== 示例图与 CIFAR 测试图 ====================

sample = app._create_sample_image()          # BGR 800x600
sample_rgb = bgr2rgb(sample)

def _load_cifar_sample(label="airplane"):
    """从本地 CIFAR-10 测试集取一张指定类别的样本，返回 BGR 图（放大到 128）。"""
    import torchvision
    import torchvision.transforms as T
    testset = torchvision.datasets.CIFAR10(
        root=os.path.join(".datasets", "cifar10"), train=False, download=False,
        transform=T.ToTensor())
    classes = testset.classes
    idx = classes.index(label)
    for img, y in testset:
        if y == idx:
            arr = (img.permute(1, 2, 0).numpy() * 255).astype(np.uint8)
            arr = cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)
            arr = cv2.resize(arr, (128, 128), interpolation=cv2.INTER_NEAREST)
            return arr, label
    raise RuntimeError("未找到样本")

# ==================== 图5-4：图像分类 + 语义分割 ====================

def fig5_4():
    print("生成 图5-4 图像分类 + 语义分割 ...", flush=True)
    cls = image_classification(sample, {"top_k": 3})
    seg = semantic_segmentation(sample, {"opacity": 0.55})
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    axes[0].imshow(bgr2rgb(cls))
    axes[0].set_title("(a) 图像分类 (MobileNetV2, Top-3)", fontsize=11)
    axes[0].axis("off")
    axes[1].imshow(bgr2rgb(seg))
    axes[1].set_title("(b) 语义分割 (DeepLabV3, COCO)", fontsize=11)
    axes[1].axis("off")
    fig.tight_layout()
    _save(fig, "fig5_4_深度学习图像理解.png")

# ==================== 图5-5：超分辨率 + CIFAR-10 分类 ====================

def fig5_5():
    print("生成 图5-5 超分辨率 + CIFAR-10 分类 ...", flush=True)
    # 超分辨率：构造 LR / 双三次 / SRCNN 三幅对比
    gray = cv2.cvtColor(sample, cv2.COLOR_BGR2GRAY)
    h, w = gray.shape
    lr = cv2.resize(gray, (w // 3, h // 3), interpolation=cv2.INTER_AREA)
    lr_up = cv2.resize(lr, (w, h), interpolation=cv2.INTER_CUBIC)
    sr = super_resolution(sample, {"scale": 3})
    sr_gray = cv2.cvtColor(sr, cv2.COLOR_BGR2GRAY) if sr.ndim == 3 else sr

    # CIFAR-10 分类
    cifar_img, cifar_label = _load_cifar_sample("airplane")
    cifar_cls = cifar10_classification(cifar_img, {"top_k": 3})

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    # 左：超分辨率三连
    ax = axes[0]
    combo = np.hstack([lr_up, sr_gray])
    ax.imshow(combo, cmap="gray")
    ax.set_title("(a) 超分辨率重建 (SRCNN)：双三次放大 vs SRCNN", fontsize=11)
    ax.axis("off")
    # 右：CIFAR-10 分类
    axes[1].imshow(bgr2rgb(cifar_cls))
    axes[1].set_title(f"(b) CIFAR-10 分类 (CIFAR10Net)", fontsize=11)
    axes[1].axis("off")
    fig.tight_layout()
    _save(fig, "fig5_5_超分与分类.png")

# ==================== 图5-6：训练曲线 ====================

def fig5_6():
    print("生成 图5-6 训练曲线 ...", flush=True)
    import modules.dl_models as dm
    import modules.training as tr

    # 临时目录，避免覆盖真实训练权重
    tmp = os.path.join(".datasets", "_fig_tmp_models")
    os.makedirs(tmp, exist_ok=True)
    real_models = dm.MODELS_DIR
    dm.MODELS_DIR = tmp
    tr.MODELS_DIR = tmp

    print("  短期训练 CIFAR-10 (subset=512, epochs=4) ...", flush=True)
    _, hist_cifar = tr.train_cifar10(epochs=4, batch_size=64, lr=1e-3, subset=512)
    print("  短期训练 SRCNN (subset=512, epochs=4) ...", flush=True)
    _, hist_srcnn = tr.train_srcnn(epochs=4, batch_size=64, lr=1e-3, subset=512)

    # 还原
    dm.MODELS_DIR = real_models
    tr.MODELS_DIR = real_models
    import shutil
    shutil.rmtree(tmp, ignore_errors=True)

    fig, axes = plt.subplots(1, 3, figsize=(15, 4.2))
    axes[0].plot(hist_cifar["train_loss"], marker="o", label="训练损失")
    axes[0].plot(hist_cifar["val_loss"], marker="s", label="验证损失")
    axes[0].set_xlabel("训练轮次")
    axes[0].set_ylabel("损失")
    axes[0].set_title("(a) CIFAR-10 损失曲线")
    axes[0].legend()
    axes[0].grid(alpha=0.3)

    axes[1].plot(hist_cifar["train_acc"], marker="o", label="训练准确率")
    axes[1].plot(hist_cifar["val_acc"], marker="s", label="验证准确率")
    axes[1].set_xlabel("训练轮次")
    axes[1].set_ylabel("准确率")
    axes[1].set_title("(b) CIFAR-10 准确率曲线")
    axes[1].legend()
    axes[1].grid(alpha=0.3)

    axes[2].plot(hist_srcnn["train_loss"], marker="o", color="crimson")
    axes[2].set_xlabel("训练轮次")
    axes[2].set_ylabel("损失")
    axes[2].set_title("(c) SRCNN 训练损失曲线")
    axes[2].grid(alpha=0.3)

    fig.suptitle("深度学习模型训练过程", fontsize=13, fontweight="bold")
    fig.tight_layout()
    _save(fig, "fig5_6_训练曲线.png")

if __name__ == "__main__":
    fig5_4()
    fig5_5()
    fig5_6()
    print("\n全部完成。")
