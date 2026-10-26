"""
填写任务书和开题报告脚本
使用 Word COM 自动化，保留学校模板格式
"""

import sys
import os
import win32com.client

sys.stdout.reconfigure(encoding="utf-8")

# ==================== 基本信息 ====================
TITLE = "基于OpenCV和Streamlit的图像处理算法交互式演示系统"
NAME = "XXX"
MAJOR = "智能科学与技术"
GRADE = "2023级"
STUDENT_ID = "XXX"
ADVISOR = "XXX"

# ==================== 任务书 - 本课题目标 ====================
OBJECTIVES = (
    "本课题旨在设计并实现一个基于OpenCV和Streamlit的"
    "图像处理算法交互式演示系统，以解决传统图像处理教学中算法原理抽象、"
    "学习门槛高、缺乏直观交互式演示工具的核心问题。具体目标如下：\n"
    "（1）构建覆盖滤波、图像增强、边缘检测、形态学操作、阈值分割和图像变换"
    "六大类共30种常用图像处理算法的算法库；\n"
    "（2）为每种算法提供滑块、下拉菜单、单选按钮等交互组件，实现参数实时调节，"
    "确保参数调整后0.5秒内更新处理结果预览；\n"
    "（3）针对关键算法，通过Matplotlib动态展示中间处理步骤、直方图变化及"
    "频域分布等数据曲线，增强算法原理的可理解性；\n"
    "（4）提供包含算法原理说明、核心代码片段、参数作用解释及典型应用场景的"
    "教学辅助功能；\n"
    "（5）实现图像上传、处理结果保存与下载、算法分类导航等完整的用户操作流程。"
)

# ==================== 任务书 - 本课题的任务和要求 ====================
TASKS = (
    "任务：\n"
    "（1）完成图像处理算法理论调研，梳理常用算法的分类体系与核心原理；\n"
    "（2）基于Python语言和OpenCV库实现滤波、增强、边缘检测、形态学、分割、"
    "变换等六大类30种图像处理算法；\n"
    "（3）采用模块化设计思想，将算法实现、参数管理、可视化展示与UI交互进行"
    "分层解耦；\n"
    "（4）基于Streamlit框架构建交互式Web界面，实现参数滑块实时调节、"
    "原图与结果对比、算法分类导航等功能；\n"
    "（5）基于Matplotlib实现算法中间步骤、直方图对比、伽马校正曲线、"
    "频率域分析等教学可视化；\n"
    "（6）编写算法原理说明、参数解释、核心代码片段和典型应用场景等教学资料；\n"
    "（7）进行系统性能测试与优化，完成毕业论文撰写与系统演示。\n"
    "要求：\n"
    "（1）系统须在普通配置计算机上流畅运行，参数调节无明显卡顿；\n"
    "（2）支持JPG、PNG、BMP等常见图像格式的上传与处理；\n"
    "（3）实现处理结果的保存与下载功能；\n"
    "（4）系统运行稳定，支持连续多张图像处理。"
)

# ==================== 任务书 - 课题进度安排 ====================
# (年份, 起止日期, 任务内容)
SCHEDULE_TASK = [
    ("2025", "11月1日～11月30日", "查阅文献资料，进行课题调研，明确研究目标与内容"),
    ("2025", "12月1日～12月15日", "完成需求分析，撰写开题报告"),
    ("2025", "12月16日～12月20日", "完成开题答辩"),
    ("2025", "12月21日～12月31日", "确定系统总体设计与技术方案"),
    ("2026", "1月1日～2月28日", "实现滤波、增强、边缘检测等核心算法模块"),
    ("2026", "3月1日～3月31日", "实现形态学、分割、变换算法及交互式界面开发"),
    ("2026", "4月1日～4月30日", "系统集成、功能测试与性能优化"),
    ("2026", "5月1日～5月20日", "撰写毕业论文"),
    ("2026", "5月21日～6月10日", "论文修改、定稿与答辩准备"),
]

