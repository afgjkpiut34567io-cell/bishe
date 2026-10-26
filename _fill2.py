# -*- coding: utf-8 -*-
"""1) 参考样式另存新的过程检查记录表并填写 8 条记录
   2) 填写 3.中期检查表.doc（表头+进展+下一步，日期留空）"""
import sys, os, shutil, time

sys.stdout.reconfigure(encoding="utf-8")
import pythoncom
import win32com.client as wc

D = r"c:\Users\25626\Desktop\7230267148 杨康康 过程检查记录表"
BLANK = os.path.join(D, "4.过程检查记录.doc")
NEW = os.path.join(D, "4.7230267148_杨康康_过程检查记录表.doc")
MID = os.path.join(D, "3.中期检查表.doc")
MID_BAK = os.path.join(D, "3.中期检查表_原始备份.doc")

TEACHER = "漆龙"

RECORDS = [
    ("2027年1月15日",
     "在漆老师的指导下，确定毕业论文题目为“基于OpenCV和Streamlit的图像处理算法交互式演示系统”，完成选题资料的收集与整理，明确系统以图像处理算法的交互式演示为核心功能。"),
    ("2027年2月5日",
     "在漆老师的指导下，完成开题报告与任务书的撰写，梳理图像处理算法与可视化应用的研究现状，确定系统功能需求与总体技术路线，明确界面采用Streamlit、算法以OpenCV与PyTorch实现。"),
    ("2027年2月25日",
     "在漆老师的指导下，完成系统总体设计，按界面层、算法层与数据层进行分层组织，将算法部分划分为六个算法模块与一个训练模块，并明确模块间的调用关系与参数传递方式。"),
    ("2027年3月15日",
     "在漆老师的指导下，完成经典算法与深度学习算法模块的开发，实现六大类30种经典算法与四类深度学习算法共34种，并搭建参数调节面板与处理结果对比界面。"),
    ("2027年3月30日",
     "在漆老师的指导下，开展系统功能测试，逐类验证各算法的处理效果，修正参数传递与结果显示中的问题，并开始整理各算法在不同分辨率图像下的耗时统计数据。"),
    ("2027年4月15日",
     "在漆老师的指导下，完成性能测试数据的整理，补充并发访问实测与连续处理过程中的内存占用变化数据，并按统一口径统计各算法的耗时，形成完整的测试结果。"),
    ("2027年4月30日",
     "在漆老师的指导下，完成论文初稿的撰写，按章节整理系统设计、实现与测试内容，并按学院格式规范统一图表编号、题注与参考文献标注，完成查重与降重修改。"),
    ("2027年5月10日",
     "在漆老师的指导下，完成论文定稿与系统最终版本的整理，核对图表编号与清单页码，并准备系统演示与答辩材料，梳理系统开发过程中的技术要点与创新点。"),
]

PROGRESS = [
    "目前毕业论文已完成绪论、相关理论与技术部分的撰写，正在开始系统设计与分析部分的写作；",
    "已提交任务书与开题报告；",
    "完成系统总体设计，按界面层、算法层与数据层分层组织，算法部分划分为六个算法模块与一个训练模块；",
    "完成算法模块开发与界面搭建，实现六大类30种经典算法与四类深度学习算法共34种，涵盖滤波、图像增强、边缘检测、形态学操作、阈值分割、图像变换以及图像分类、语义分割与超分辨率重建，并完成参数调节面板、处理结果对比与结果导出功能；",
    "已完成系统功能测试，逐类验证各算法的处理效果，结果符合预期，系统运行稳定。",
]

NEXT_PLAN = [
    "（1）完成系统性能测试与数据整理，统计各算法在不同分辨率图像下的耗时，统一采用中位数耗时口径，并补充并发访问与连续处理过程的内存占用数据；",
    "（2）完善深度学习模块的测试，补充超分辨率重建质量对照与加噪前后信噪比对照等实验结果；",
    "（3）排查并修复测试中发现的界面响应与结果显示问题，优化参数调节与图像导出流程，保障系统功能稳定；",
    "（4）整理前期开发成果，形成中期总结材料，明确后续优化方向；",
    "（5）推进论文核心章节撰写，完成系统详细设计与实现、系统测试与结果分析章节，并按要求整理图表与参考文献格式。",
]

HEADER = {"学号": "7230267148", "学生姓名": "杨康康", "班级": "23智科",
          "专业": "智能科学与技术", "指导教师": TEACHER,
          "毕业论文（设计）题目": "基于opencv和streamlit的图像处理算法交互式演示系统"}


def retry(fn, tries=30, delay=0.6):
    last = None
    for _ in range(tries):
        try:
            return fn()
        except pythoncom.com_error as e:
            last = e
            if e.hresult == -2147418111:
                time.sleep(delay)
                continue
            raise
    raise last


