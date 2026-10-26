# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding="utf-8")
from docx import Document
PATH = r'd:\1\bishe\毕设\7230267148_杨康康_基于opencv和streamlit的图像处理算法交互式演示系统 - 降重改写版.docx'
doc = Document(PATH)
ps = doc.paragraphs
print("--- 含 浏览器/访问/网址/本地/分享/发布 的段落 ---")
for i, p in enumerate(ps):
    t = p.text
    if any(k in t for k in ["浏览器", "访问", "网址", "分享", "发布", "local", "8501", "端口"]):
        print(f"[{i}] ({p.style.name}) {t[:160]}")
print("\n--- 第3章 需求分析 区域 [126..146] ---")
for i in range(126, 147):
    print(f"[{i}] ({ps[i].style.name}) {ps[i].text[:150]}")
