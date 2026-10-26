# -*- coding: utf-8 -*-
"""精确核算表6-3(双列对布局)的均值/中位数/样本数"""
from docx import Document
import statistics

PATH = r'd:\1\bishe\毕设\7230267148_杨康康_基于opencv和streamlit的图像处理算法交互式演示系统 - 降重改写版.docx'
doc = Document(PATH)

tb = doc.tables[16]
vals = []
for r in tb.rows[1:]:
    cells = [c.text.strip() for c in r.cells]
    for i in (1, 3):
        if i < len(cells): 
            s = cells[i].replace('ms', '').strip()
            try:
                vals.append(float(s))
            except Exception:
                pass
print("耗时序列:", vals)
print(f"样本数={len(vals)} 均值={statistics.mean(vals):.3f}ms 中位数={statistics.median(vals):.3f}ms")
