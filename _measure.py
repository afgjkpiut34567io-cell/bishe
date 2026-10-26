# -*- coding: utf-8 -*-
"""测量降重版: 页数/总字数/各章字数占比"""
from docx import Document
import re, zipfile

SRC = r'd:\1\bishe\毕设\2   7230267148_杨康康_基于opencv和streamlit的图像处理算法交互式演示系统 - 降重版.docx'

# 1. 页数(app.xml)
with zipfile.ZipFile(SRC) as z:
    app = z.read('docProps/app.xml').decode('utf-8', 'ignore')
m = re.search(r'<Pages>(\d+)</Pages>', app)
print(f"docProps记录页数: {m.group(1) if m else '未知'}")

doc = Document(SRC)

# 2. 全文字数(段落+表格)
def count_chars(text):
    return len(re.sub(r'\s', '', text))

para_chars = sum(count_chars(p.text) for p in doc.paragraphs)
tbl_chars = 0
for t in doc.tables:
    for row in t.rows:
        for c in row.cells:
            tbl_chars += count_chars(c.text)
print(f"段落字符数(不计空格): {para_chars}")
print(f"表格字符数: {tbl_chars}")
print(f"全文总字符数: {para_chars + tbl_chars}")

# 3. 按章统计(以一级标题分段)
chapters = []
cur_name, cur_chars = "前置部分", 0
for p in doc.paragraphs:
    style = p.style.name if p.style else ''
    t = p.text.strip()
    if style == '论文一级标题' and t:
        chapters.append((cur_name, cur_chars))
        cur_name, cur_chars = t, 0
        continue
    cur_chars += count_chars(p.text)
chapters.append((cur_name, cur_chars))

print("\n=== 按一级标题分章字数 ===")
for name, c in chapters:
    print(f"{name}: {c}字")