def run(path, readonly, job):
    """在独立 Word 实例中打开 path，执行 job(doc)，按需保存"""
    d = os.path.dirname(path)
    lock = os.path.join(d, "~$" + os.path.basename(path)[2:])
    if os.path.exists(lock):
        try:
            os.remove(lock)
        except Exception:
            pass
    app = wc.DispatchEx("Word.Application")
    app.Visible = False
    app.DisplayAlerts = 0
    doc = None
    try:
        doc = retry(lambda: app.Documents.Open(path, ReadOnly=readonly, AddToRecentFiles=False, Visible=False))
        time.sleep(1.5)
        job(doc)
        if not readonly:
            retry(lambda: doc.Save())
            print("   已保存")
    finally:
        try:
            if doc is not None:
                doc.Close(False)
        except Exception as e:
            print("   关闭异常:", e)
        try:
            app.Quit()
        except Exception:
            pass


def set_cell_text(cell, text):
    r = cell.Range
    r.MoveEnd(1, -2)          # 去掉段落标记与单元格结束标记
    r.Text = text


# ==================== 1. 另存新的过程检查记录表 ====================
print("=" * 60)
print("【1】过程检查记录表 ->", os.path.basename(NEW))
shutil.copy2(BLANK, NEW)
print("   已从原始空白件复制")


def fill_record(doc):
    tb = retry(lambda: doc.Tables(1))
    rows = retry(lambda: tb.Rows.Count)
    start = None
    for r in range(1, rows + 1):
        head = retry(lambda r=r: tb.Cell(r, 1).Range.Text).replace('\x07', '').replace(' ', '').strip()
        if head == '日期':
            start = r + 1
            break
    assert start, "未找到记录表头行"
    print(f"   记录起始行={start} 可用行={rows - start + 1}")

    for i, (d, txt) in enumerate(RECORDS):
        row = start + i

        def do(r=row, dd=d, tt=txt):
            dc = tb.Cell(r, 1)
            rc = tb.Cell(r, 2)
            if dd not in dc.Range.Text:
                dc.Range.InsertBefore(dd)
            if tt[:14] not in rc.Range.Text:
                rc.Range.Paragraphs(1).Range.InsertBefore(tt)

        retry(do)
        print(f"   已填 第{i+1}条 {d}")


run(NEW, False, fill_record)

# ==================== 2. 中期检查表 ====================
print("=" * 60)
print("【2】中期检查表 ->", os.path.basename(MID))
if not os.path.exists(MID_BAK):
    shutil.copy2(MID, MID_BAK)
    print("   已备份 ->", os.path.basename(MID_BAK))


def fill_mid(doc):
    tb = retry(lambda: doc.Tables(1))
    print("   表格行数 =", retry(lambda: tb.Rows.Count))

    # 表头
    set_cell_text(retry(lambda: tb.Cell(1, 4)), HEADER["学号"])
    set_cell_text(retry(lambda: tb.Cell(1, 6)), HEADER["学生姓名"])
    set_cell_text(retry(lambda: tb.Cell(2, 2)), HEADER["班级"])
    set_cell_text(retry(lambda: tb.Cell(2, 4)), HEADER["专业"])
    set_cell_text(retry(lambda: tb.Cell(2, 6)), HEADER["指导教师"])
    set_cell_text(retry(lambda: tb.Cell(3, 2)), HEADER["毕业论文（设计）题目"])
    print("   表头已填")

    # 进展：替换含 × 的示例段
    cell = retry(lambda: tb.Cell(4, 1))
    n = retry(lambda: cell.Range.Paragraphs.Count)
    tgt = None
    for i in range(1, n + 1):
        t = retry(lambda i=i: cell.Range.Paragraphs(i).Range.Text)
        if '×' in t:
            tgt = i
            break
    assert tgt, "进展栏未找到示例段"
    rng = retry(lambda: cell.Range.Paragraphs(tgt).Range)
    rng.MoveEnd(1, -1)
    rng.Text = "\r".join(PROGRESS)
    print(f"   进展栏已填（原示例段为第{tgt}段）")

    # 下一步
    cell5 = retry(lambda: tb.Cell(5, 1))
    n5 = retry(lambda: cell5.Range.Paragraphs.Count)
    print(f"   下一步栏原有段落数={n5}")
    rng5 = retry(lambda: cell5.Range.Paragraphs(2).Range)
    rng5.MoveEnd(1, -1)
    rng5.Text = "\r".join(NEXT_PLAN)
    print("   下一步栏已填")

    # 统一格式：小四宋体 + 西文 Times New Roman + 1.5倍行距
    for ci in (4, 5):
        cr = retry(lambda ci=ci: tb.Cell(ci, 1).Range)
        cr.Font.NameFarEast = "宋体"
        cr.Font.NameAscii = "Times New Roman"
        cr.Font.NameOther = "Times New Roman"
        cr.Font.Size = 12
        cr.ParagraphFormat.LineSpacingRule = 1      # 1.5 倍行距
    print("   格式已统一为小四宋体/Times New Roman、1.5倍行距")


run(MID, False, fill_mid)
print("\nDONE")
