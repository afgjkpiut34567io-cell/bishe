# -*- coding: utf-8 -*-
"""修复 3.中期检查表.doc：
   1) 表头格子残留旧字符（整格重写）
   2) 清掉栏内与参考样式版本重复的旧文字（你自己粘进去的那版）
"""
import sys, os, shutil, time

sys.stdout.reconfigure(encoding="utf-8")
import pythoncom
import win32com.client as wc

D = r"c:\Users\25626\Desktop\7230267148 杨康康 过程检查记录表"
MID = os.path.join(D, "3.中期检查表.doc")
BAK = os.path.join(D, "3.中期检查表_修复前备份.doc")

HEADER = {
    (1, 4): "7230267148",
    (1, 6): "杨康康",
    (2, 2): "23智科",
    (2, 4): "智能科学与技术",
    (2, 6): "漆龙",
}

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


if not os.path.exists(BAK):
    shutil.copy2(MID, BAK)
    print("已备份 ->", os.path.basename(BAK))

lock = os.path.join(D, "~$中期检查表.doc")
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
    doc = retry(lambda: app.Documents.Open(MID, ReadOnly=False, AddToRecentFiles=False, Visible=False))
    time.sleep(1.5)
    tb = retry(lambda: doc.Tables(1))

    # --- 1) 表头整格重写 ---
    for (r, c), v in HEADER.items():
        cell = retry(lambda r=r, c=c: tb.Cell(r, c))
        old = " ".join(retry(lambda: cell.Range.Text).replace('\x07', '').split())
        retry(lambda: setattr(cell.Range, 'Text', v))
        retry(lambda: setattr(cell.Range.Font, 'Size', 12))
        cell.Range.Font.NameFarEast = "宋体"
        cell.Range.Font.NameAscii = "Times New Roman"
        print(f"   行{r}列{c}: {old!r} -> {v!r}")

    # --- 2) 清理栏内旧文字 ---
    for row, keep, tag in ((4, PROGRESS, "进展"), (5, NEXT_PLAN, "下一步")):
        cell = retry(lambda row=row: tb.Cell(row, 1))
        n = retry(lambda: cell.Range.Paragraphs.Count)
        to_del, texts = [], []
        for i in range(1, n + 1):
            t = retry(lambda i=i: cell.Range.Paragraphs(i).Range.Text).replace('\x07', '').strip()
            if i == 1 or not t or t in keep:
                continue
            to_del.append(i)
            texts.append(t)
        for i in reversed(to_del):
            retry(lambda i=i: cell.Range.Paragraphs(i).Range.Delete())
        print(f"   {tag}栏：删除重复旧段 {len(to_del)} 段")
        for t in texts:
            print(f"       - {t[:52]}")

    # --- 3) 格式复核 ---
    for row in (4, 5):
        cr = retry(lambda row=row: tb.Cell(row, 1).Range)
        cr.Font.NameFarEast = "宋体"
        cr.Font.NameAscii = "Times New Roman"
        cr.Font.Size = 12
        cr.ParagraphFormat.LineSpacingRule = 1
    print("   格式已复核：小四宋体 / Times New Roman / 1.5倍行距")

    retry(lambda: doc.Save())
    print("已保存")
finally:
    try:
        if doc is not None:
            doc.Close(False)
    except Exception as e:
        print("关闭异常:", e)
    try:
        app.Quit()
    except Exception:
        pass
print("DONE")
