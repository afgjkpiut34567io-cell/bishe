# -*- coding: utf-8 -*-
"""筛出13gram重合率>0.22的段落,分4批供二次改写"""
from docx import Document
import json, glob, re

orig = Document(r'd:\1\bishe\毕设\7230267148_杨康康_基于opencv和streamlit的图像处理算法交互式演示系统.docx').paragraphs
rew = {}
for f in sorted(glob.glob(r'd:\1\bishe\_rew\b*.json')):
    rew.update(json.load(open(f, encoding='utf-8')))

def overlap13(a, b):
    grams = set(b[i:i+13] for i in range(len(b)-12))
    if not grams:
        return 0
    return sum(1 for i in range(len(a)-12) if a[i:i+13] in grams) / max(len(a)-12, 1)

bad = []
for k, v in rew.items():
    o = re.sub(r'\s', '', orig[int(k)].text)
    n = re.sub(r'\s', '', v)
    r = overlap13(o, n)
    if r > 0.22:
        bad.append({'idx': int(k), 'rate': round(r, 2), 'text': v})
bad.sort(key=lambda x: x['idx'])
print(f"需二次改写: {len(bad)}段, 总字数: {sum(len(x['text']) for x in bad)}")

B = 4
per = (len(bad) + B - 1) // B
for bi in range(B):
    chunk = bad[bi*per:(bi+1)*per]
    if chunk:
        with open(rf'd:\1\bishe\_rew\pass2_in{bi}.json', 'w', encoding='utf-8') as f:
            json.dump(chunk, f, ensure_ascii=False, indent=1)
        print(f"  pass2批{bi}: {len(chunk)}段 idx {chunk[0]['idx']}-{chunk[-1]['idx']}")
