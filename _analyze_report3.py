# -*- coding: utf-8 -*-
"""分析降重改写版的新AIGC报告"""
from docx import Document

doc = Document(r'd:\download\免费_Word标红版_AIGC检测报告_[7230267148_杨康康_基于ope] (1).docx')
paras = doc.paragraphs
colors = {}
for p in paras:
    for r in p.runs:
        if r.font.color and r.font.color.rgb:
            c = str(r.font.color.rgb)
            colors[c] = colors.get(c, 0) + len(r.text)
print('颜色分布:', colors)

red_paras = []
for i, p in enumerate(paras):
    t = p.text.strip()
    if not t:
        continue
    red = sum(len(r.text) for r in p.runs if r.font.color and str(r.font.color.rgb) == 'F12828')
    total = sum(len(r.text) for r in p.runs)
    if total > 30 and red / total > 0.3:
        red_paras.append((i, t[:45], round(red/total, 2), total))

all_chars = sum(len(p.text) for p in paras)
red_total = colors.get('F12828', 0)
print(f'标红段数: {len(red_paras)}, 报告总字符: {all_chars}')
print(f'红色字符: {red_total}, 占比: {red_total/all_chars*100:.0f}%')
print('=== 标红段落 ===')
for x in red_paras:
    print(x)
