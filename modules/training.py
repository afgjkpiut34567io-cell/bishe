"""
深度学习训练模块 - Phase 3 迁移学习 / 从零训练流水线

训练两个轻量模型，用于平台"自定义训练模型"的教学演示：
  1. CIFAR-10 图像分类网络 (CIFAR10Net) —— 从零训练一个 10 类分类器；
  2. 图像超分辨率网络 (SRCNN) —— 学习低分辨率到高分辨率的映射。

用法（命令行，在项目根目录执行）：
    python -m modules.training                         # 训练两个模型
    python -m modules.training --task cifar10 --epochs 5
    python -m modules.training --task srcnn  --epochs 10
    python -m modules.training --subset 1000 --epochs 2   # 小样本快速试跑

说明：
  - 训练数据使用 torchvision 的 CIFAR-10（首次自动下载约 170MB 到 .datasets/）；
  - SRCNN 的训练样本由 CIFAR-10 图像下采样构造 LR/HR 对，无需额外数据；
  - 训练产物保存到 models/（cifar10_cnn.pth / srcnn.pth），供推理模块加载。
"""

import os
import argparse

import numpy as np
import cv2
import torch
import torch.nn as nn
import torch.nn.functional as F
import torchvision
import torchvision.transforms as T

from modules.dl_models import SRCNN, CIFAR10Net, CIFAR10_CLASSES, MODELS_DIR, DATA_DIR

CIFAR10_MEAN = [0.4914, 0.4822, 0.4465]
CIFAR10_STD = [0.2023, 0.1994, 0.2010]

def _device():
    return "cuda" if torch.cuda.is_available() else "cpu"

# ==================== CIFAR-10 分类训练 ====================

