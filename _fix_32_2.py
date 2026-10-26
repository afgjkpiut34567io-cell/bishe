# -*- coding: utf-8 -*-
"""审查项：3.2 节第(2)条补列深度学习算法处理功能，计数表述改为“六大类30种经典算法加四类深度学习共34种”"""
import sys, shutil
sys.stdout.reconfigure(encoding="utf-8")
from docx import Document

PATH = r'd:\1\bishe\毕设\7230267148_杨康康_基于opencv和streamlit的图像处理算法交互式演示系统 - 降重改写版.docx'
BAK = r'd:\1\bishe\毕设\_bak_降重改写版_20261014_before_32_2.docx'
shutil.copy2(PATH, BAK)
print("备份:", BAK)

doc = Document(PATH)
target = None
for p in doc.paragraphs:
    if p.text.startswith("（2）算法处理功能"):
        target = p; break
assert target is not None, "未找到 3.2 节第(2)条"

print("修改前 runs：")
for i, r in enumerate(target.runs):
    print(i, repr(r.text))

# 保留 run5='CIFAR-10'、run7='34'、run8='种'、run9='。' 的独立 run；只改 run2/run3/run4/run6
新版 = {
    2: "）算法处理功能。在算法覆盖面上，本系统是围绕滤波、图像增强、边缘检测、形态学操作、阈值分割和图像变换这六大类经典算法展开的",
    3: "，",
    4: "此外还补充了图像分类、语义分割、超分辨率和",
    6: "分类这四类深度学习算法，也就是六大类30种经典算法加四类深度学习共",
}
for idx, text in 新版.items():
    target.runs[idx].text = text

doc.save(PATH)
print("已保存。\n修改后段落全文：")
print(target.text)
print("\n修改后 runs：")
for i, r in enumerate(target.runs):
    print(i, repr(r.text))
