# -*- coding: utf-8 -*-
"""核对表6-2内容是否已替换"""
from docx import Document

PATH = r'd:\1\bishe\毕设\7230267148_杨康康_基于opencv和streamlit的图像处理算法交互式演示系统 - 降重改写版.docx'
doc = Document(PATH)
for tb in doc.tables:
    if not tb.rows:
        continue
    hdr = [c.text.strip() for c in tb.rows[0].cells]
    if hdr[:2] == ["测试项", "测试内容"] and hdr[-1] == "实际结果":
        print("表头:", hdr)
        for row in tb.rows[1:]:
            print(" | ".join(c.text.strip() for c in row.cells))
