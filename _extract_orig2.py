# -*- coding: utf-8 -*-
"""从原始论文提取需改写段落(中文摘要+正文+致谢) -> JSON批次"""
from docx import Document
import json, re

SRC = r'd:\1\bishe\毕设\7230267148_杨康康_基于opencv和streamlit的图像处理算法交互式演示系统.docx'
OUT = r'd:\1\bishe\_orig_paras.json'

doc = Document(SRC)
paras = doc.paragraphs

SKIP_STYLES = {'论文一级标题', '论文二级标题', 'Heading 2', 'Heading 3', '论文参考文献', '论文参考文献内容', 'Caption', 'Plain Text'}

def is_code(t):
    s = t.lstrip()
    return s.startswith(('def ', 'return', 'import ', 'from ', 'if ', 'for ', 'cv2.', 'np.', 'algo_', 'gray ', 'blur', '#', '    '))

def is_caption(t):
    return bool(re.match(r'^(图\d|表\d|续表|（\d|式\(|注：)', t.strip()))

RANGES = [(50, 52), (80, 317), (358, 360)]
items = []
for lo, hi in RANGES:
    for i in range(lo, hi):
        p = paras[i]
        t = p.text
        ts = t.strip()
        if not ts:
            continue
        style = p.style.name if p.style else ''
        if style in SKIP_STYLES:
            continue
        if is_caption(ts) or is_code(t):
            continue
        items.append({'idx': i, 'len': len(ts), 'text': ts})

total = sum(it['len'] for it in items)
print(f"待改写段落数: {len(items)}, 总字数: {total}")

batches, cur, cur_len = [], [], 0
for it in items:
    cur.append(it)
    cur_len += it['len']
    if cur_len >= 3200:
        batches.append(cur)
        cur, cur_len = [], 0
if cur:
    batches.append(cur)

print(f"批次数: {len(batches)}")
for bi, b in enumerate(batches):
    print(f"  批{bi}: {len(b)}段, {sum(x['len'] for x in b)}字, idx {b[0]['idx']}-{b[-1]['idx']}")

with open(OUT, 'w', encoding='utf-8') as f:
    json.dump(batches, f, ensure_ascii=False, indent=1)
print("已写出:", OUT)
