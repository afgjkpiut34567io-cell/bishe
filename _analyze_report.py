# -*- coding: utf-8 -*-
"""分析报告中标红段落的分布"""
from docx import Document
import re

doc = Document(r'd:\download\免费_Word标红版_AIGC检测报告_[2 7230267148_杨康康_基于o].docx')

# 按段落统计红色字符占比
para_red = []
for i, p in enumerate(doc.paragraphs):
    t = p.text.strip()
    if not t:
        continue
    red = sum(len(r.text) for r in p.runs if r.font.color and str(r.font.color.rgb) == 'F12828')
    total = sum(len(r.text) for r in p.runs if r.font.color and r.font.color.rgb)
    if total > 0:
        ratio = red / total
        if ratio > 0.3:  # 30%以上标红
            para_red.append((i, t[:70], ratio, total))

print(f"高度标红段落数(>30%红): {len(para_red)}")
# 按章节位置分组
for i, t, r, total in para_red[:40]:
    print(f"[{i}] ({r*100:.0f}%红, {total}字) {t}...")
