# -*- coding: utf-8 -*-
"""验证：Information(1)=显示页码(adjusted) vs Information(3)=物理页码"""
import sys
sys.stdout.reconfigure(encoding="utf-8")
import win32com.client as wc
PATH = r'd:\1\bishe\毕设\7230267148_杨康康_基于opencv和streamlit的图像处理算法交互式演示系统 - 降重改写版.docx'
app = wc.Dispatch("Word.Application"); app.Visible = False
d = app.Documents.Open(PATH, ReadOnly=True)
try:
    for probe in ["图6-1", "表6-3", "表6-4", "图3-1", "表5-1"]:
        for para in d.Paragraphs:
            if para.Range.Information(12):
                continue
            t = para.Range.Text.replace("\r", "").replace("\x07", "").strip()
            if t.startswith(probe) and len(t) > len(probe) + 1:
                print(f"{probe}: adjusted(1)={para.Range.Information(1)} phys(3)={para.Range.Information(3)}")
                break
    print("--- 前置页(罗马/无编号区)行数探测 ---")
    n = 0
    for para in d.Paragraphs:
        n += 1
        t = para.Range.Text.replace("\r", "").replace("\x07", "").strip()
        if t.startswith("绪论") or t.startswith("第1章"):
            print("首个正文标题出现于段落#", n, "adj=", para.Range.Information(1), "phys=", para.Range.Information(3), repr(t[:30]))
            break
finally:
    d.Close(False); app.Quit()
