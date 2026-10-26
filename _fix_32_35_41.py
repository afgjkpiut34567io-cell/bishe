# -*- coding: utf-8 -*-
"""[审查项#11] 3.2 补深度学习功能需求；3.5 补深度学习用例；4.1 代码组织改为“六个算法模块加 training 模块”"""
import sys, shutil
sys.stdout.reconfigure(encoding="utf-8")
from docx import Document

PATH = r'd:\1\bishe\毕设\7230267148_杨康康_基于opencv和streamlit的图像处理算法交互式演示系统 - 降重改写版.docx'
BAK = r'd:\1\bishe\毕设\_bak_降重改写版_20261014_before_dlreq.docx'
shutil.copy2(PATH, BAK)
print("备份:", BAK)

doc = Document(PATH)
ps = doc.paragraphs

# ---------- 1) 3.2 节第(2)条：补深度学习处理功能描述 ----------
p32 = None
for p in ps:
    if p.text.startswith("（2）算法处理功能"):
        p32 = p; break
assert p32 is not None, "未找到 3.2 节第(2)条"
assert p32.runs[9].text == "。"
p32.runs[9].text = (
    "。这四类深度学习算法要依托PyTorch才能跑起来，功能上各自给出对应的推理结果，"
    "图像分类与CIFAR-10分类会给出概率靠前的若干预测类别，语义分割把不同类别用彩色掩码叠到原图上，"
    "超分辨率则按设定的倍数把图像放大重建。"
)

# ---------- 2) 3.5 节用例分析：补第四类深度学习用例 ----------
p35 = None
for p in ps:
    if p.text.startswith("系统与用户之间的交互，可以借助几类典型用例"):
        p35 = p; break
assert p35 is not None, "未找到 3.5 节用例分析段"
dl_case = (
    "第四类是深度学习算法体验：用户在深度学习这一类里挑一个算法，"
    "比如图像分类、语义分割、超分辨率或者CIFAR-10分类，把图像传上去跑一次推理，"
    "分类和CIFAR-10分类会给出若干个预测类别，语义分割把不同类别用彩色掩码标出来，"
    "超分辨率则按倍数把图像放大，用户可以由此感受深度学习算法和传统算法在做法上的不同；"
    "这一类要依托PyTorch运行，模型第一次加载时会稍等一会儿。"
)
assert "系统总体用例图如图" in p35.runs[0].text
p35.runs[0].text = p35.runs[0].text.replace("系统总体用例图如图", dl_case + "系统总体用例图如图")

# ---------- 3) 4.1 代码组织：明确“六个算法模块加 training 模块” ----------
p41 = None
for p in ps:
    if p.text.startswith("代码组织上，系统按分层思想"):
        p41 = p; break
assert p41 is not None, "未找到 4.1 代码组织段"
新41 = {
    0: "代码组织上，系统按分层思想划分出若干目录。算法层在",
    1: "",
    2: "",
    3: "",
    4: "modules",
    5: ("目录下放了六个算法模块，分别对应滤波、增强、边缘检测、形态学、变换和阈值分割，"
        "再加上深度学习模块和可视化模块；深度学习模型的训练流水线则放在"),
    6: "",
    7: "training",
    8: "模块；",
}
for idx, text in 新41.items():
    p41.runs[idx].text = text

doc.save(PATH)
print("已保存。\n")
for n, p in (("3.2(2)", p32), ("3.5 用例", p35), ("4.1 代码组织", p41)):
    print("===", n, "===")
    print(p.text)
    print("runs:", [r.text for r in p.runs])
    print()
