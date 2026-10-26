"""
深度学习功能端到端验证脚本

覆盖三阶段：
  - 阶段一：预训练模型推理（图像分类 / 语义分割）
  - 阶段二：特征图 + Grad-CAM 可视化
  - 阶段三：训练流水线（CIFAR-10 分类 / SRCNN 超分）+ 自定义模型推理

用法：
    python verify_dl.py [--skip-train] [--subset N] [--epochs N]

注意：首次运行会联网下载预训练权重（约 25MB）与 CIFAR-10 数据集（约 170MB）。
"""

import os
import sys
import argparse
import time

import numpy as np
import cv2

sys.stdout.reconfigure(encoding="utf-8")

PASS = []
FAIL = []


def check(name, fn):
    t0 = time.time()
    try:
        fn()
        dt = time.time() - t0
        PASS.append(name)
        print(f"  [PASS] {name}  ({dt:.1f}s)")
    except Exception as e:
        FAIL.append(name)
        print(f"  [FAIL] {name}  -> {type(e).__name__}: {e}")


def make_test_image(h=224, w=224):
    """构造一张含简单几何元素的测试图（BGR）。"""
    img = np.full((h, w, 3), 220, dtype=np.uint8)
    cv2.rectangle(img, (40, 40), (w - 40, h - 40), (0, 0, 0), 2)
    cv2.circle(img, (w // 2, h // 2), 50, (40, 40, 200), -1)
    cv2.rectangle(img, (80, 80), (150, 150), (0, 180, 0), -1)
    return img


def test_imports():
    import modules.dl_models
    import modules.dl_visualization
    import modules.deep_learning
    import modules.training
    from modules import registry

    dl_registered = [k for k in registry.ALGORITHM_FUNCTIONS
                      if k in ("image_classification", "semantic_segmentation",
                               "super_resolution", "cifar10_classification")]
    assert registry._DL_AVAILABLE is True, "torch 已安装但 _DL_AVAILABLE 不为 True"
    assert len(dl_registered) == 4, f"DL 算法注册数={len(dl_registered)}，应为 4"
    print(f"        注册表共 {len(registry.ALGORITHM_FUNCTIONS)} 个算法（30 经典 + 4 DL）")


def test_model_architectures():
    import torch
    from modules.dl_models import SRCNN, CIFAR10Net

    srcnn = SRCNN()
    out = srcnn(torch.randn(1, 1, 32, 32))
    assert out.shape == (1, 1, 32, 32), f"SRCNN 输出 {out.shape}"

    net = CIFAR10Net(num_classes=10)
    logits = net(torch.randn(2, 3, 32, 32))
    assert logits.shape == (2, 10), f"CIFAR10Net 输出 {logits.shape}"


def test_image_classification():
    from modules.deep_learning import image_classification
    img = make_test_image()
    result = image_classification(img, {"top_k": 3})
    assert result.dtype == np.uint8 and result.shape[0] >= img.shape[0]
    print(f"        输出尺寸 {result.shape[1]}x{result.shape[0]}")


def test_semantic_segmentation():
    from modules.deep_learning import semantic_segmentation
    img = make_test_image(256, 256)
    result = semantic_segmentation(img, {"opacity": 0.5})
    assert result.shape == img.shape and result.dtype == np.uint8
    print(f"        输出尺寸 {result.shape[1]}x{result.shape[0]}")


def test_feature_maps_and_gradcam():
    import torch
    from modules.dl_models import IMAGENET_MEAN, IMAGENET_STD
    from modules.dl_visualization import plot_feature_maps, plot_grad_cam

    from torchvision import models
    model = models.mobilenet_v2(weights=None).eval()

    img = make_test_image(224, 224)
    rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB).astype(np.float32) / 255.0
    rgb = (rgb - np.array(IMAGENET_MEAN, dtype=np.float32)) / np.array(IMAGENET_STD, dtype=np.float32)
    x = torch.from_numpy(rgb).permute(2, 0, 1).unsqueeze(0)

    fm = plot_feature_maps(model, x)
    assert fm.dtype == np.uint8 and fm.ndim == 3

    cam = plot_grad_cam(img, model, x)
    assert cam.dtype == np.uint8 and cam.ndim == 3
    print(f"        特征图 {fm.shape[1]}x{fm.shape[0]}, Grad-CAM {cam.shape[1]}x{cam.shape[0]}")


def test_train_cifar10(subset, epochs):
    from modules.training import train_cifar10, plot_training_curves
    model, hist = train_cifar10(epochs=epochs, batch_size=64, lr=1e-3, subset=subset)
    assert os.path.exists(os.path.join("models", "cifar10_cnn.pth"))
    assert len(hist["train_loss"]) == epochs and len(hist["val_acc"]) == epochs
    curve = plot_training_curves(hist, "CIFAR-10 训练曲线")
    assert curve.dtype == np.uint8


def test_train_srcnn(subset, epochs):
    from modules.training import train_srcnn
    model, hist = train_srcnn(epochs=epochs, batch_size=64, lr=1e-3, subset=subset)
    assert os.path.exists(os.path.join("models", "srcnn.pth"))
    assert len(hist["train_loss"]) == epochs


def test_custom_model_inference():
    from modules.deep_learning import super_resolution, cifar10_classification
    img = make_test_image(64, 64)

    sr = super_resolution(img, {"scale": 2})
    assert sr.shape == img.shape and sr.dtype == np.uint8

    cls = cifar10_classification(img, {"top_k": 3})
    assert cls.dtype == np.uint8 and cls.shape[0] >= img.shape[0]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--skip-train", action="store_true")
    ap.add_argument("--subset", type=int, default=256)
    ap.add_argument("--epochs", type=int, default=1)
    args = ap.parse_args()

    print("=" * 60)
    print("深度学习功能端到端验证")
    print("=" * 60)

    print("\n[1] 模块导入与注册")
    check("模块导入 + DL 注册", test_imports)

    print("\n[2] 模型结构")
    check("SRCNN / CIFAR10Net 前向传播", test_model_architectures)

    print("\n[3] 阶段一：预训练模型推理")
    check("图像分类 (MobileNetV2)", test_image_classification)
    check("语义分割 (DeepLabV3)", test_semantic_segmentation)

    print("\n[4] 阶段二：特征图 + Grad-CAM")
    check("特征图 + Grad-CAM 可视化", test_feature_maps_and_gradcam)

    if not args.skip_train:
        print("\n[5] 阶段三：训练流水线")
        check(f"CIFAR-10 训练 (subset={args.subset}, epochs={args.epochs})",
              lambda: test_train_cifar10(args.subset, args.epochs))
        check(f"SRCNN 训练 (subset={args.subset}, epochs={args.epochs})",
              lambda: test_train_srcnn(args.subset, args.epochs))

        print("\n[6] 阶段三：自定义模型推理")
        check("超分辨率 + CIFAR-10 分类推理", test_custom_model_inference)

    print("\n" + "=" * 60)
    print(f"结果：通过 {len(PASS)} 项，失败 {len(FAIL)} 项")
    if FAIL:
        print("失败项：")
        for f in FAIL:
            print(f"  - {f}")
        sys.exit(1)
    else:
        print("全部通过 ✅")


if __name__ == "__main__":
    main()
