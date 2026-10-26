# -*- coding: utf-8 -*-
"""[审查项#17] 行330（2章 OpenCV 段）覆盖范围限定为六大类30种经典算法，深度学习四类与 NumPy 自建核表另行分述"""
import sys, shutil
sys.stdout.reconfigure(encoding="utf-8")
from docx import Document

PATH = r'd:\1\bishe\毕设\7230267148_杨康康_基于opencv和streamlit的图像处理算法交互式演示系统 - 降重改写版.docx'
BAK = r'd:\1\bishe\毕设\_bak_降重改写版_20261014_before_opencvclaim.docx'
shutil.copy2(PATH, BAK)
print("备份:", BAK)

doc = Document(PATH)
p = None
for q in doc.paragraphs:
    if q.text.startswith("算法覆盖面全这一点是最直接的"):
        p = q; break
assert p is not None, "未找到 OpenCV 覆盖面段"
print("改前:", p.text[:60], "...")

assert p.runs[1].text == "34"
新版 = {
    0: "算法覆盖面全这一点是最直接的，本系统要用到的六大类",
    1: "30",
    2: ("种经典算法，在它里面都有成熟而且经过优化的实现；深度学习那四类并不由OpenCV提供，"
        "而是由PyTorch和torchvision来承担；剩下的那些OpenCV没有直接提供的地方，"
        "则用NumPy自建的核与查找表来补齐。它的"),
}
for idx, text in 新版.items():
    p.runs[idx].text = text

doc.save(PATH)
print("\n改后全文:")
print(p.text)