def _load_cifar10(subset=None):
    """加载 CIFAR-10 数据集；subset 仅取前 N 个样本用于快速试跑。"""
    os.makedirs(DATA_DIR, exist_ok=True)
    root = os.path.join(DATA_DIR, "cifar10")

    train_tf = T.Compose([
        T.RandomCrop(32, padding=4),
        T.RandomHorizontalFlip(),
        T.ToTensor(),
        T.Normalize(CIFAR10_MEAN, CIFAR10_STD),
    ])
    test_tf = T.Compose([T.ToTensor(), T.Normalize(CIFAR10_MEAN, CIFAR10_STD)])

    trainset = torchvision.datasets.CIFAR10(root=root, train=True, download=True, transform=train_tf)
    testset = torchvision.datasets.CIFAR10(root=root, train=False, download=True, transform=test_tf)

    if subset:
        trainset = torch.utils.data.Subset(trainset, range(min(subset, len(trainset))))
        testset = torch.utils.data.Subset(testset, range(min(max(subset // 5, 1), len(testset))))
    return trainset, testset

def _evaluate(model, loader, criterion, device):
    model.eval()
    loss_sum, correct, total = 0.0, 0, 0
    with torch.no_grad():
        for x, y in loader:
            x, y = x.to(device), y.to(device)
            out = model(x)
            loss_sum += criterion(out, y).item() * x.size(0)
            correct += (out.argmax(1) == y).sum().item()
            total += x.size(0)
    return loss_sum / total, correct / total

def train_cifar10(epochs=5, batch_size=128, lr=1e-3, subset=None):
    """从零训练 CIFAR10Net，返回 (模型, 训练历史)。"""
    device = _device()
    trainset, testset = _load_cifar10(subset)
    trainloader = torch.utils.data.DataLoader(trainset, batch_size=batch_size, shuffle=True, num_workers=0)
    testloader = torch.utils.data.DataLoader(testset, batch_size=batch_size, shuffle=False, num_workers=0)

    model = CIFAR10Net(num_classes=10).to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)

    history = {"train_loss": [], "train_acc": [], "val_loss": [], "val_acc": []}
    print(f"[CIFAR-10] 设备={device}, epochs={epochs}, 训练样本={len(trainset)}")

    for epoch in range(epochs):
        model.train()
        running_loss, correct, total = 0.0, 0, 0
        for x, y in trainloader:
            x, y = x.to(device), y.to(device)
            optimizer.zero_grad()
            out = model(x)
            loss = criterion(out, y)
            loss.backward()
            optimizer.step()
            running_loss += loss.item() * x.size(0)
            correct += (out.argmax(1) == y).sum().item()
            total += x.size(0)

        train_loss = running_loss / total
        train_acc = correct / total
        val_loss, val_acc = _evaluate(model, testloader, criterion, device)
        history["train_loss"].append(train_loss)
        history["train_acc"].append(train_acc)
        history["val_loss"].append(val_loss)
        history["val_acc"].append(val_acc)
        print(f"  Epoch {epoch + 1}/{epochs}  "
              f"train_loss={train_loss:.4f} train_acc={train_acc:.3f}  "
              f"val_loss={val_loss:.4f} val_acc={val_acc:.3f}")

    os.makedirs(MODELS_DIR, exist_ok=True)
    ckpt = os.path.join(MODELS_DIR, "cifar10_cnn.pth")
    torch.save(model.state_dict(), ckpt)
    print(f"[OK] 已保存模型: {ckpt}")
    return model, history

# ==================== SRCNN 超分辨率训练 ====================

def train_srcnn(epochs=10, batch_size=64, lr=1e-3, subset=None, scale=2):
    """训练 SRCNN，训练样本由 CIFAR-10 图像下采样构造 LR/HR 对。"""
    device = _device()
    os.makedirs(DATA_DIR, exist_ok=True)
    root = os.path.join(DATA_DIR, "cifar10")

    transform = T.Compose([T.ToTensor()])
    trainset = torchvision.datasets.CIFAR10(root=root, train=True, download=True, transform=transform)
    if subset:
        trainset = torch.utils.data.Subset(trainset, range(min(subset, len(trainset))))
    trainloader = torch.utils.data.DataLoader(trainset, batch_size=batch_size, shuffle=True, num_workers=0)

    model = SRCNN().to(device)
    criterion = nn.MSELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)

    history = {"train_loss": []}
    print(f"[SRCNN] 设备={device}, epochs={epochs}, 训练样本={len(trainset)}", flush=True)

    for epoch in range(epochs):
        model.train()
        running_loss, n = 0.0, 0
        for x, _ in trainloader:
            x = x.to(device)                                        # (B,3,32,32)
            hr = 0.299 * x[:, 0:1] + 0.587 * x[:, 1:2] + 0.114 * x[:, 2:3]  # 灰度 HR
            # 下采样用 area（抗混叠），上采样用 bicubic——与推理阶段 deep_learning.super_resolution 保持一致
            lr = F.interpolate(hr, scale_factor=1 / scale, mode="area")
            lr_up = F.interpolate(lr, scale_factor=scale, mode="bicubic", align_corners=False)
            optimizer.zero_grad()
            out = model(lr_up)
            loss = criterion(out, hr)
            loss.backward()
            optimizer.step()
            running_loss += loss.item() * x.size(0)
            n += x.size(0)
        avg = running_loss / n
        history["train_loss"].append(avg)
        print(f"  Epoch {epoch + 1}/{epochs}  train_loss={avg:.5f}", flush=True)

    os.makedirs(MODELS_DIR, exist_ok=True)
    ckpt = os.path.join(MODELS_DIR, "srcnn.pth")
    torch.save(model.state_dict(), ckpt)
    print(f"[OK] 已保存模型: {ckpt}")
    return model, history

# ==================== 训练曲线可视化 ====================

def plot_training_curves(history: dict, title: str = "训练过程") -> np.ndarray:
    """绘制训练/验证损失与准确率曲线，返回 BGR 图像。"""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from modules.visualization import _figure_to_image, _L, COLORS

    has_acc = "train_acc" in history and "val_acc" in history
    fig, axes = plt.subplots(1, 2, figsize=(11, 4)) if has_acc else plt.subplots(1, 1, figsize=(6, 4))

    if has_acc:
        axes[0].plot(history["train_loss"], label=_L("训练损失", "Train Loss"), color=COLORS["primary"])
        axes[0].plot(history["val_loss"], label=_L("验证损失", "Val Loss"), color=COLORS["warning"])
        axes[0].set_xlabel(_L("轮次 (Epoch)", "Epoch"))
        axes[0].set_title(_L("损失曲线", "Loss Curve"))
        axes[0].legend()
        axes[1].plot(history["train_acc"], label=_L("训练准确率", "Train Acc"), color=COLORS["primary"])
        axes[1].plot(history["val_acc"], label=_L("验证准确率", "Val Acc"), color=COLORS["accent"])
        axes[1].set_xlabel(_L("轮次 (Epoch)", "Epoch"))
        axes[1].set_title(_L("准确率曲线", "Accuracy Curve"))
        axes[1].legend()
    else:
        axes.plot(history["train_loss"], label=_L("训练损失", "Train Loss"), color=COLORS["primary"])
        axes.set_xlabel(_L("轮次 (Epoch)", "Epoch"))
        axes.set_title(_L("损失曲线", "Loss Curve"))
        axes.legend()

    fig.suptitle(title, fontsize=14, fontweight="bold")
    fig.tight_layout()
    return _figure_to_image(fig)

# ==================== 命令行入口 ====================

def main():
    parser = argparse.ArgumentParser(description="深度学习模型训练（CIFAR-10 分类 / SRCNN 超分）")
    parser.add_argument("--task", choices=["all", "cifar10", "srcnn"], default="all")
    parser.add_argument("--epochs", type=int, default=5)
    parser.add_argument("--batch-size", type=int, default=128)
    parser.add_argument("--lr", type=float, default=1e-3)
    parser.add_argument("--subset", type=int, default=None, help="仅用前 N 个样本（快速试跑）")
    parser.add_argument("--save-curve", type=str, default=None, help="训练曲线 PNG 保存路径")
    args = parser.parse_args()

    if args.task in ("all", "cifar10"):
        print("=" * 40)
        print("训练 CIFAR-10 分类网络")
        _, hist = train_cifar10(args.epochs, args.batch_size, args.lr, args.subset)
        if args.save_curve:
            os.makedirs(os.path.dirname(os.path.abspath(args.save_curve)), exist_ok=True)
            cv2.imwrite(args.save_curve, plot_training_curves(hist, "CIFAR-10 分类训练曲线"))
            print(f"[OK] 训练曲线已保存: {args.save_curve}")

    if args.task in ("all", "srcnn"):
        print("=" * 40)
        print("训练 SRCNN 超分辨率网络")
        _, hist = train_srcnn(args.epochs, args.batch_size, args.lr, args.subset)
        if args.save_curve:
            curve_path = args.save_curve
            # --save-curve 为单一路径时，CIFAR-10 已占用则按任务名区分
            if args.task == "all":
                base, ext = os.path.splitext(curve_path)
                curve_path = f"{base}_srcnn{ext or '.png'}"
            os.makedirs(os.path.dirname(os.path.abspath(curve_path)), exist_ok=True)
            cv2.imwrite(curve_path, plot_training_curves(hist, "SRCNN 超分辨率训练曲线"))
            print(f"[OK] 训练曲线已保存: {curve_path}")

if __name__ == "__main__":
    main()