# ==================== 开题报告 - 研究目的和意义 ====================
PURPOSE = (
    "研究目的：\n"
    "图像处理是计算机视觉和人工智能领域的基础性技术，广泛应用于医疗影像、"
    "工业检测、安防监控、自动驾驶等众多领域。然而，图像处理算法通常以数学公式"
    "和静态图片的形式进行讲授，算法原理抽象、处理过程不可见，导致初学者学习门槛"
    "高、理解困难。本课题旨在设计并实现一个基于OpenCV和"
    "Streamlit的图像处理算法交互式演示系统，将抽象的图像处理算法原理转化为"
    "直观、可交互的视觉体验，通过实时参数调节和中间步骤可视化，帮助学生建立对"
    "算法的直观理解，降低学习门槛，提升教学效果。\n"
    "研究意义：\n"
    "（1）教学层面：传统图像处理教学以公式推导和静态图片为主，学生难以直观理解"
    "算法的处理过程和参数影响。本系统通过参数实时调节和算法步骤可视化，将"
    "“抽象公式”转化为“视觉经验”，弥补了传统教学方式的不足；\n"
    "（2）应用层面：图像处理技术是人工智能人才培养的重要内容，掌握核心算法原理"
    "是相关专业学生开展后续学习和研究的基础，本系统有助于夯实学生的专业基础；\n"
    "（3）技术层面：本课题验证了Python生态下“OpenCV算法引擎+Streamlit交互框架"
    "+Matplotlib可视化”的轻量级图像处理演示系统构建方案，为同类系统的开发提供"
    "参考和借鉴。"
)

# ==================== 开题报告 - 课题研究现状 ====================
CURRENT_STATUS = (
    "图像处理算法教学工具的发展大致经历了三个阶段：早期以MATLAB GUI为核心的"
    "图像处理实验系统，算法库丰富、开发便捷，但依赖商业软件、可移植性差、"
    "不利于网络传播；随后出现了基于PyQt或C++的桌面端教学系统，功能较为完善，"
    "但界面开发成本高、跨平台部署困难；近年来，随着Web技术的成熟，基于Streamlit、"
    "Dash等框架的交互式图像处理演示系统逐渐兴起，具有部署便捷、交互直观、"
    "便于分享等优势，成为图像处理教学工具的发展趋势。\n"
    "当前相关研究仍存在以下不足：一是算法覆盖不够全面，多数平台仅集成十余种"
    "基础算法，难以满足教学大纲对算法体系的完整覆盖要求；二是缺乏算法中间步骤的"
    "可视化展示，难以揭示算法内部的处理机制；三是教学辅助功能较为薄弱，缺少原理"
    "说明、参数解释和代码展示的有机结合；四是部分平台性能优化不足，参数调节响应"
    "延迟明显，影响交互体验。\n"
    "针对上述不足，本课题拟构建一个覆盖六大类30种算法、融合实时交互与步骤可视化、"
    "具备完整教学辅助功能的综合性图像处理算法交互式演示系统。"
)

# ==================== 开题报告 - 主要内容、实施方案及创新点 ====================
MAIN_CONTENT = (
    "一、研究主要内容\n"
    "（1）算法库建设：集成滤波、图像增强、边缘检测、形态学操作、阈值分割和"
    "图像变换六大类共30种常用图像处理算法，覆盖教学大纲核心知识点；\n"
    "（2）参数交互调节：为每种算法提供滑块、下拉菜单、单选按钮等交互组件，"
    "实现参数的实时调节；\n"
    "（3）实时预览机制：建立高效的图像处理流水线，确保参数调整后0.5秒内更新"
    "处理结果预览；\n"
    "（4）算法步骤可视化：针对关键算法，通过Matplotlib动态展示中间处理步骤、"
    "直方图变化及频域分布等数据曲线；\n"
    "（5）教学辅助功能：提供算法原理说明、核心代码片段、参数作用解释及典型"
    "应用场景介绍。\n"
    "二、实施方案\n"
    "系统采用模块化四层架构：UI层（Streamlit）、算法层（OpenCV）、可视化层"
    "（Matplotlib）、工具层（图像IO与性能优化）。算法层按类别划分为滤波、增强、"
    "边缘检测、形态学、分割、变换六个模块，每个算法函数接收图像和参数字典并返回"
    "处理结果；UI层通过侧边栏实现算法分类导航和参数面板，通过标签页组织预览、"
    "步骤可视化和教学面板；可视化层使用Matplotlib绘制直方图对比、步骤网格、"
    "伽马曲线、频域分析等图表。性能优化方面，采用图像自动缩放、结果缓存、参数"
    "变更检测等策略保障响应速度。\n"
    "三、创新点\n"
    "（1）采用“算法原理+核心代码+参数详解+应用场景”四维一体的教学资料组织方式，"
    "实现理论、代码与实践的有机结合；\n"
    "（2）针对关键算法设计了多阶段的中间步骤可视化，直观揭示算法内部处理机制；\n"
    "（3）采用Web端交互式架构，相比传统桌面端工具具有部署便捷、跨平台、"
    "易于分享的优势。"
)

