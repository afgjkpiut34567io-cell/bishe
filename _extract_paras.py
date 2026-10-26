# -*- coding: utf-8 -*-
"""提取降重版正文需要改写的段落全文 -> JSON"""
from docx import Document
import json, re

SRC = r'd:\1\bishe\毕设\2   7230267148_杨康康_基于opencv和streamlit的图像处理算法交互式演示系统 - 降重版.docx'
OUT = r'd:\1\bishe\_paras_to_rewrite.json'

doc = Document(SRC)
paras = doc.paragraphs

SKIP_STYLES = {'论文一级标题', '论文二级标题', 'Heading 2', '论文参考文献', '论文参考文献内容', 'Caption'}

def is_code(t):
    s = t.lstrip()
    return s.startswith(('def ', 'return', 'import ', 'from ', 'if ', 'for ', 'cv2.', 'np.', 'algo_', 'gray ', 'ksize', 'gamma', 'blur', 'image', '#'))

def is_caption(t):
    return bool(re.match(r'^(图\d+|表\d+|续表\d+|（5\.\d+）|式\(5)', t.strip()))

items = []
for i in range(76, 375):  # 正文范围
    p = paras[i]
    t = p.text
    ts = t.strip()
    if not ts:
        continue
    style = p.style.name if p.style else ''
    if style in SKIP_STYLES:
        continue
    if is_caption(ts):
        continue
    if is_code(t):
        continue
    # 有内容的正文段落
    items.append({'idx': i, 'len': len(ts), 'text': ts})

total_chars = sum(it['len'] for it in items)
print(f"待改写段落数: {len(items)}, 总字数: {total_chars}")

# 按章节分批,每批约2500-3500字
batches = []
cur, cur_len = [], 0
for it in items:
    cur.append(it)
    cur_len += it['len']
    if cur_len >= 3000:
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
