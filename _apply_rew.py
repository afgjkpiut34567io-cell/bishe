# -*- coding: utf-8 -*-
"""将改写结果应用到原始docx,生成独立新文件"""
from docx import Document
import json, glob

SRC = r'd:\1\bishe\毕设\7230267148_杨康康_基于opencv和streamlit的图像处理算法交互式演示系统.docx'
DST = r'd:\1\bishe\毕设\7230267148_杨康康_基于opencv和streamlit的图像处理算法交互式演示系统 - 降重改写版.docx'

rew = {}
for f in sorted(glob.glob(r'd:\1\bishe\_rew\b*.json')):
    rew.update(json.load(open(f, encoding='utf-8')))

doc = Document(SRC)
paras = doc.paragraphs
applied, skipped = 0, []
for k, v in rew.items():
    i = int(k)
    p = paras[i]
    if not p.runs:
        skipped.append(i)
        continue
    # 保留首个run的格式,写入新文本,删除其余run
    p.runs[0].text = v
    for r in list(p.runs[1:]):
        r._element.getparent().remove(r._element)
    applied += 1

doc.save(DST)
print(f"已应用: {applied}段, 跳过(无run): {skipped}")
print(f"已保存: {DST}")