# ==================== 开题报告 - 主要参考文献 ====================
# 说明：[1]-[6]为知网可检索的中文期刊/学位论文，[7]-[9]为外文文献（Web of Science / IEEE Xplore 检索）
REFERENCES = (
    "[1] 王文成, 李健, 王瑞兰, 等. 基于Matlab GUI的数字图像处理仿真平台"
    "设计与开发[J]. 实验技术与管理, 2019, 36(2).\n"
    "[2] 刘丽娟. 基于MATLAB GUI的图像处理辅助教学平台设计与开发[J]. "
    "电子元器件与信息技术, 2021, 5(3): 181-183.\n"
    "[3] 李振杰, 臧春华, 苏宝玉, 等. 基于OpenCV图像处理软件的设计[J]. "
    "物联网技术, 2024, 14(6).\n"
    "[4] 杨蕊遥. 基于嵌入式和OpenCV的智能视频监控系统研究[D]. "
    "大连: 大连海事大学, 2018.\n"
    "[5] 贾小军, 喻擎苍. 基于开源计算机视觉库OpenCV的图像处理[J]. "
    "计算机应用与软件, 2008, 25(4): 276-278.\n"
    "[6] 刘立强, 蔡晓华, 吴泽全. 基于OpenCV的除草机器人图像处理技术[J]. "
    "农机化研究, 2013(12): 162-165.\n"
    "[7] Canny J. A computational approach to edge detection[J]. IEEE "
    "Transactions on Pattern Analysis and Machine Intelligence, 1986, 8(6): 679-698.\n"
    "[8] Otsu N. A threshold selection method from gray-level histograms[J]. "
    "IEEE Transactions on Systems, Man, and Cybernetics, 1979, 9(1): 62-66.\n"
    "[9] Shalini G M, Anand R, Sankeerth T, et al. Integrated colorization "
    "and styling approach for enhancing image clarity[C]//2024 3rd International "
    "Conference on Applied Artificial Intelligence and Computing (ICAAIC). "
    "IEEE, 2024: 798-804."
)

# ==================== 开题报告 - 进度安排 ====================
SCHEDULE_REPORT = (
    "2025年11月1日～2025年11月30日：查阅文献资料，进行课题调研，明确研究目标与内容；\n"
    "2025年12月1日～2025年12月31日：完成需求分析，撰写开题报告，完成开题答辩，"
    "确定系统总体设计方案；\n"
    "2026年1月1日～2026年2月28日：实现滤波、增强、边缘检测等核心算法模块；\n"
    "2026年3月1日～2026年3月31日：实现形态学、分割、变换算法及交互式界面开发；\n"
    "2026年4月1日～2026年4月30日：系统集成、功能测试与性能优化；\n"
    "2026年5月1日～2026年6月10日：撰写毕业论文，完成论文修改、定稿与答辩准备。"
)


# ==================== 填写函数 ====================
def set_font(rng, name_cn="宋体", name_en="Times New Roman", size=12):
    """设置字体格式"""
    rng.Font.Name = name_en          # 西文字体
    rng.Font.NameFarEast = name_cn   # 中文字体
    rng.Font.Size = size
    rng.ParagraphFormat.LineSpacingRule = 1  # wdLineSpace1pt5 = 1


def replace_placeholder(doc, content):
    """替换 ×××× 占位符为实际内容"""
    rng = doc.Content
    find = rng.Find
    find.ClearFormatting()
    find.Replacement.ClearFormatting()
    # 查找并替换占位符（包括其中的提示文字）
    find.Text = "×××××××××（小四号宋体，1.5倍行距，西文字符使用Times New Roman字体）×××××××××××××××××××××"
    find.Replacement.Text = ""
    find.Execute(Replace=2)  # wdReplaceAll = 2

    # 在占位符位置插入内容
    # 由于上面已经删除占位符，现在查找该段落并插入
    rng = doc.Content
    find = rng.Find
    find.ClearFormatting()
    find.Text = ""  # 重新定位
    # 直接使用 Find 定位到目标段落标题后的空内容比较复杂，改用表格方式


def fill_cover(doc, title, name, major, grade, sid, advisor):
    """填写封面字段"""
    fields = {
        "目：": title,
        "名：": name,
        "业：": major,
        "级：": grade,
        "号：": sid,
        "师：": advisor,
    }
    for keyword, value in fields.items():
        rng = doc.Content
        find = rng.Find
        find.ClearFormatting()
        find.Text = keyword
        if find.Execute():
            # 找到关键词，在其后插入值
            end_pos = rng.End
            insert_rng = doc.Range(end_pos, end_pos)
            insert_rng.Text = value
            set_font(insert_rng)
            # 设置下划线（封面字段通常带下划线）
            insert_rng.Font.Underline = 1


