# -*- coding: utf-8 -*-
"""分析原始文件AIGC报告中标红段落的分布"""
from docx import Document

doc = Document(r'd:\download\免费_Word标红版_AIGC检测报告_[7230267148_杨康康_基于ope].docx')

paras = doc.paragraphs
print(f"报告总段落数: {len(paras)}")

# 检测所有出现过的字体颜色
colors = {}
for p in paras:
    for r in p.runs:
        if r.font.color and r.font.color.rgb:
            c = str(r.font.color.rgb)
            colors[c] = colors.get(c, 0) + len(r.text)
print("颜色分布(颜色: 字符数):", colors)

# 按段落统计红色占比
para_red = []
for i, p in enumerate(paras):
    t = p.text.strip()
    if not t:
        continue
    red = sum(len(r.text) for r in p.runs if r.font.color and str(r.font.color.rgb) == 'F12828')
    total = sum(len(r.text) for r in p.runs)
    if total > 30:  # 只看有实质内容的段落
        ratio = red / total
        if ratio > 0.3:
            para_red.append((i, t[:50], ratio, total, red))

print(f"\n标红段落数(>30%红, 段落>30字): {len(para_red)}")
red_chars = sum(x[4] for x in para_red)
all_chars = sum(len(p.text) for p in paras)
print(f"标红字符数: {red_chars}, 报告总字符: {all_chars}, 占比约: {red_chars/all_chars*100:.0f}%")
print("\n=== 标红段落明细 ===")
for i, t, r, total, red in para_red:
    print(f"[{i}] ({r*100:.0f}%红/{total}字) {t}")
