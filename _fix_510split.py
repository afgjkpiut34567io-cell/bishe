# -*- coding: utf-8 -*-
"""审查项#9：把 5.10 概述段四类深度学习算法分述为“复用 torchvision 预训练结构”与“自研训练”两组"""
import sys, shutil
sys.stdout.reconfigure(encoding="utf-8")
from docx import Document

PATH = r'd:\1\bishe\毕设\7230267148_杨康康_基于opencv和streamlit的图像处理算法交互式演示系统 - 降重改写版.docx'
BAK = r'd:\1\bishe\毕设\_bak_降重改写版_20261014_before_510split.docx'
shutil.copy2(PATH, BAK)
print("备份:", BAK)

doc = Document(PATH)
target = None
for p in doc.paragraphs:
    if p.text.startswith("系统还基于PyTorch补充了四类"):
        target = p; break
assert target is not None, "未找到 5.10 概述段"

# run2~run7 是描述四类算法的部分，整体替换为分述表述
新版 = {
    2: "补充了四类深度学习图像处理算法，按实现来源可以分成两组来看：一组复用",
    3: "",
    4: "torchvision",   # 保留在独立的英文 run 里
    5: ("提供的预训练网络结构，图像分类用的是MobileNetV2、语义分割用的是DeepLabV3，"
        "这两类只做预处理、前向传播和结果后处理，网络结构与权重都取自官方，系统并没有自己去训练；"
        "另一组是自研训练的网络，图像超分辨率用的是SRCNN、"),
    6: "CIFAR-10",
    7: ("分类用的是CIFAR10Net，结构由系统自己设计，权重也是靠项目里的训练脚本"
        "在CIFAR-10数据上训练出来的；"),
}
for idx, text in 新版.items():
    target.runs[idx].text = text

doc.save(PATH)
print("已保存。")
print("\n修改后段落全文：")
print(target.text)
