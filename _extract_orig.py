# -*- coding: utf-8 -*-
"""从原始论文提取需改写段落(摘要+正文+致谢) -> JSON批次"""
from docx import Document
import json, re

SRC = r'd:\1\bishe\毕设\7230267148_杨康康_基于opencv和streamlit的图像处理算法交互式演示系统.docx'
OUT = r'd:\1\bishe\_orig_paras.json'

doc = Document(SRC)
paras = doc.paragraphs
print(f"总段落数: {len(paras)}")

# 先打印结构概览
for i, p in enumerate(paras):
    t = p.text.strip()
    if not t:
        continue
    style = p.style.name if p.style else ''
    if style in ('论文一级标题', '论文二级标题', 'Heading 2', '论文参考文献', '论文参考文献内容') or re.match(r'^(摘|Abstract|Key|关键词|目\s*录|图清单|表清单|变量注释|致\s*谢|参考文献)', t):
        print(f"[{i}] ({style}) {t[:40]}")
