"""
深度学习模型定义与标签常量

集中维护 CNN 模型结构（供推理与训练共用）以及标签/调色板等常量，
避免在 deep_learning.py（推理）与 training.py（训练）之间产生循环依赖。

注意：本模块在顶部导入 torch，因此仅当 torch 已安装时才能被导入。
modules/registry.py 在导入 deep_learning 时已用 try/except 包裹，
torch 缺失时不会破坏经典算法平台的启动。
"""

import os
import numpy as np
import torch
import torch.nn as nn

# ==================== 路径常量 ====================
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS_DIR = os.path.join(ROOT, "models")          # 训练产出的权重存放目录
DATA_DIR = os.path.join(ROOT, ".datasets")         # 数据集缓存目录

# ==================== 模型定义 ====================

class SRCNN(nn.Module):
    """
    图像超分辨率卷积网络（SRCNN，Dong et al. 2014）。

    经典三层结构：Conv(9×9, 1→64) → Conv(1×1, 64→32) → Conv(5×5, 32→1)。
    输入为双三次（此处用双线性近似）上采样后的单通道亮度 Y，
    输出为重建的高分辨率亮度。参数量约 5.7 万，CPU 即可训练。
    """

    def __init__(self):
        super().__init__()
        self.conv1 = nn.Conv2d(1, 64, kernel_size=9, padding=4)
        self.conv2 = nn.Conv2d(64, 32, kernel_size=1, padding=0)
        self.conv3 = nn.Conv2d(32, 1, kernel_size=5, padding=2)
        self.relu = nn.ReLU(inplace=True)

    def forward(self, x):
        x = self.relu(self.conv1(x))
        x = self.relu(self.conv2(x))
        x = self.conv3(x)
        return x


class CIFAR10Net(nn.Module):
    """
    面向 CIFAR-10（32×32×3，10 类）的小型卷积网络。

    三层卷积 + 池化堆叠提取特征，后接两层全连接分类头。
    结构简单、参数量小，适合作为"自定义训练模型"的教学示例。
    """

    def __init__(self, num_classes: int = 10):
        super().__init__()
        self.features = nn.Sequential(
            nn.Conv2d(3, 32, 3, padding=1), nn.ReLU(inplace=True), nn.MaxPool2d(2),
            nn.Conv2d(32, 64, 3, padding=1), nn.ReLU(inplace=True), nn.MaxPool2d(2),
            nn.Conv2d(64, 128, 3, padding=1), nn.ReLU(inplace=True), nn.MaxPool2d(2),
        )
        self.classifier = nn.Sequential(
            nn.Flatten(),
            nn.Linear(128 * 4 * 4, 256), nn.ReLU(inplace=True), nn.Dropout(0.5),
            nn.Linear(256, num_classes),
        )

    def forward(self, x):
        return self.classifier(self.features(x))

# ==================== 标签与调色板 ====================

CIFAR10_CLASSES = [
    "airplane", "automobile", "bird", "cat", "deer",
    "dog", "frog", "horse", "ship", "truck",
]

# DeepLabV3（COCO/VOC 标签）的 21 类（含 background）
VOC_CLASSES = [
    "background", "aeroplane", "bicycle", "bird", "boat", "bottle", "bus",
    "car", "cat", "chair", "cow", "dining table", "dog", "horse",
    "motorbike", "person", "potted plant", "sheep", "sofa", "train",
    "tv/monitor",
]

def _build_palette(n: int) -> np.ndarray:
    """生成确定性的语义分割调色板（BGR），background 固定为黑色。"""
    rng = np.random.RandomState(42)
    palette = rng.randint(40, 230, size=(n, 3)).astype(np.uint8)
    palette[0] = [0, 0, 0]
    return palette

VOC_PALETTE = _build_palette(len(VOC_CLASSES))

# ImageNet 归一化参数
IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD = [0.229, 0.224, 0.225]

# CIFAR-10 归一化参数（训练集统计值）
CIFAR10_MEAN = [0.4914, 0.4822, 0.4465]
CIFAR10_STD = [0.2023, 0.1994, 0.2010]
