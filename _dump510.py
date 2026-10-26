# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding="utf-8")
from docx import Document
P = r'd:\1\bishe\毕设\7230267148_杨康康_基于opencv和streamlit的图像处理算法交互式演示系统 - 降重改写版.docx'
doc = Document(P)
ps = doc.paragraphs
start = None
for i, p in enumerate(ps):
    if p.text.strip() == "深度学习算法模块" and p.style.name == "论文二级标题":
        start = i
        break
print("5.10 标题索引", start)
for i in range(start, min(start + 22, len(ps))):
    t = ps[i].text.strip()
    print(f"\n[{i}] <{ps[i].style.name}> {t}")
print("\n---- 全文命中 '自研/自行/自己训练/自主训练/预训练/迁移学习' ----")
for i, p in enumerate(ps):
    t = p.text
    for k in ("自研", "自行实现", "自己训练", "自主训练", "自行训练", "预训练", "迁移学习", "从头训练"):
        if k in t:
            print(f"[{i}] {k} :: {t.strip()[:160]}")
            break
