# -*- coding: utf-8 -*-
"""定位"定位误差/检出率"类量化承诺所在段落"""
from docx import Document

PATH = r'd:\1\bishe\毕设\7230267148_杨康康_基于opencv和streamlit的图像处理算法交互式演示系统 - 降重改写版.docx'
doc = Document(PATH)

keys = ["定位误差", "检出率", "真值", "检出", "逐像素", "合成", "亚像素", "误差"]
for i, p in enumerate(doc.paragraphs):
    t = p.text
    hit = [k for k in keys if k in t]
    if hit:
        print(f"[{i}] 命中{hit}")
        print(t)
        print("-" * 70)