def fill_task_schedule(doc):
    """填写任务书的进度安排表格"""
    # 表格2是进度安排表
    if doc.Tables.Count < 2:
        return
    tbl = doc.Tables(2)

    # 任务行映射：R4-R7 对应 2025 年前4条，R9-R13 对应 2026 年后5条
    # 先填年份
    # R3 = 2025, R8 = 2026
    tbl.Cell(3, 1).Range.Text = "2025"
    tbl.Cell(8, 1).Range.Text = "2026"

    # 日期行：R4-R7（2025），R9-R13（2026）
    date_rows = [4, 5, 6, 7, 9, 10, 11, 12, 13]
    for i, (year, date_range, task) in enumerate(SCHEDULE_TASK):
        if i >= len(date_rows):
            break
        row = date_rows[i]
        # 日期单元格
        tbl.Cell(row, 1).Range.Text = date_range
        # 任务内容单元格
        tbl.Cell(row, 2).Range.Text = task


def fill_report_schedule(doc):
    """填写开题报告的进度安排（单单元格）"""
    # 表格1 R4 是课题进度安排
    tbl = doc.Tables(1)
    cell = tbl.Cell(4, 1)
    # 保留标题"课题进度安排:"，在其后插入内容
    cell.Range.InsertAfter("\n" + SCHEDULE_REPORT)


def fill_task_doc(word):
    """填写任务书"""
    src = os.path.abspath("1.毕业论文（设计）任务书.doc")
    dst = os.path.abspath("1.毕业论文（设计）任务书_已填写.docx")

    doc = word.Documents.Open(src)
    # 1. 封面
    fill_cover(doc, TITLE, NAME, MAJOR, GRADE, STUDENT_ID, ADVISOR)

    # 2. 本课题目标（表格1 R1）
    tbl1 = doc.Tables(1)
    cell = tbl1.Cell(1, 1)
    cell.Range.Text = "本课题目标:\n" + OBJECTIVES
    set_font(cell.Range, "宋体", "Times New Roman", 12)

    # 3. 本课题的任务和要求（表格1 R2）
    cell = tbl1.Cell(2, 1)
    cell.Range.Text = "本课题的任务和要求:\n" + TASKS
    set_font(cell.Range, "宋体", "Times New Roman", 12)

    # 4. 进度安排表格
    fill_task_schedule(doc)

    # 保存
    doc.SaveAs2(dst, FileFormat=16)  # wdFormatDocumentDefault = 16 (.docx)
    doc.Close(False)
    print(f"[OK] 已生成: {dst}")


def fill_report_doc(word):
    """填写开题报告"""
    src = os.path.abspath("2.开题报告.doc")
    dst = os.path.abspath("2.开题报告_已填写.docx")

    doc = word.Documents.Open(src)
    # 1. 封面
    fill_cover(doc, TITLE, NAME, MAJOR, GRADE, STUDENT_ID, ADVISOR)

    tbl = doc.Tables(1)

    # 2. 研究目的和意义（R1）
    cell = tbl.Cell(1, 1)
    cell.Range.Text = "研究目的和意义:\n" + PURPOSE
    set_font(cell.Range, "宋体", "Times New Roman", 12)

    # 3. 课题研究现状（R2）
    cell = tbl.Cell(2, 1)
    cell.Range.Text = "课题研究现状:\n" + CURRENT_STATUS
    set_font(cell.Range, "宋体", "Times New Roman", 12)

    # 4. 主要内容、实施方案及创新点（R3）
    cell = tbl.Cell(3, 1)
    cell.Range.Text = "课题研究主要内容、实施方案及创新点:\n" + MAIN_CONTENT
    set_font(cell.Range, "宋体", "Times New Roman", 12)

    # 5. 进度安排（R4）
    cell = tbl.Cell(4, 1)
    cell.Range.Text = "课题进度安排:\n" + SCHEDULE_REPORT
    set_font(cell.Range, "宋体", "Times New Roman", 12)

    # 6. 主要参考文献（R5）
    cell = tbl.Cell(5, 1)
    cell.Range.Text = "主要参考文献:\n" + REFERENCES
    set_font(cell.Range, "宋体", "Times New Roman", 12)

    # 保存
    doc.SaveAs2(dst, FileFormat=16)
    doc.Close(False)
    print(f"[OK] 已生成: {dst}")


if __name__ == "__main__":
    print("开始填写文档...")
    word = win32com.client.Dispatch("Word.Application")
    word.Visible = False
    try:
        fill_task_doc(word)
        fill_report_doc(word)
    finally:
        word.Quit()
    print("完成！")
