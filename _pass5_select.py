# -*- coding: utf-8 -*-
"""导出42个标红段落,分3批"""
from docx import Document
import json

doc = Document(r'd:\1\bishe\毕设\7230267148_杨康康_基于opencv和streamlit的图像处理算法交互式演示系统 - 降重改写版2.docx')
red_idx = [51, 82, 84, 91, 92, 93, 112, 117, 120, 121, 123, 125, 132, 138, 181, 182, 183, 185, 186, 209, 232, 260, 263, 277, 278, 296, 297, 298, 300, 301, 308, 309, 319, 323, 329, 331, 332, 343, 344, 345, 346, 348]
items = [{'idx': i, 'text': doc.paragraphs[i].text.strip()} for i in red_idx]
tot = sum(len(i['text']) for i in items)
print(f"42段总字数: {tot}")

per = (len(items) + 2) // 3
for bi in range(3):
    chunk = items[bi*per:(bi+1)*per]
    if chunk:
        with open(rf'd:\1\bishe\_rew\pass5_in{bi}.json', 'w', encoding='utf-8') as f:
            json.dump(chunk, f, ensure_ascii=False, indent=1)
        print(f"  pass5批{bi}: {len(chunk)}段 idx {chunk[0]['idx']}-{chunk[-1]['idx']}, {sum(len(c['text']) for c in chunk)}字")
