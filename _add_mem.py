# -*- coding: utf-8 -*-
"""
6.3 补内存实测：文字段 + 表6-5（预训练模型常驻内存表）+ 图6-3（内存增长曲线）
同时把 6.4 现有 表6-5/表6-6 顺延为 表6-6/表6-7、图6-3 顺延为 图6-4
"""
import sys, copy, shutil
sys.stdout.reconfigure(encoding="utf-8")
from docx import Document
from docx.shared import Cm, Pt
from docx.oxml import OxmlElement
from docx.text.paragraph import Paragraph
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT

PATH = r'd:\1\bishe\毕设\7230267148_杨康康_基于opencv和streamlit的图像处理算法交互式演示系统 - 降重改写版.docx'
BAK = r'd:\1\bishe\毕设\_bak_降重改写版_20261014_before_mem.docx'
FIG = r'd:\1\bishe\figures\fig6_3_内存增长曲线.png'
shutil.copy2(PATH, BAK)
print("备份:", BAK)

doc = Document(PATH)


def para_after(el, parent):
    p_el = OxmlElement('w:p')
    el.addnext(p_el)
    return Paragraph(p_el, parent)


def body_after(el, parent, text):
    p = para_after(el, parent)
    p.add_run(text)
    p.paragraph_format.first_line_indent = Pt(24)
    p.paragraph_format.line_spacing = 1.5
    return p


def caption_after(el, parent, text):
    p = para_after(el, parent)
    p.add_run(text)
    p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.line_spacing = 1.5
    return p


def picture_after(el, parent, path, width_cm=13.5):
    p = para_after(el, parent)
    p.add_run().add_picture(path, width=Cm(width_cm))
    p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    return p


def table_after(el, header, rows, widths):
    tbl = doc.add_table(rows=len(rows) + 1, cols=len(header))
    tbl.style = doc.styles['Table Grid']
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    el.addnext(tbl._tbl)
    for j, h in enumerate(header):
        c = tbl.rows[0].cells[j]; c.text = ''
        cc = c.paragraphs[0]; cc.add_run(h); cc.alignment = WD_ALIGN_PARAGRAPH.CENTER
    for i, row in enumerate(rows):
        for j, v in enumerate(row):
            c = tbl.rows[i + 1].cells[j]; c.text = ''
            cc = c.paragraphs[0]; cc.add_run(str(v)); cc.alignment = WD_ALIGN_PARAGRAPH.CENTER
    for r in tbl.rows:
        for j, w in enumerate(widths):
            r.cells[j].width = Cm(w)
    return tbl


def set_cell_text(cell, text):
    p = cell.paragraphs[0]
    if p.runs:
        p.runs[0].text = text
        for r in p.runs[1:]:
            r._element.getparent().remove(r._element)
    else:
        p.add_run(text)


def renum(marks, old, new):
    n = 0
    for p in doc.paragraphs:
        t = p.text
        if old in t and any(t.startswith(m) for m in marks):
            for r in p.runs:
                if old in r.text:
                    r.text = r.text.replace(old, new); n += 1
    print(f"  {old} -> {new}: {n} run")
    return n


# ---------- 1) 先把旧编号腾出来 ----------
MF3 = ["为了把关键参数对处理效果的影响", "图6-3 代表性算法关键参数取值-效果消融曲线", "图6-3给出几条规律"]
M66 = ["去噪效果用加噪前后的信噪比变化", "表6-6 加噪前后信噪比对照表", "从表6-6能读到"]
M65 = ["超分辨率这一块", "表6-5 超分辨率重建质量对照表", "表6-5里的数据说明"]
renum(M66, "表6-6", "表6-7")
renum(M65, "表6-5", "表6-6")
renum(MF3, "图6-3", "图6-4")

# ---------- 2) 定位锚点：6.3 并发解读段 ----------
anchor = None
for p in doc.paragraphs:
    if p.text.startswith("从表6-4的数据能看到"):
        anchor = p; break
assert anchor is not None, "未找到 6.3 并发解读段"
parent = anchor._parent
cur = anchor._p

P1 = ("除了并发访问的情况，测试环节顺带把内存占用也看了一遍。连续处理这块的做法是尽量贴近真实使用："
      "挑高斯滤波、中值滤波、均值滤波、双边滤波、伽马校正、Canny边缘检测、Otsu阈值分割、图像缩放和傅里叶低通这九种算法，"
      "每一轮让参数做一点小变化，连续跑120轮，每10轮记一次进程的驻留内存，全程按800×600的图来处理。"
      "测下来，不带结果缓存时，驻留内存很快就涨到232.8MB左右并且稳住了，一直到最后都没有再往上走，"
      "过程的峰值是261.1MB，出现在某次大数组分配的时候；带上结果缓存以后，曲线就成了一路上升的形态，"
      "从221.1MB起步，到第120轮是342.0MB，峰值366.3MB，整段增长约120.9MB。两条曲线的走向如图6-3所示。")
