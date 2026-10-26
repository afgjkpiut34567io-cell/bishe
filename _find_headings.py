# -*- coding: utf-8 -*-
"""打印各级标题,用于定位 3.3 与 6.4 章节"""
from docx import Document

PATH = r'd:\1\bishe\毕设\7230267148_杨康康_基于opencv和streamlit的图像处理算法交互式演示系统 - 降重改写版.docx'
doc = Document(PATH)

for i, p in enumerate(doc.paragraphs):
    s = p.style.name if p.style else ''
    if '标题' in s:
        print(f"[{i}] ({s}) {p.text}")
