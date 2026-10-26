# -*- coding: utf-8 -*-
"""用 Word COM 复核：删行后前置页数是否保持 11（绪论物理页码应为 12）"""
import sys
sys.stdout.reconfigure(encoding="utf-8")
import win32com.client as win32

PATH = r'd:\1\bishe\毕设\7230267148_杨康康_基于opencv和streamlit的图像处理算法交互式演示系统 - 降重改写版.docx'
app = win32.gencache.EnsureDispatch("Word.Application")
app.Visible = False
doc = app.Documents.Open(PATH, ReadOnly=True)

print("总页数:", doc.ComputeStatistics(2))  # wdStatisticPages
for i in range(1, doc.Paragraphs.Count + 1):
    p = doc.Paragraphs(i)
    txt = p.Range.Text.strip()
    if txt.startswith("绪论") or txt.startswith("变量注释表"):
        print(f"[{txt[:12]}] 显示页码={p.Range.Information(1)} 物理页码={p.Range.Information(3)}")
doc.Close(False)
app.Quit()
