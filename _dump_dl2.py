# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding="utf-8")
from docx import Document
PATH = r'd:\1\bishe\毕设\7230267148_杨康康_基于opencv和streamlit的图像处理算法交互式演示系统 - 降重改写版.docx'
doc = Document(PATH)
ps = doc.paragraphs
for i in range(228, 262):
    p = ps[i]
    print(f"[{i}] ({p.style.name}) {p.text}")
print("--- 表5-8 出现处 ---")
for i, p in enumerate(ps):
    if "表5-8" in p.text:
        print(f"[{i}] {p.text[:60]}")
print("--- 含 图5-4/5-5/5-6 题注 ---")
for i, p in enumerate(ps):
    t = p.text.strip()
    if t.startswith("图5-4") or t.startswith("图5-5") or t.startswith("图5-6"):
        print(f"[{i}] {t}")
