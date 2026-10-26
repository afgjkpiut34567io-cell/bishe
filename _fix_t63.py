# -*- coding: utf-8 -*-
"""[审查项#14] 表6-3 题注补分辨率限定，与表清单题名“部分算法平均处理耗时（800×600图像）”一致"""
import sys, shutil
sys.stdout.reconfigure(encoding="utf-8")
from docx import Document

PATH = r'd:\1\bishe\毕设\7230267148_杨康康_基于opencv和streamlit的图像处理算法交互式演示系统 - 降重改写版.docx'
BAK = r'd:\1\bishe\毕设\_bak_降重改写版_20261014_before_t63.docx'
shutil.copy2(PATH, BAK)
print("备份:", BAK)

doc = Document(PATH)
p = None
for q in doc.paragraphs:
    if q.text.startswith("表6-3 "):
        p = q; break
assert p is not None, "未找到表6-3 题注"
print("改前:", repr(p.text))

# 保留中文 run0=‘表’、run4=‘800×600’，其余按新题名填充
新版 = {0: "表", 1: "6-3 ", 2: "部分算法平均处理耗时（", 3: "", 4: "800×600", 5: "图像）"}
for idx, text in 新版.items():
    p.runs[idx].text = text

doc.save(PATH)
print("改后:", repr(p.text))

# 与表清单条目核对
tb = doc.tables[1]
for r in tb.rows:
    if r.cells[0].text.strip() == "表6-3":
        print("表清单:", repr(r.cells[1].text.strip()))
        assert r.cells[1].text.strip() == p.text[4:], "仍不一致"
        print("一致 ✔")
