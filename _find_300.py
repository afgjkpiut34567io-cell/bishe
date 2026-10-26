# -*- coding: utf-8 -*-
"""定位 300ms 指标、摘要、6.4 结论 相关段落"""
from docx import Document

PATH = r'd:\1\bishe\毕设\7230267148_杨康康_基于opencv和streamlit的图像处理算法交互式演示系统 - 降重改写版.docx'
doc = Document(PATH)

keys = ["300", "毫秒", "实时性", "3ms", "响应延迟", "响应速度", "耗时"]
for i, p in enumerate(doc.paragraphs):
    t = p.text
    if any(k in t for k in keys):
        print(f"[{i}] {t}")
        print("-" * 70)
