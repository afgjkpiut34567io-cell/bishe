# -*- coding: utf-8 -*-
"""列出全部标题 + 含 部署/并发/浏览器/多用户 的段落"""
import sys
sys.stdout.reconfigure(encoding="utf-8")
from docx import Document
PATH = r'd:\1\bishe\毕设\7230267148_杨康康_基于opencv和streamlit的图像处理算法交互式演示系统 - 降重改写版.docx'
doc = Document(PATH)
ps = doc.paragraphs
print(f"段落数={len(ps)}")
print("--- 全部标题 ---")
for i, p in enumerate(ps):
    if p.style.name.startswith("论文"):
        print(f"[{i}] ({p.style.name}) {p.text.strip()[:50]}")
print("--- 关键词命中 ---")
for i, p in enumerate(ps):
    t = p.text
    if any(k in t for k in ["浏览器", "并发", "部署", "多用户", "局域网", "服务器", "同时", "session"]):
        print(f"[{i}] ({p.style.name}) {t[:120]}")
