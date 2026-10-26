# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding="utf-8")
from docx import Document
P = r'd:\1\bishe\毕设\7230267148_杨康康_基于opencv和streamlit的图像处理算法交互式演示系统 - 降重改写版.docx'
doc = Document(P)
for i, p in enumerate(doc.paragraphs):
    if p.text.startswith("系统还基于PyTorch补充了四类"):
        print(f"[{i}] style={p.style.name} runs={len(p.runs)}")
        for j, r in enumerate(p.runs):
            print(f"  run{j} bold={r.bold} sz={r.font.size} name={r.font.name} :: {r.text!r}")
        break
