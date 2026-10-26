# -*- coding: utf-8 -*-
"""定位 深度学习算法模块(5.10) 与 开发环境 小节, 打印上下文"""
import sys
sys.stdout.reconfigure(encoding="utf-8")
from docx import Document
PATH = r'd:\1\bishe\毕设\7230267148_杨康康_基于opencv和streamlit的图像处理算法交互式演示系统 - 降重改写版.docx'
doc = Document(PATH)
ps = doc.paragraphs
def find(key):
    hits = [i for i, p in enumerate(ps) if key in p.text]
    return hits
for key in ["深度学习算法模块", "开发环境", "深度学习与PyTorch", "PyTorch"]:
    print(f"\n### 含'{key}'的段落: {find(key)}")
# 打印 深度学习算法模块 小节全文
i0 = find("深度学习算法模块")[0]
print(f"\n--- 深度学习算法模块 小节 [{i0}..] ---")
j = i0
while j < len(ps) and not (ps[j].style.name == "论文二级标题" and j != i0):
    print(f"[{j}] ({ps[j].style.name}) {ps[j].text}")
    j += 1
print(f"(下一个二级标题在 [{j}]: {ps[j].text})")
