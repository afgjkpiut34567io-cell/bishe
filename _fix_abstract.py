# -*- coding: utf-8 -*-
"""[审查项#13] 英文摘要：integrates three common algorithms -> seven categories, 34 algorithms，并补译四类深度学习算法"""
import sys, shutil
sys.stdout.reconfigure(encoding="utf-8")
from docx import Document

PATH = r'd:\1\bishe\毕设\7230267148_杨康康_基于opencv和streamlit的图像处理算法交互式演示系统 - 降重改写版.docx'
BAK = r'd:\1\bishe\毕设\_bak_降重改写版_20261014_before_abstract.docx'
shutil.copy2(PATH, BAK)
print("备份:", BAK)

doc = Document(PATH)
p = None
for q in doc.paragraphs:
    if q.text.startswith("To address this, this paper designs and implements"):
        p = q; break
assert p is not None, "未找到英文摘要段"

OLD = ("The platform integrates three common algorithms: filtering, image enhancement, "
       "edge detection, morphology operations, threshold segmentation, and image transformation, "
       "supporting real-time parameter adjustment")
NEW = ("The platform integrates seven categories and 34 algorithms in total, "
       "covering filtering, image enhancement, edge detection, morphology operations, "
       "threshold segmentation, and image transformation as the six classic categories, "
       "together with four deep learning algorithms, namely image classification, "
       "semantic segmentation, super-resolution, and CIFAR-10 classification. "
       "It supports real-time parameter adjustment")

hit = False
for r in p.runs:
    if OLD in r.text:
        r.text = r.text.replace(OLD, NEW); hit = True
assert hit, "未匹配到待替换英文片段"

doc.save(PATH)
print("已保存。\n修改后英文摘要：")
print(p.text)
