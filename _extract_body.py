# -*- coding: utf-8 -*-
"""从降重版提取正文段落结构,输出JSON供分批改写"""
from docx import Document
import json, re, sys

SRC = r'd:\1\bishe\毕设\2   7230267148_杨康康_基于opencv和streamlit的图像处理算法交互式演示系统 - 降重版.docx'

doc = Document(SRC)
paras = doc.paragraphs
print(f"总段落数: {len(paras)}")

# 打印每个非空段落的: 索引 | 样式 | 前60字
for i, p in enumerate(paras):
    t = p.text.strip()
    if not t:
        continue
    style = p.style.name if p.style else ''
    print(f"[{i}] ({style}) {t[:60]}")