cur = body_after(cur, parent, P1)._p
cur = picture_after(cur, parent, FIG)._p
cur = caption_after(cur, parent, "图6-3 连续处理过程的进程驻留内存变化曲线")._p

P2 = ("常驻模型的驻留内存另外单独测了一轮。先把torch和torchvision导入进来量一个底数，再依次加载四个模型，"
      "记录每次加载前后的驻留内存变化。结果是，深度学习依赖本身（torch与torchvision）就先占掉了约247MB；"
      "模型部分，MobileNetV2加载完增加了31.4MB，DeepLabV3增加58.6MB，SRCNN的网很小，几乎看不出变化，"
      "CIFAR10Net增加0.6MB，四个模型合起来约90.6MB；加载过程中进程峰值到过380.7MB，随后回落到324MB上下，"
      "也就是权重文件读取时用到的临时缓冲后来被释放掉了。各项数据见表6-5。")
cur = body_after(cur, parent, P2)._p
cur = caption_after(cur, parent, "表6-5 预训练模型常驻内存表")._p

tbl = table_after(cur, ["模型", "参数量", "权重文件大小", "加载后驻留内存增量（MB）"], [
    ["MobileNetV2（图像分类）", "3,504,872", "约13.6MB", "31.4"],
    ["DeepLabV3（语义分割）", "11,029,328", "约42.3MB", "58.6"],
    ["SRCNN（超分辨率）", "8,129", "约0.03MB", "0.0"],
    ["CIFAR10Net（自定义分类）", "620,362", "约2.4MB", "0.6"],
    ["合计", "15,162,691", "约58.3MB", "90.6"],
], [3.8, 3.2, 3.2, 4.6])
cur = tbl._tbl

P3 = ("释放策略得分成两类内存来说。一类是模型，四个深度学习模型都由st.cache_resource托管，"
      "进程里只常驻一份、所有会话共用，页面刷新或者会话结束了都不会把它们放掉，"
      "这么设计换来的是每次交互不必重新加载，代价是这部分内存在服务运行的整个期间一直被占着，"
      "想放掉只能停掉服务进程，或者直接调用st.cache_resource.clear()，"
      "系统目前在界面上没给出清理缓存的入口，实际用的时候多是靠重启服务来回收。"
      "另一类是处理结果，它挂在st.cache_data上，键是图像、算法和参数三样，重复的交互不会重算，"
      "可参数一变或者图像一换就要新占一条，Streamlit对这类缓存默认不限制条目个数，"
      "所以前一条一直往上爬的曲线，主要就是这些缓存条目堆出来的；"
      "配置里其实预留了CACHE_TTL这个过期时间常量（300秒），只是还没接到缓存装饰器上用，"
      "另外也可以给缓存设个条目上限，或者补一个手动清理的入口。"
      "至于算法计算过程中用到的临时数组，像滤波核、频域变换的矩阵，算完就交给Python的垃圾回收，"
      "不会长期留着，这也解释了不带缓存那条曲线为什么很快就平了。")
p = para_after(cur, parent)
p.add_run(P3)
p.paragraph_format.first_line_indent = Pt(24)
p.paragraph_format.line_spacing = 1.5

# ---------- 3) 同步前置清单 ----------
fl = doc.tables[0]
frows = {r.cells[0].text.strip(): r for r in fl.rows[1:]}
set_cell_text(frows["图6-3"].cells[0], "图6-4")
nf = fl.add_row()
frows["图6-2"]._tr.addnext(nf._tr)
set_cell_text(nf.cells[0], "图6-3")
set_cell_text(nf.cells[1], "连续处理过程的进程驻留内存变化曲线")
set_cell_text(nf.cells[2], "36")

tl = doc.tables[1]
trows = {r.cells[0].text.strip(): r for r in tl.rows[1:]}
set_cell_text(trows["表6-6"].cells[0], "表6-7")
set_cell_text(trows["表6-5"].cells[0], "表6-6")
nt = tl.add_row()
trows["表6-4"]._tr.addnext(nt._tr)
set_cell_text(nt.cells[0], "表6-5")
set_cell_text(nt.cells[1], "预训练模型常驻内存表")
set_cell_text(nt.cells[2], "36")

doc.save(PATH)
print("已保存。段落", len(doc.paragraphs), "表格", len(doc.tables))
print("--- 图清单 ---")
for r in fl.rows:
    print("  ", [c.text.strip() for c in r.cells])
print("--- 表清单 ---")
for r in tl.rows:
    print("  ", [c.text.strip() for c in r.cells])
