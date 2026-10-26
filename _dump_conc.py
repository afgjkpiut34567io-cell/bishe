# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding="utf-8")
from docx import Document

P = r'd:\1\bishe\毕设\7230267148_杨康康_基于opencv和streamlit的图像处理算法交互式演示系统 - 降重改写版.docx'
doc = Document(P)
ps = doc.paragraphs
print("段落总数", len(ps))
for i, p in enumerate(ps):
    t = p.text.strip()
    if not t:
        continue
    if 120 <= i <= 150 or 270 <= i <= 320:
        print(f"[{i}] <{p.style.name}> {t[:110]}")
