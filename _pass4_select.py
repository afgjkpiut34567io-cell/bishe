# -*- coding: utf-8 -*-
"""导出57个标红段落,分3批"""
from docx import Document
import json

doc = Document(r'd:\1\bishe\毕设\7230267148_杨康康_基于opencv和streamlit的图像处理算法交互式演示系统 - 降重改写版.docx')
red = json.load(open(r'd:\1\bishe\_red_paras.json', encoding='utf-8'))
mapping = json.load(open(r'd:\1\bishe\_red_map.json', encoding='utf-8'))
items = [{'idx': mapping[str(x[0])], 'text': doc.paragraphs[mapping[str(x[0])]].text.strip()} for x in red]
items.sort(key=lambda i: i['idx'])
tot = sum(len(i['text']) for i in items)
print(f"57段总字数: {tot}")

per = (len(items) + 2) // 3
for bi in range(3):
    chunk = items[bi*per:(bi+1)*per]
    if chunk:
        with open(rf'd:\1\bishe\_rew\pass4_in{bi}.json', 'w', encoding='utf-8') as f:
            json.dump(chunk, f, ensure_ascii=False, indent=1)
        print(f"  pass4批{bi}: {len(chunk)}段 idx {chunk[0]['idx']}-{chunk[-1]['idx']}, {sum(len(c['text']) for c in chunk)}字")
