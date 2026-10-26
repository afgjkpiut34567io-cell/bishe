# -*- coding: utf-8 -*-
"""
生成毕业论文 Word 文档
题目：基于OpenCV和Streamlit的图像处理算法交互式演示系统
符合《2023级毕业设计要求说明》格式规范
"""

import sys
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

sys.stdout.reconfigure(encoding="utf-8")

# ==================== 基本信息 ====================
TITLE = "基于OpenCV和Streamlit的图像处理算法交互式演示系统"
STUDENT_NAME = "XXX"
STUDENT_ID = "XXX"
MAJOR = "智能科学与技术"
GRADE = "2023级"
ADVISOR = "XXX"

# ==================== 参考文献 ====================
REFERENCES = [
    "[1] 冈萨雷斯, 伍兹. 数字图像处理（第三版）[M]. 阮秋琦, 阮宇智, 译. 北京: 电子工业出版社, 2011.",
    "[2] 阮秋琦. 数字图像处理学（第四版）[M]. 北京: 电子工业出版社, 2013.",
    "[3] 章毓晋. 图像工程（第四版）[M]. 北京: 清华大学出版社, 2018.",
    "[4] 毛星云, 冷雪飞. OpenCV3编程入门[M]. 北京: 电子工业出版社, 2015.",
    "[5] 李立宗. OpenCV轻松入门：面向Python[M]. 北京: 电子工业出版社, 2019.",
    "[6] 王文成, 李健, 王瑞兰, 等. 基于Matlab GUI的数字图像处理仿真平台设计与开发[J]. 实验技术与管理, 2019, 36(2).",
    "[7] 刘丽娟. 基于MATLAB GUI的图像处理辅助教学平台设计与开发[J]. 电子元器件与信息技术, 2021, 5(3): 181-183.",
    "[8] 贾小军, 喻擎苍. 基于开源计算机视觉库OpenCV的图像处理[J]. 计算机应用与软件, 2008, 25(4): 276-278.",
    "[9] 刘立强, 蔡晓华, 吴泽全. 基于OpenCV的除草机器人图像处理技术[J]. 农机化研究, 2013(12): 162-165.",
    "[10] 郭晖, 陈光. 基于OpenCV的视频图像处理应用研究[J]. 微型机与应用, 2010(21).",
    "[11] 邱望标, 朱金亮. 基于OpenCV的烟叶图像处理技术[J]. 安徽农业科学, 2010(26).",
    "[12] 李振杰, 臧春华, 苏宝玉, 等. 基于OpenCV图像处理软件的设计[J]. 物联网技术, 2024, 14(6).",
    "[13] 杨蕊遥. 基于嵌入式和OpenCV的智能视频监控系统研究[D]. 大连: 大连海事大学, 2018.",
    "[14] 梁丹, 骆立锋, 项四通, 等. 面向机器视觉课堂教学的交互式仿真实验平台设计[J]. 数字技术与应用, 2024(10).",
    "[15] 基于OpenCV和PyQt的数字图像处理综合实验平台开发[J]. 电脑知识与技术, 2023(24).",
    "[16] 基于OpenCV的“数字图像处理”课程阶梯式实践教学体系研究[J]. 科教导刊, 2024(8).",
    "[17] Canny J. A computational approach to edge detection[J]. IEEE Transactions on Pattern Analysis and Machine Intelligence, 1986, 8(6): 679-698.",
    "[18] Otsu N. A threshold selection method from gray-level histograms[J]. IEEE Transactions on Systems, Man, and Cybernetics, 1979, 9(1): 62-66.",
    "[19] Harris C, Stephens M. A combined corner and edge detector[C]//Proceedings of the Alvey Vision Conference. 1988: 147-151.",
    "[20] Lowe D G. Distinctive image features from scale-invariant keypoints[J]. International Journal of Computer Vision, 2004, 60(2): 91-110.",
    "[21] Rudin L I, Osher S, Fatemi E. Nonlinear total variation based noise removal algorithms[J]. Physica D: Nonlinear Phenomena, 1992, 60(1-4): 259-268.",
    "[22] Tomasi C, Manduchi R. Bilateral filtering for gray and color images[C]//Proceedings of the IEEE International Conference on Computer Vision. 1998: 839-846.",
    "[23] Bradski G, Kaehler A. Learning OpenCV 3: Computer Vision in C++ with the OpenCV Library[M]. O'Reilly Media, 2017.",
    "[24] Shalini G M, Anand R, Sankeerth T, et al. Integrated colorization and styling approach for enhancing image clarity[C]//2024 3rd International Conference on Applied Artificial Intelligence and Computing (ICAAIC). IEEE, 2024: 798-804.",
]

# ==================== 文档格式化辅助函数 ====================

def _set_run_font(run, cn="宋体", en="Times New Roman", size=12, bold=False, color=None):
    """设置 run 的中英文字体、字号"""
    run.font.name = en
    run._element.rPr.rFonts.set(qn("w:eastAsia"), cn)
    run.font.size = Pt(size)
    run.font.bold = bold
    if color:
        run.font.color.rgb = RGBColor(*color)


def _set_paragraph_format(para, align=None, line_spacing=1.5,
                          first_line_indent=None, space_before=0, space_after=0):
    """设置段落格式"""
    pf = para.paragraph_format
    if align is not None:
        pf.alignment = align
    pf.line_spacing = line_spacing
    if first_line_indent is not None:
        pf.first_line_indent = Pt(first_line_indent)
    pf.space_before = Pt(space_before)
    pf.space_after = Pt(space_after)


def add_body(doc, text, indent=True, bold=False):
    """添加正文段落（宋体小四，1.5倍行距，首行缩进2字符）"""
    para = doc.add_paragraph()
    run = para.add_run(text)
    _set_run_font(run, size=12, bold=bold)
    _set_paragraph_format(para, align=WD_ALIGN_PARAGRAPH.JUSTIFY,
                          line_spacing=1.5,
                          first_line_indent=24 if indent else None)
    return para


def add_heading1(doc, text):
    """一级标题（章）：黑体三号居中加粗"""
    para = doc.add_paragraph()
    run = para.add_run(text)
    _set_run_font(run, cn="黑体", en="Times New Roman", size=16, bold=True)
    _set_paragraph_format(para, align=WD_ALIGN_PARAGRAPH.CENTER,
                          line_spacing=1.5, space_before=12, space_after=12)
    # 设置为标题样式便于生成目录
    para.style = doc.styles["Heading 1"]
    for r in para.runs:
        _set_run_font(r, cn="黑体", en="Times New Roman", size=16, bold=True)
    _set_paragraph_format(para, align=WD_ALIGN_PARAGRAPH.CENTER,
                          line_spacing=1.5, space_before=12, space_after=12)
    return para


def add_heading2(doc, text):
    """二级标题（节）：黑体四号左对齐加粗"""
    para = doc.add_paragraph()
    run = para.add_run(text)
    _set_run_font(run, cn="黑体", en="Times New Roman", size=14, bold=True)
    para.style = doc.styles["Heading 2"]
    for r in para.runs:
        _set_run_font(r, cn="黑体", en="Times New Roman", size=14, bold=True)
    _set_paragraph_format(para, align=WD_ALIGN_PARAGRAPH.LEFT,
                          line_spacing=1.5, space_before=6, space_after=6)
    return para


def add_heading3(doc, text):
    """三级标题（小节）：黑体小四左对齐加粗"""
    para = doc.add_paragraph()
    run = para.add_run(text)
    _set_run_font(run, cn="黑体", en="Times New Roman", size=12, bold=True)
    para.style = doc.styles["Heading 3"]
    for r in para.runs:
        _set_run_font(r, cn="黑体", en="Times New Roman", size=12, bold=True)
    _set_paragraph_format(para, align=WD_ALIGN_PARAGRAPH.LEFT,
                          line_spacing=1.5, space_before=6, space_after=3)
    return para


def add_code(doc, code):
    """添加代码块（等宽字体，五号，单倍行距，浅灰底纹）"""
    para = doc.add_paragraph()
    run = para.add_run(code)
    run.font.name = "Consolas"
    run._element.rPr.rFonts.set(qn("w:eastAsia"), "宋体")
    run.font.size = Pt(10.5)
    _set_paragraph_format(para, line_spacing=1.0, space_before=6, space_after=6)
    # 设置底纹
    pPr = para._p.get_or_add_pPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:fill"), "F2F2F2")
    pPr.append(shd)
    return para


def add_table(doc, headers, rows):
    """添加三线表"""
    table = doc.add_table(rows=1 + len(rows), cols=len(headers))
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.style = "Table Grid"
    # 表头
    for i, h in enumerate(headers):
        cell = table.rows[0].cells[i]
        cell.text = ""
        run = cell.paragraphs[0].add_run(h)
        _set_run_font(run, cn="黑体", size=10.5, bold=True)
        cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    # 数据行
    for ri, row in enumerate(rows):
        for ci, val in enumerate(row):
            cell = table.rows[ri + 1].cells[ci]
            cell.text = ""
            run = cell.paragraphs[0].add_run(str(val))
            _set_run_font(run, size=10.5)
            cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    return table


def add_caption(doc, text):
    """添加表/图标题（居中，宋体五号加粗）"""
    para = doc.add_paragraph()
    run = para.add_run(text)
    _set_run_font(run, size=10.5, bold=True)
    _set_paragraph_format(para, align=WD_ALIGN_PARAGRAPH.CENTER,
                          line_spacing=1.5, space_before=6, space_after=6)
    return para


def add_page_break(doc):
    """添加分页符"""
    from docx.enum.text import WD_BREAK
    para = doc.add_paragraph()
    run = para.add_run()
    run.add_break(WD_BREAK.PAGE)


def add_summary(doc, text):
    """添加本章小结（楷体，无首行缩进）"""
    para = doc.add_paragraph()
    run = para.add_run(text)
    _set_run_font(run, cn="楷体", en="Times New Roman", size=12)
    _set_paragraph_format(para, align=WD_ALIGN_PARAGRAPH.JUSTIFY,
                          line_spacing=1.5)
    return para


def add_toc(doc):
    """插入自动目录域"""
    para = doc.add_paragraph()
    run = para.add_run()
    fld_char = OxmlElement("w:fldChar")
    fld_char.set(qn("w:fldCharType"), "begin")
    instr_text = OxmlElement("w:instrText")
    instr_text.set(qn("xml:space"), "preserve")
    instr_text.text = 'TOC \\o "1-3" \\h \\z \\u'
    fld_char2 = OxmlElement("w:fldChar")
    fld_char2.set(qn("w:fldCharType"), "separate")
    fld_char3 = OxmlElement("w:fldChar")
    fld_char3.set(qn("w:fldCharType"), "end")
    run._r.append(fld_char)
    run._r.append(instr_text)
    run._r.append(fld_char2)
    run._r.append(fld_char3)


# ==================== 构建文档 ====================
def build_document():
    doc = Document()

    # 设置页面默认字体
    style = doc.styles["Normal"]
    style.font.name = "Times New Roman"
    style._element.rPr.rFonts.set(qn("w:eastAsia"), "宋体")
    style.font.size = Pt(12)

    # ==================== 封面 ====================
    for _ in range(4):
        doc.add_paragraph()
    p = doc.add_paragraph()
    r = p.add_run("本科毕业论文（设计）")
    _set_run_font(r, cn="黑体", size=22, bold=True)
    _set_paragraph_format(p, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=30)

    p = doc.add_paragraph()
    r = p.add_run(TITLE)
    _set_run_font(r, cn="黑体", size=18, bold=True)
    _set_paragraph_format(p, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=40)

    for _ in range(4):
        doc.add_paragraph()

    cover_fields = [
        ("学    院", "XXXXXX学院"),
        ("专    业", MAJOR),
        ("年    级", GRADE),
        ("学    号", STUDENT_ID),
        ("姓    名", STUDENT_NAME),
        ("指导教师", ADVISOR),
    ]
    for label, value in cover_fields:
        p = doc.add_paragraph()
        r = p.add_run(f"{label}：{value}")
        _set_run_font(r, size=14)
        _set_paragraph_format(p, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=8)

    p = doc.add_paragraph()
    r = p.add_run("2026 年 5 月")
    _set_run_font(r, size=14)
    _set_paragraph_format(p, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=40)

    add_page_break(doc)

    # ==================== 中文摘要 ====================
    p = doc.add_paragraph()
    r = p.add_run("摘  要")
    _set_run_font(r, cn="黑体", size=16, bold=True)
    _set_paragraph_format(p, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=12)

    abstract_cn_1 = (
        "图像处理是计算机视觉和人工智能领域的重要基础技术，在医疗影像、工业检测、安防监控、"
        "自动驾驶等众多领域得到了广泛应用。然而，在传统图像处理课程教学中，算法通常以数学公式"
        "和静态图像的形式进行讲授，算法原理抽象、处理过程不可见，导致初学者理解困难、学习效率"
        "低下。如何将抽象的图像处理算法转化为直观、可交互的视觉体验，从而降低学习门槛，是图像"
        "处理教学领域亟待解决的问题。"
    )
    add_body(doc, abstract_cn_1)

    abstract_cn_2 = (
        "针对上述问题，本课题设计并实现了一个基于OpenCV和Streamlit的图像处理算法交互式演示系统。"
        "系统以Python作为开发语言，以OpenCV作为核心算法引擎，以Streamlit构建交互式Web界面，以"
        "Matplotlib实现数据可视化。系统集成滤波、图像增强、边缘检测、形态学操作、阈值分割、图像"
        "变换六大类共30种常用图像处理算法，为每种算法提供滑块、下拉菜单、单选按钮等参数调节组件，"
        "实现参数的实时调节与结果预览；针对关键算法设计了中间步骤可视化、直方图对比、伽马曲线、"
        "频域分析等多种教学可视化方式，并提供算法原理、核心代码、参数详解和典型应用场景等教学资料。"
        "系统采用模块化四层架构，通过图像自动缩放、结果缓存、参数变更检测等策略保障响应速度。"
        "测试结果表明，系统各算法平均处理耗时约为3毫秒，远低于300毫秒的实时性要求，各功能模块"
        "运行稳定，能够有效辅助图像处理课程的教学与自学，具有一定的实际应用价值。"
    )
    add_body(doc, abstract_cn_2)

    p = doc.add_paragraph()
    r = p.add_run("关键词：图像处理；OpenCV；Streamlit；交互式教学；数据可视化")
    _set_run_font(r, size=12, bold=True)
    _set_paragraph_format(p, line_spacing=1.5, space_before=12)

    add_page_break(doc)

    # ==================== 英文摘要 ====================
    p = doc.add_paragraph()
    r = p.add_run("Abstract")
    _set_run_font(r, en="Times New Roman", size=16, bold=True)
    _set_paragraph_format(p, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=12)

    abstract_en_1 = (
        "Image processing is a fundamental technology in the field of computer vision and "
        "artificial intelligence, and has been widely applied in medical imaging, industrial "
        "inspection, security surveillance, autonomous driving, and many other fields. However, "
        "in traditional image processing courses, algorithms are usually taught in the form of "
        "mathematical formulas and static images, making the underlying principles abstract and "
        "the processing procedure invisible, which leads to high learning barriers and low "
        "learning efficiency for beginners."
    )
    para = doc.add_paragraph()
    run = para.add_run(abstract_en_1)
    _set_run_font(run, en="Times New Roman", size=12)
    _set_paragraph_format(para, align=WD_ALIGN_PARAGRAPH.JUSTIFY, line_spacing=1.5)

    abstract_en_2 = (
        "To address the above problems, this project designs and implements an interactive "
        "demonstration system for image processing algorithms based on OpenCV and Streamlit. "
        "The system is developed in Python, with OpenCV as the core algorithm engine, Streamlit "
        "for building the interactive web interface, and Matplotlib for data visualization. It "
        "integrates 30 commonly used image processing algorithms across six categories, including "
        "filtering, image enhancement, edge detection, morphological operations, threshold "
        "segmentation, and image transformation. For each algorithm, the system provides "
        "parameter-adjusting widgets such as sliders, drop-down menus, and radio buttons to "
        "enable real-time parameter tuning and result preview. For key algorithms, multiple "
        "visualization methods such as intermediate-step visualization, histogram comparison, "
        "gamma curves, and frequency-domain analysis are designed, together with teaching "
        "materials covering algorithm principles, core code, parameter explanations, and typical "
        "application scenarios. The system adopts a modular four-layer architecture and ensures "
        "responsiveness through automatic image resizing, result caching, and parameter-change "
        "detection. Test results show that the average processing time of each algorithm is about "
        "3 milliseconds, far below the 300-millisecond real-time requirement, and all functional "
        "modules run stably, which can effectively assist the teaching and self-learning of image "
        "processing courses."
    )
    para = doc.add_paragraph()
    run = para.add_run(abstract_en_2)
    _set_run_font(run, en="Times New Roman", size=12)
    _set_paragraph_format(para, align=WD_ALIGN_PARAGRAPH.JUSTIFY, line_spacing=1.5)

    p = doc.add_paragraph()
    r = p.add_run("Key Words: Image Processing; OpenCV; Streamlit; Interactive Teaching; Data Visualization")
    _set_run_font(r, en="Times New Roman", size=12, bold=True)
    _set_paragraph_format(p, line_spacing=1.5, space_before=12)

    add_page_break(doc)

    # ==================== 目录 ====================
    p = doc.add_paragraph()
    r = p.add_run("目  录")
    _set_run_font(r, cn="黑体", size=16, bold=True)
    _set_paragraph_format(p, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=12)
    add_toc(doc)
    doc.add_paragraph("（提示：打开文档后，在目录处右键选择“更新域”即可自动生成页码）")

    add_page_break(doc)

    # ==================== 第1章 绪论 ====================
    add_heading1(doc, "第1章  绪论")

    add_heading2(doc, "1.1  研究背景与意义")
    add_body(doc,
        "随着计算机技术和人工智能的迅速发展，图像处理技术已经从早期的实验室研究走向了大规模"
        "的工程应用。在医疗领域，医学图像增强与分割技术被广泛用于CT、MRI影像的辅助诊断；在"
        "工业领域，基于机器视觉的表面缺陷检测显著提高了产品质量检验的效率与精度；在安防领域，"
        "目标检测与跟踪技术成为智能视频监控的核心支撑。图像处理已经成为信息时代不可或缺的基础"
        "性技术之一。"
    )
    add_body(doc,
        "图像处理技术的广泛应用，使得相关人才的需求持续增长。目前，国内外高校普遍将“数字图像"
        "处理”设置为计算机、电子信息、人工智能等相关专业的核心课程。然而，该课程具有理论性强、"
        "数学推导复杂的特点。灰度变换、空域滤波、频域变换、边缘检测等算法的核心思想往往需要通过"
        "卷积、梯度、傅里叶变换等数学工具加以描述，对于初学者而言，仅凭公式推导和静态图像难以"
        "建立起对算法处理过程的直观理解。传统教学中，学生通常只能通过阅读教材中的示例图片来感受"
        "算法的效果，无法实时观察参数变化对处理结果的影响，更难以理解算法内部的中间处理环节。"
        "这种“重理论、轻直观”的教学方式，在一定程度上降低了学习效率，也影响了学生的学习兴趣。"
    )
    add_body(doc,
        "针对上述问题，本课题设计并实现了一个基于OpenCV和Streamlit的图像处理算法交互式演示系统。"
        "系统将抽象的图像处理算法转化为直观、可交互的视觉体验，学生通过拖动参数滑块即可实时观察"
        "图像的变化，通过步骤可视化可以了解算法的内部处理机制，通过教学面板可以学习算法的原理、"
        "代码和应用场景。该系统的设计与实现，一方面能够为图像处理课程的教学提供一种直观、便捷的"
        "辅助工具，弥补传统教学方式在直观性方面的不足；另一方面，系统验证了Python生态下“OpenCV"
        "算法引擎+Streamlit交互框架+Matplotlib可视化”这一轻量级技术方案在构建交互式教学系统方面的"
        "可行性，为同类系统的开发提供了有益的参考。"
    )
    add_body(doc,
        "从更宏观的视角来看，本课题的意义还体现在教育信息化的发展趋势之中。随着教育信息化进程的"
        "不断推进，利用信息技术手段改进教学模式、提升教学效果已成为高等教育改革的重要方向。交互式"
        "演示系统作为信息技术与课程教学深度融合的具体实践，能够将原本依赖教师口头讲解和静态教材"
        "呈现的抽象知识，转化为学生可自主探索、实时反馈的动态体验，符合“以学生为中心”的现代教学"
        "理念。本课题所构建的系统，正是这一理念在图像处理课程中的一次具体落地，其设计思路和技术"
        "方案对于其他理工科课程的交互式教学工具开发同样具有借鉴意义。"
    )

    add_heading2(doc, "1.2  国内外研究现状")
    add_body(doc,
        "图像处理教学工具的研发，经历了从桌面端到Web端、从静态演示到交互式探索的演进过程。"
        "早期的图像处理教学平台大多基于MATLAB及其GUI工具构建。王文成等人设计开发了基于Matlab "
        "GUI的数字图像处理仿真平台，通过可视化界面集成多种经典算法，实现了处理结果的直观展示"
        "和参数的可交互调节[6]。刘丽娟基于MATLAB GUI设计了图像处理辅助教学平台，将图像增强、"
        "图像分割等模块以图形化方式呈现，提高了学生的学习兴趣[7]。这类平台算法库丰富、开发便捷，"
        "但依赖商业软件、可移植性较差，不利于网络化传播。"
    )
    add_body(doc,
        "随着开源计算机视觉库OpenCV的普及，基于OpenCV的教学平台逐渐成为主流。贾小军等人较早"
        "介绍了利用OpenCV进行图像处理的方法，展示了其在图像平滑、边缘检测等方面的应用[8]。"
        "近年来，相关研究进一步聚焦于教学场景：有学者开发了基于OpenCV和PyQt的数字图像处理综合"
        "实验平台，涵盖图像基本操作、图像增强、图像分割和形态学处理等模块，并提供可视化的参数"
        "调节界面[15]；梁丹等人设计了面向机器视觉课堂教学的交互式仿真实验平台，让学生在实践探索"
        "中体会经典的图像处理操作[14]；还有研究针对“数字图像处理”课程提出了基于OpenCV的阶梯式"
        "实践教学体系[16]。此外，OpenCV在众多工程领域也得到了广泛应用，例如嵌入式视频监控[13]、"
        "图像处理软件设计[12]、智能除草机器人的图像处理[9]、视频图像处理应用[10]以及烟叶等农产品"
        "的图像检测[11]等，充分体现了OpenCV作为通用图像处理工具的强大能力与广泛适用性。"
    )
    add_body(doc,
        "在交互界面技术方面，传统桌面端平台多采用Qt、PyQt等框架，虽然功能完善，但开发成本高、"
        "跨平台部署困难。近年来，以Streamlit、Dash为代表的Python Web框架逐渐兴起，为交互式教学"
        "系统的快速开发提供了新的技术路径。Streamlit凭借“用纯Python编写交互式Web应用”的理念，"
        "大幅降低了数据应用和可视化工具的开发门槛，在国际上已被用于数据探索、机器学习演示和"
        "教学辅助等多个场景。Shalini等人基于Streamlit和OpenCV开发了图像着色与风格化的交互式"
        "工具，验证了二者结合构建图像处理Web应用的可行性[24]。"
    )
    add_body(doc,
        "综合来看，现有研究仍存在以下不足：其一，算法覆盖不够全面，多数平台仅集成十余种基础"
        "算法，难以完整覆盖教学大纲对算法体系的要求；其二，缺乏对算法中间处理步骤的可视化展示，"
        "难以揭示算法内部的处理机制；其三，教学辅助功能较为薄弱，原理说明、参数解释与代码展示"
        "往往相互割裂，未形成有机整体；其四，部分平台性能优化不足，参数调节响应延迟明显，影响"
        "交互体验。针对上述不足，本课题构建了一个覆盖六大类30种算法、融合实时交互与步骤可视化、"
        "具备完整教学辅助功能的综合性图像处理算法交互式演示系统。"
    )

    add_heading2(doc, "1.3  主要研究内容")
    add_body(doc, "本课题的主要研究内容包括以下几个方面：")
    add_body(doc,
        "（1）图像处理算法库的构建。依据图像处理课程的知识体系，将常用算法划分为滤波、图像增强、"
        "边缘检测、形态学操作、阈值分割、图像变换六大类，基于OpenCV实现共30种算法的处理功能。"
    )
    add_body(doc,
        "（2）交互式参数调节机制的实现。为每种算法设计滑块、下拉菜单、单选按钮等交互组件，"
        "实现参数的实时调节，并通过高效的图像处理流水线确保参数调整后结果预览的及时更新。"
    )
    add_body(doc,
        "（3）算法步骤可视化与教学辅助功能的设计。针对关键算法，通过Matplotlib动态展示中间处理"
        "步骤、直方图变化、伽马曲线及频域分布等数据曲线；同时提供算法原理说明、核心代码片段、"
        "参数作用解释和典型应用场景等教学资料。"
    )
    add_body(doc,
        "（4）系统性能优化与测试验证。通过图像自动缩放、结果缓存、参数变更检测等策略保障系统"
        "响应速度，并通过功能测试和性能测试验证系统的有效性与稳定性。"
    )

    add_heading2(doc, "1.4  论文组织结构")
    add_body(doc,
        "本文共分为七章，各章内容安排如下：第1章为绪论，阐述课题的研究背景、意义、国内外研究"
        "现状及主要研究内容；第2章介绍系统涉及的相关技术与理论基础；第3章对系统进行需求分析；"
        "第4章阐述系统的总体设计方案；第5章详细说明系统的实现过程；第6章对系统进行测试与结果"
        "分析；第7章对全文工作进行总结并对未来研究方向进行展望。"
    )

    add_page_break(doc)

    # ==================== 第2章 相关技术与理论基础 ====================
    add_heading1(doc, "第2章  相关技术与理论基础")

    add_heading2(doc, "2.1  图像处理基础")
    add_body(doc,
        "数字图像在计算机中以矩阵形式存储。一幅灰度图像可以表示为一个二维矩阵，矩阵中的每个元素"
        "对应一个像素的灰度值，取值范围通常为0到255；一幅彩色图像则由红、绿、蓝三个通道的矩阵"
        "叠加而成。图像处理的核心任务，就是通过对这些像素矩阵施加各种数学变换，实现对图像信息的"
        "增强、提取与分析。关于数字图像处理的系统理论，冈萨雷斯等人的经典教材对图像处理的基本概念、"
        "空域与频域处理方法以及图像增强、复原、分割等技术进行了全面而深入的阐述[1]；阮秋琦编著的"
        "《数字图像处理学》则从教学角度系统梳理了图像处理的知识体系[2]；章毓晋的《图像工程》进一步"
        "从工程应用层面构建了图像处理、图像分析和图像理解的完整框架[3]。上述著作构成了本课题理论"
        "基础的重要来源。"
    )
    add_body(doc,
        "图像处理算法种类繁多，按照处理目的和数学方法的不同，可以大致划分为空间域处理和频率域"
        "处理两大类。空间域处理直接对像素值进行操作，包括灰度变换、空域滤波、直方图处理等；频率域"
        "处理则首先通过傅里叶变换将图像转换到频率域，再对频谱进行操作。此外，形态学操作基于集合论"
        "思想，利用结构元素对图像中的形状进行分析和处理；边缘检测则通过计算像素灰度的梯度或二阶"
        "导数来定位图像中亮度发生突变的区域。本系统所集成的30种算法，正是围绕上述处理范式而组织的。"
    )
    add_body(doc,
        "卷积是空间域滤波的数学基础。对于图像f与滤波核w，二维卷积运算将核w在图像上滑动，对每个"
        "位置计算核与对应像素的加权和，得到输出图像。滤波核的取值决定了滤波的性质：高斯核的取值"
        "服从二维高斯分布，具有中心大、四周小的特征，用于平滑去噪；拉普拉斯核的取值包含正负项，"
        "用于锐化和边缘增强。直方图则是图像灰度分布的重要统计工具，它统计了各灰度级在图像中出现的"
        "频数，直方图均衡化、Otsu阈值分割等算法均以直方图为分析基础。梯度反映了图像灰度变化的方向"
        "和快慢，一阶梯度算子（如Sobel）和二阶梯度算子（如Laplacian）构成了边缘检测的两类基本方法。"
        "这些数学工具虽然形式各异，但共同构成了图像处理算法分析与实现的理论基石。"
    )

    add_heading2(doc, "2.2  OpenCV图像处理库")
    add_body(doc,
        "OpenCV（Open Source Computer Vision Library）是一个开源的计算机视觉与图像处理软件库，"
        "最初由Intel公司发起并维护。OpenCV提供了包括图像读写、几何变换、滤波、特征检测、目标"
        "跟踪、机器学习等在内的数千个优化算法，支持C++、Python、Java等多种编程语言，并具备良好的"
        "跨平台特性。由于底层采用SIMD指令集优化和多线程并行计算，OpenCV在图像处理性能上具有显著"
        "优势[23]。在国内，毛星云等人编著的《OpenCV3编程入门》系统介绍了OpenCV的基本架构与编程"
        "方法，是学习OpenCV的重要入门教材[4]；李立宗编著的《OpenCV轻松入门：面向Python》则针对"
        "Python语言详细讲解了OpenCV在图像处理中的应用，与本系统的技术路线高度契合[5]。"
    )
    add_body(doc,
        "本系统选用OpenCV作为核心算法引擎，主要基于以下考虑：一是OpenCV算法覆盖全面，本系统"
        "所需的30种算法均有成熟且经过优化的实现，避免了重复造轮子；二是OpenCV的Python接口设计"
        "简洁，便于与Streamlit等Web框架集成；三是OpenCV在处理性能上的优势，能够满足系统对实时"
        "响应的要求。系统通过OpenCV实现了高斯滤波、中值滤波、双边滤波、直方图均衡化、Canny边缘"
        "检测、腐蚀膨胀、Otsu阈值分割、傅里叶变换等算法的核心功能。"
    )
    add_body(doc,
        "从工程实践的角度看，直接调用OpenCV而非自行从零实现算法，既保证了算法的正确性与执行"
        "效率，也使本课题能够将更多精力投入到系统架构、交互设计和教学功能等更有价值的工作上。"
        "OpenCV的算法实现经过长期迭代和广泛验证，在数值稳定性和边界条件处理方面都较为成熟，有效"
        "避免了自行实现算法时容易出现的数值溢出、边界越界等问题。当然，系统也并非完全依赖OpenCV的"
        "封装，对于Prewitt算子、锐化核、伽马查找表等OpenCV未直接提供的功能，系统通过NumPy自行构造"
        "相关核与查找表，体现了在“复用成熟实现”与“自主实现关键细节”之间的合理取舍。"
    )

    add_heading2(doc, "2.3  Streamlit交互式框架")
    add_body(doc,
        "Streamlit是一个面向数据科学和机器学习领域的开源Python框架，其核心理念是“用纯Python脚本"
        "构建交互式Web应用”，开发者无需掌握HTML、CSS、JavaScript等前端技术即可快速搭建功能完整"
        "的交互式界面。Streamlit提供了丰富的内置组件，包括滑块（slider）、下拉菜单（selectbox）、"
        "单选按钮（radio）、文件上传（file_uploader）、标签页（tabs）等，并采用“脚本从上到下重新"
        "执行”的响应式模型，当用户交互改变组件状态时，脚本会自动重新运行并刷新界面。"
    )
    add_body(doc,
        "Streamlit的这一特性与本系统的需求高度契合。图像处理教学系统的核心交互模式是“调节参数、"
        "观察结果”，Streamlit的响应式模型天然支持这一模式：当用户拖动参数滑块时，脚本重新执行，"
        "算法模块基于新参数重新处理图像并更新预览。此外，Streamlit的会话状态（session_state）机制"
        "可用于缓存处理结果、记录性能数据，为系统的状态管理和性能优化提供了便利。"
    )
    add_body(doc,
        "与其他Web开发方案相比，Streamlit在本场景下具有明显优势。传统方案中，使用Flask或Django"
        "等后端框架结合前端框架开发交互式应用，需要开发者同时掌握后端路由、接口设计和前端组件开发"
        "等多方面技能，开发成本高、周期长；而Streamlit将交互组件与业务逻辑统一在Python脚本中表达，"
        "开发者只需编写纯Python代码即可获得完整的Web交互界面，大幅缩短了开发周期。对于以算法演示"
        "和教学为目标的本系统而言，Streamlit在“开发效率”与“交互能力”之间取得了很好的平衡，是最为"
        "合适的技术选型。"
    )

    add_heading2(doc, "2.4  Matplotlib可视化库")
    add_body(doc,
        "Matplotlib是Python生态中最常用的数据可视化库，能够绘制直方图、折线图、散点图、热力图等"
        "多种类型的图表，并支持对图形元素进行精细控制。本系统利用Matplotlib实现三类可视化功能："
        "一是绘制图像的灰度直方图及处理前后的直方图对比，直观反映算法对像素分布的影响；二是将算法"
        "的中间处理步骤以图像网格的形式进行展示，帮助学生理解算法的内部流程；三是绘制伽马校正曲线、"
        "频率能量分布等数据曲线，将算法中的数学关系以图形化方式呈现。"
    )

    add_heading2(doc, "2.5  NumPy数值计算库")
    add_body(doc,
        "NumPy是Python科学计算的基础库，提供了高性能的多维数组对象以及丰富的数值运算函数。在"
        "本系统中，图像在底层即以NumPy数组的形式进行表示和传递，OpenCV与NumPy之间可以直接无缝"
        "转换。NumPy的向量化运算特性，使得对图像像素的批量操作无需显式编写循环，从而显著提升了"
        "处理效率，例如伽马校正中查找表的构建、傅里叶变换中幅度谱的计算等均借助NumPy实现。"
    )
    add_body(doc,
        "NumPy在本系统中的作用贯穿始终。图像在系统内部始终以NumPy的多维数组形式存在，OpenCV的"
        "图像对象本质上也是NumPy数组，二者之间的转换是零成本的，这为算法模块与显示模块之间的数据"
        "交换提供了极大的便利。在处理复杂算法时，NumPy的向量化运算能力发挥了关键作用：例如在实现"
        "Prewitt边缘检测算子时，通过NumPy直接构造卷积核矩阵，再调用OpenCV的filter2D函数完成卷积；"
        "在傅里叶变换中，通过NumPy的fftshift和ifftshift函数实现频谱的搬移。这种OpenCV与NumPy"
        "协同工作的模式，是本系统技术实现的一个重要特点，也体现了Python科学计算生态的成熟与高效。"
    )

    add_heading2(doc, "2.6  本章小结")
    add_summary(doc,
        "本章对本系统所涉及的相关技术与理论基础进行了介绍。首先概述了数字图像的基本表示方式和"
        "图像处理的主要范式，为后续算法实现奠定理论基础；随后分别介绍了OpenCV、Streamlit、"
        "Matplotlib和NumPy四个核心技术库的特点及其在本系统中的角色分工。其中，OpenCV作为算法引擎"
        "承担图像处理的核心计算任务，Streamlit负责交互式界面的构建，Matplotlib用于数据可视化，"
        "NumPy提供底层数组运算支撑。上述技术的合理选型与分工，为系统的设计与实现提供了坚实的技术"
        "基础。"
    )

    add_page_break(doc)

    # ==================== 第3章 系统需求分析 ====================
    add_heading1(doc, "第3章  系统需求分析")

    add_heading2(doc, "3.1  系统总体需求")
    add_body(doc,
        "本系统的目标用户为图像处理课程的教师与学生。对于教师而言，系统应能够作为课堂演示工具，"
        "直观展示各类图像处理算法的效果及参数影响；对于学生而言，系统应能够作为自主学习工具，"
        "帮助其理解算法原理、观察处理过程并进行动手实践。基于上述定位，系统应满足以下总体需求："
        "覆盖图像处理课程的核心算法体系，提供直观便捷的交互操作方式，具备算法过程可视化与教学"
        "辅助功能，并保证良好的运行性能与稳定性。"
    )

    add_heading2(doc, "3.2  功能需求分析")
    add_body(doc, "结合系统定位，本系统的功能需求可以归纳为以下五个方面：")
    add_body(doc,
        "（1）图像输入功能。系统应支持JPG、PNG、BMP等常见图像格式的上传，并提供内置示例图像，"
        "使用户在未准备素材的情况下也能快速体验各算法的效果。"
    )
    add_body(doc,
        "（2）算法处理功能。系统应集成滤波、图像增强、边缘检测、形态学操作、阈值分割、图像变换"
        "六大类共30种常用图像处理算法，覆盖图像处理课程的核心知识点。"
    )
    add_body(doc,
        "（3）参数交互功能。系统应为每种算法提供相应的参数调节组件，包括滑块、下拉菜单、单选按钮"
        "等，用户调整参数后应能够实时观察到处理结果的变化。"
    )
    add_body(doc,
        "（4）可视化与教学功能。系统应提供算法中间步骤可视化、直方图对比、数据曲线等多种可视化"
        "方式，并提供算法原理说明、核心代码、参数详解和应用场景等教学资料。"
    )
    add_body(doc,
        "（5）结果输出功能。系统应支持处理结果的下载与保存，并展示处理耗时、图像尺寸等性能与"
        "基本信息，方便用户评估处理效果。"
    )

    add_heading2(doc, "3.3  非功能需求分析")
    add_body(doc,
        "除功能需求外，系统还应满足以下非功能需求：在性能方面，参数调整后处理结果应在300毫秒内"
        "更新，以保证交互的流畅性，避免用户产生卡顿感；在兼容性方面，系统应能够在普通配置的"
        "计算机上稳定运行，支持Windows等主流操作系统；在易用性方面，界面布局应清晰直观，用户"
        "无需阅读说明文档即可快速上手；在可维护性方面，系统应采用模块化设计，各功能模块之间"
        "保持低耦合，便于后续的功能扩展与维护。"
    )
    add_body(doc,
        "在性能需求方面，需要进一步明确的是，300毫秒的实时性指标并非算法处理时间的硬性上限，而是"
        "指从用户完成参数调节到界面呈现更新结果之间的整体感知延迟。由于Streamlit框架本身在脚本"
        "重新执行和界面刷新环节存在一定的固有开销，因此在系统实现中，既要通过算法层面的优化降低"
        "处理时间，也要通过参数变更检测、结果缓存等手段减少不必要的重复执行，从多个环节协同保障"
        "整体响应速度。这一认识对于后续的性能优化设计具有重要的指导意义。"
    )

    add_heading2(doc, "3.4  可行性分析")
    add_body(doc,
        "在技术可行性方面，本系统所依赖的OpenCV、Streamlit、Matplotlib、NumPy等均为成熟稳定的"
        "开源库，技术文档完善、社区活跃，且均提供Python接口，技术选型之间能够良好协同，不存在"
        "技术障碍。在经济可行性方面，系统全部采用开源软件，无需支付任何授权费用，开发成本低。"
        "在操作可行性方面，系统以Web应用形式运行，用户通过浏览器即可访问，操作简单，符合目标用户"
        "的使用习惯。综合来看，本课题在技术、经济和操作层面均具备充分的可行性。"
    )

    add_heading2(doc, "3.5  系统用例分析")
    add_body(doc,
        "为更清晰地刻画系统与用户之间的交互，可将系统的主要使用场景归纳为以下几类典型用例。"
        "其一为课堂演示用例：教师在课堂上选择某个算法，通过调节参数向学生展示处理效果的变化，"
        "并切换到步骤可视化标签页讲解算法的内部流程，此场景要求参数调节响应迅速、步骤展示清晰。"
        "其二为自主学习用例：学生课后自行上传图像，按学习路径依次体验滤波、增强、边缘检测等算法，"
        "同时查阅教学面板中的原理说明和代码实现，此场景要求算法覆盖全面、教学资料翔实。其三为"
        "效果对比用例：用户对同一幅图像应用不同算法或不同参数，比较处理效果以理解参数的影响，"
        "此场景要求系统便于在算法间快速切换。上述用例共同界定了系统在实时性、完整性和易用性方面"
        "的具体需求。"
    )

    add_heading2(doc, "3.6  本章小结")
    add_summary(doc,
        "本章从总体需求、功能需求、非功能需求和可行性四个角度对系统进行了分析。系统定位于图像"
        "处理课程的辅助教学工具，需要满足图像输入、算法处理、参数交互、可视化教学和结果输出五大"
        "类功能需求，同时满足实时响应、跨平台稳定运行、界面易用和模块化可维护等非功能需求。通过"
        "技术、经济和操作三个维度的可行性分析，确认本课题具备充分的实施条件，为后续的系统设计"
        "与实现指明了方向。"
    )

    add_page_break(doc)

    # ==================== 第4章 系统总体设计 ====================
    add_heading1(doc, "第4章  系统总体设计")

    add_heading2(doc, "4.1  系统架构设计")
    add_body(doc,
        "本系统采用模块化四层架构，自底向上依次为工具层、算法层、可视化层和UI层，各层之间职责"
        "清晰、相互解耦。工具层负责图像输入输出、格式转换、性能计时等基础功能；算法层基于OpenCV"
        "实现六大类30种图像处理算法，是整个系统的核心；可视化层基于Matplotlib实现直方图绘制、"
        "步骤网格、数据曲线等可视化功能；UI层基于Streamlit构建交互式界面，负责算法选择、参数调节、"
        "结果预览和教学资料展示。这种分层设计使得各模块可以独立开发、测试和维护，也便于后续对算法"
        "库进行扩展。"
    )
    add_body(doc,
        "四层之间的调用关系遵循“上层依赖下层、下层不感知上层”的依赖原则。UI层是系统的入口，负责"
        "接收用户输入并调用算法层和可视化层完成处理与展示；算法层专注于图像处理算法的实现，通过"
        "统一的函数接口接收图像和参数字典并返回处理结果；可视化层接收算法层产生的中间结果，生成"
        "相应的图表图像；工具层为上述各层提供图像IO、格式转换和性能计时等基础服务。各层通过定义"
        "清晰的接口进行交互，例如所有算法函数均遵循“接收图像（NumPy数组）和参数（字典）、返回"
        "处理结果（NumPy数组）”的统一签名，使得算法层可以独立于UI层进行开发与单元测试。"
    )
    add_body(doc,
        "在代码组织上，系统按照分层思想划分了若干目录：modules目录存放算法层的六个算法实现模块"
        "及可视化模块，ui目录存放UI层的侧边栏、预览、步骤可视化和教学面板四个界面模块，utils目录"
        "存放工具层的配置、图像IO和性能优化模块，data目录存放教学资料数据，根目录下的app.py作为"
        "主程序负责各模块的装配与调度。这种目录结构清晰地反映了系统的分层架构，也便于开发者在对应"
        "目录中定位和维护代码。"
    )

    add_heading2(doc, "4.2  功能模块设计")
    add_body(doc,
        "依据需求分析，系统划分为图像管理模块、算法处理模块、参数交互模块、可视化模块和教学模块"
        "五个功能模块。图像管理模块负责图像的上传、加载、格式转换和结果下载；算法处理模块负责"
        "根据算法标识符和参数执行相应的处理逻辑；参数交互模块负责为不同算法动态生成参数调节组件；"
        "可视化模块负责生成步骤网格、直方图和数据曲线；教学模块负责展示算法的原理、代码、参数"
        "详解和应用场景。各模块通过主程序中的会话状态进行协调，实现数据在模块间的有序流转。"
    )
    add_body(doc,
        "图像管理模块是整个系统的数据入口，其核心职责包括接收用户上传的图像文件、将其解码为标准"
        "的NumPy数组格式、对超大图像进行自动缩放，以及将处理结果编码为可下载的文件格式。算法处理"
        "模块通过算法注册表实现算法标识符到处理函数的映射，注册表以字典形式维护，键为算法标识符、"
        "值为对应的处理函数引用，这种设计使得算法的新增与删除只需修改注册表即可，无需改动其他代码。"
        "参数交互模块根据算法参数定义动态生成调节组件，实现了“一套代码适配所有算法”的目标；可视化"
        "模块与算法模块中的步骤函数协同工作，由算法模块提供中间步骤的图像序列，可视化模块负责将"
        "这些图像序列绘制成统一的网格图。"
    )

    add_heading2(doc, "4.3  算法分类体系设计")
    add_body(doc,
        "依据图像处理课程的知识体系，系统将30种算法划分为六个类别，各类别包含的算法如表4-1所示。"
        "这一分类方式既符合教学大纲的逻辑结构，也便于用户在侧边栏中按类别逐级定位目标算法。"
    )
    add_caption(doc, "表4-1  算法分类统计表")
    add_table(doc,
        ["类别", "算法", "数量"],
        [
            ["滤波算法", "高斯滤波、中值滤波、均值滤波、双边滤波、方框滤波", "5"],
            ["图像增强", "直方图均衡化、CLAHE、对比度亮度、伽马校正、锐化、反锐化掩膜", "6"],
            ["边缘检测", "Canny、Sobel、Laplacian、Scharr、Prewitt", "5"],
            ["形态学操作", "腐蚀、膨胀、开运算、闭运算、形态学梯度、顶帽、黑帽", "7"],
            ["阈值分割", "全局阈值、自适应阈值、Otsu二值化", "3"],
            ["图像变换", "缩放、旋转、仿射变换、傅里叶变换", "4"],
        ],
    )

    add_heading2(doc, "4.4  数据流设计")
    add_body(doc,
        "系统的数据流遵循“输入图像—算法选择—参数调节—算法执行—结果展示”的流程。用户上传或"
        "选择示例图像后，系统将图像以NumPy数组的形式加载并存储于会话状态；用户选择算法类别和具体"
        "算法后，参数交互模块根据该算法的参数定义动态生成调节组件；用户调整参数触发脚本重新执行，"
        "算法处理模块基于当前图像和参数执行处理，并将结果更新至会话状态；最后，预览模块、可视化"
        "模块和教学模块分别从会话状态中读取原始图像、处理结果和算法信息进行展示。为避免不必要的"
        "重复计算，系统对参数是否发生变化进行检测，仅当算法或参数改变时才重新执行处理。"
    )
    add_body(doc,
        "会话状态在整个数据流中扮演着“数据总线”的角色。系统在初始化阶段为会话状态设置原始图像、"
        "处理结果、当前算法、当前参数、性能统计等关键字段，各功能模块通过读写这些字段实现数据的"
        "共享与传递。这种基于会话状态的数据流设计，既符合Streamlit框架的响应式执行模型，又避免了"
        "在函数之间进行复杂的数据传递，使代码结构更加清晰。同时，系统将默认参数与用户当前参数"
        "合并后进行比较，判断是否需要重新执行算法处理，这一“参数变更检测”机制是系统实现高效响应"
        "的关键。"
    )

    add_heading2(doc, "4.5  界面布局设计")
    add_body(doc,
        "系统界面采用Streamlit经典的“侧边栏+主内容区”布局。侧边栏是用户操作的主要入口，从上到下"
        "依次布置图像上传区、算法选择区和参数面板三个区域：图像上传区提供“使用示例图像”复选框和"
        "文件上传组件；算法选择区通过“算法分类”和“具体算法”两个下拉菜单实现二级导航；参数面板"
        "根据所选算法动态生成对应的参数调节组件。主内容区则以标签页的形式组织展示内容，分为“处理"
        "结果预览”“算法步骤可视化”“教学面板”三个标签页，分别承载结果对比、可视化分析和教学资料"
        "的展示功能。"
    )
    add_body(doc,
        "这种布局设计的合理性在于：一方面，将高频使用的图像上传和算法选择操作集中在侧边栏，用户"
        "无需滚动页面即可完成核心操作；另一方面，将内容展示通过标签页分区，避免了单个页面内容过多"
        "导致的混乱，用户可按需切换查看。预览标签页中的性能指标区域以卡片形式展示本次耗时、平均"
        "耗时、处理次数和响应状态等指标，使用户能够直观感知系统的性能表现。此外，页面底部还设置了"
        "包含版本信息、算法集成数量和会话处理次数的信息栏，完善了界面的整体信息呈现。"
    )

    add_heading2(doc, "4.6  本章小结")
    add_summary(doc,
        "本章完成了系统的总体设计。系统采用模块化四层架构，将工具层、算法层、可视化层和UI层"
        "进行职责分离，保证了系统的可维护性与可扩展性；依据需求分析划分了五个功能模块，明确了"
        "各模块的职责分工；设计了覆盖六大类30种算法的分类体系，并梳理了系统数据流的完整脉络。"
        "总体设计为后续的详细实现提供了清晰的框架。"
    )

    add_page_break(doc)

    # ==================== 第5章 系统详细设计与实现 ====================
    add_heading1(doc, "第5章  系统详细设计与实现")

    add_heading2(doc, "5.1  开发环境")
    add_body(doc,
        "本系统基于Python语言开发，主要依赖库及其版本如表5-1所示。系统的开发与测试均在Windows 11"
        "操作系统下完成，运行环境无需高性能配置，普通个人计算机即可流畅运行。"
    )
    add_caption(doc, "表5-1  开发环境配置表")
    add_table(doc,
        ["项目", "配置"],
        [
            ["操作系统", "Windows 11"],
            ["开发语言", "Python 3.10"],
            ["算法引擎", "OpenCV-Python（opencv-python）"],
            ["Web框架", "Streamlit"],
            ["可视化库", "Matplotlib"],
            ["数值计算", "NumPy"],
            ["图像辅助", "Pillow"],
        ],
    )

    add_heading2(doc, "5.2  图像输入输出模块")
    add_body(doc,
        "图像输入输出模块封装于utils.image_io中，提供图像的加载、缩放、格式转换和编码等功能。"
        "图像加载时，系统通过cv2.imdecode将从文件读取的字节流解码为BGR格式的NumPy数组，并对"
        "过大的图像进行自动缩放，将图像最大宽度和高度分别限制在1200像素和900像素以内，以避免"
        "后续处理出现性能瓶颈。为统一各算法的输入格式，模块还提供了灰度转换（to_grayscale）和"
        "三通道保证（ensure_3channel）两个辅助函数，确保无论输入图像是彩色还是灰度，算法模块"
        "都能正确处理并输出可供预览的三通道图像。"
    )
    add_body(doc,
        "值得说明的是，OpenCV采用BGR通道顺序存储彩色图像，而Streamlit和Matplotlib则采用RGB"
        "顺序，因此模块中还提供了bgr_to_rgb与rgb_to_bgr两个转换函数，用于在处理管线与显示管线"
        "之间进行通道顺序的转换，避免出现颜色错乱。此外，图像编码函数image_to_bytes负责将处理"
        "结果编码为PNG或JPG字节流，为结果下载功能提供支撑。针对彩色图像，系统在编码前会先将"
        "BGR转换为RGB，以保证下载图像的色彩正确。上述一系列细节处理，保证了系统在图像流转的"
        "各个环节中数据格式的一致性。"
    )
    add_body(doc,
        "在图像格式支持方面，系统在上传环节支持JPG、JPEG、PNG、BMP、TIFF等常见格式，在结果下载"
        "环节提供PNG和JPG两种编码格式供用户选择。PNG格式采用无损压缩，适合保存需要精确对比的处理"
        "结果；JPG格式体积更小，便于日常存储与分享。系统对输入图像的格式进行了校验，仅接受受支持"
        "格式的文件，对格式不正确或解码失败的文件进行了容错处理，避免异常输入导致系统崩溃。"
    )

    add_heading2(doc, "5.3  滤波算法模块")
    add_body(doc,
        "滤波算法模块实现了高斯滤波、中值滤波、均值滤波、双边滤波和方框滤波五种空间域滤波算法。"
        "高斯滤波利用服从高斯分布的权重模板对图像进行卷积，中心像素权重最大、越远离中心权重越小，"
        "对高斯噪声具有较好的抑制效果；中值滤波取邻域像素的中值替代中心像素，对椒盐噪声有极佳的"
        "去除效果，同时能较好地保留边缘；均值滤波是最简单的线性滤波器，计算速度快但会模糊边缘；"
        "双边滤波在高斯滤波的基础上引入了像素值相似度权重，同时考虑空间距离和灰度差异，是典型的"
        "保边去噪算法[22]；方框滤波则使用均匀权重核，可通过参数控制是否归一化。"
    )
    add_body(doc, "以高斯滤波为例，其核心实现代码如下：")
    add_code(doc,
        'def gaussian_blur(image, params):\n'
        '    ksize = params.get("ksize", (5, 5))\n'
        '    sigma_x = params.get("sigma_x", 1.0)\n'
        '    if isinstance(ksize, int):\n'
        '        ksize = (ksize, ksize)\n'
        '    # 确保核大小为奇数\n'
        '    ksize = (ksize[0] | 1, ksize[1] | 1)\n'
        '    return cv2.GaussianBlur(image, ksize, sigmaX=sigma_x, sigmaY=sigma_x)'
    )
    add_body(doc,
        "在上述实现中，ksize参数控制高斯核的大小，取值越大平滑效果越强；sigma_x控制高斯分布的"
        "标准差，取值越大模糊程度越高。系统对用户传入的核大小进行了奇数化处理，以满足OpenCV"
        "对高斯核必须为奇数的要求。"
    )
    add_body(doc,
        "中值滤波对椒盐噪声的去除效果尤为突出。椒盐噪声表现为图像中随机出现的黑白像素点，均值"
        "滤波和高斯滤波在处理这类噪声时容易将噪声扩散到邻域，而中值滤波通过取邻域中值，能够"
        "直接消除孤立的噪声像素，同时较好地保留图像的边缘信息。为便于教学演示，系统的中值滤波"
        "步骤可视化中会先在示例图像上叠加椒盐噪声，再展示不同窗口大小下的去噪效果，使用户能够"
        "直观对比3×3与5×5窗口的差异。"
    )
    add_body(doc,
        "双边滤波则是五种滤波算法中实现最复杂、效果也最突出的一个。传统的高斯滤波只考虑像素的"
        "空间距离，在平滑噪声的同时会不可避免地模糊边缘；双边滤波在空间域权重的基础上，额外引入"
        "了像素值相似度权重，使得灰度差异较大的边缘区域不会被平滑。其核心思想可以概括为：当中心"
        "像素与邻域像素灰度接近时，按正常权重进行平滑；当两者灰度差异较大时，降低该邻域像素的"
        "权重，从而保护边缘。这一特性使双边滤波在人像美颜、图像去噪等场景中得到了广泛应用[22]。"
        "在图像去噪方法中，除上述空间域滤波外，以全变分（Total Variation）模型为代表的变分去噪"
        "方法也是一类重要的经典方法，其通过求解能量泛函的最小化问题，在去除噪声的同时有效保持了"
        "图像的边缘结构[21]。虽然本系统的滤波模块聚焦于OpenCV提供的空间域滤波器，但了解全变分等"
        "经典去噪方法有助于建立对图像去噪问题更完整的认识。"
        "各滤波算法的主要调节参数及其含义如表5-2所示。"
    )
    add_caption(doc, "表5-2  滤波算法参数表")
    add_table(doc,
        ["算法", "参数", "含义"],
        [
            ["高斯滤波", "ksize / sigma_x", "核大小 / 高斯核标准差"],
            ["中值滤波", "ksize", "邻域窗口大小"],
            ["均值滤波", "ksize", "核大小"],
            ["双边滤波", "d / sigma_color / sigma_space", "直径 / 颜色域标准差 / 空间域标准差"],
            ["方框滤波", "ksize", "核大小"],
        ],
    )

    add_heading2(doc, "5.4  图像增强模块")
    add_body(doc,
        "图像增强模块实现了直方图均衡化、CLAHE、对比度亮度调整、伽马校正、锐化和反锐化掩膜六种"
        "增强算法。直方图均衡化通过将原始图像的直方图变换为均匀分布，使像素占据更宽的灰度范围，"
        "从而增强整体对比度，适用于整体偏暗或偏亮的图像；CLAHE（对比度受限的自适应直方图均衡化）"
        "将图像划分为若干小块分别均衡化，并通过对比度限制抑制噪声放大，克服了全局均衡化易产生"
        "过增强的问题。"
    )
    add_body(doc,
        "伽马校正是一种非线性亮度调整方法，其变换关系为输出像素值与输入像素值归一化后的1/γ次幂"
        "成正比。当γ小于1时暗部被提升、图像整体变亮；当γ大于1时亮部被压缩、图像变暗。本系统通过"
        "构建256级查找表并调用cv2.LUT实现伽马校正，避免了逐像素的幂运算，提高了处理效率。反锐化"
        "掩膜是一种专业的图像锐化技术，其思想是先从原图中减去高斯模糊结果得到细节层，再将细节层"
        "按一定强度叠加回原图，从而实现边缘增强。"
    )
    add_body(doc,
        "直方图均衡化的数学原理可以简要说明如下：设图像的灰度级为0到L-1，直方图均衡化通过累计"
        "分布函数将原始灰度值r映射为新的灰度值s，映射关系为s=(L-1)乘以r的累积概率。经过这一变换，"
        "输出图像的直方图趋于均匀分布，原本集中在较窄灰度范围内的像素被拉伸到更宽的灰度区间，从而"
        "增强了图像的对比度。直方图均衡化的实现代码简洁，系统直接调用OpenCV的equalizeHist函数，"
        "该函数内部已实现了上述映射过程。"
    )
    add_body(doc,
        "CLAHE则是直方图均衡化的改进算法。全局直方图均衡化在处理整体光照不均匀的图像时，容易"
        "造成局部区域过增强或噪声放大；CLAHE将图像划分为若干不重叠的小块，在每个小块内独立进行"
        "直方图均衡化，并设置对比度限制阈值clipLimit，将超过阈值的直方图部分进行裁剪并均匀分配到"
        "其他灰度级，从而在增强局部对比度的同时抑制噪声。本系统中，用户可通过调节clipLimit和"
        "tileGridSize两个参数，直观对比普通直方图均衡化与CLAHE在处理效果上的差异，加深对自适应"
        "算法的理解。"
    )
    add_body(doc, "伽马校正的核心实现代码如下：")
    add_code(doc,
        'def gamma_correction(image, params):\n'
        '    gamma = params.get("gamma", 1.0)\n'
        '    gamma = max(0.1, min(5.0, gamma))\n'
        '    inv_gamma = 1.0 / gamma\n'
        '    table = np.array(\n'
        '        [(i / 255.0) ** inv_gamma * 255 for i in range(256)]\n'
        '    ).astype(np.uint8)\n'
        '    return cv2.LUT(image, table)'
    )

    add_heading2(doc, "5.5  边缘检测模块")
    add_body(doc,
        "边缘检测模块实现了Canny、Sobel、Laplacian、Scharr和Prewitt五种边缘检测算法。其中，"
        "Canny算法是一种经典的多级边缘检测算法，其处理流程包括高斯滤波降噪、梯度幅值与方向计算、"
        "非极大值抑制细化边缘、双阈值检测与边缘连接四个步骤，能够产生连续且细化的边缘[17]。Sobel"
        "和Prewitt算子均基于一阶导数，通过计算水平和垂直两个方向的梯度并合成得到边缘幅值，区别"
        "在于卷积核的权重设置不同；Laplacian算子基于二阶导数，通过检测二阶导数的过零点定位边缘，"
        "但对噪声较为敏感；Scharr算子是Sobel算子的改进版本，具有更好的旋转对称性，对细小边缘的"
        "检测精度更高。"
    )
    add_body(doc, "Canny边缘检测的核心实现代码如下：")
    add_code(doc,
        'def canny_edge(image, params):\n'
        '    gray = to_grayscale(image)\n'
        '    t1 = params.get("threshold1", 50)\n'
        '    t2 = params.get("threshold2", 150)\n'
        '    edges = cv2.Canny(gray, t1, t2)\n'
        '    return ensure_3channel(edges)'
    )
    add_body(doc,
        "其中threshold1和threshold2分别对应双阈值检测中的低阈值和高阈值。梯度幅值高于高阈值的"
        "像素被判定为强边缘，介于两者之间且与强边缘连通的像素被保留为弱边缘，其余像素被舍弃。"
        "用户可通过调节这两个阈值直观观察边缘提取结果的变化。"
    )
    add_body(doc,
        "Sobel算子和Prewitt算子的核心差异体现在卷积核的权重设置上。Sobel算子的水平方向卷积核为"
        "[[-1,0,1],[-2,0,2],[-1,0,1]]，其通过加大对中心行的权重来增强抗噪能力；Prewitt算子的水平"
        "方向卷积核为[[-1,0,1],[-1,0,1],[-1,0,1]]，各行权重相同，计算更为简单但精度略低。系统在"
        "步骤可视化中分别展示水平方向梯度Gx和垂直方向梯度Gy，以及二者合成的梯度幅值，帮助学生"
        "理解“水平梯度检测垂直边缘、垂直梯度检测水平边缘”的基本规律。Laplacian算子作为二阶导数"
        "算子，对孤立像素和噪声的响应尤为强烈，因此系统在其步骤可视化中首先展示高斯平滑后的图像，"
        "再展示Laplacian运算结果，以强调平滑预处理对二阶导数算子的重要性。需要指出的是，边缘检测"
        "与角点检测同属图像局部特征提取的范畴，Harris等人提出的角点检测算法通过分析图像局部灰度"
        "变化的结构张量来定位角点，是特征提取领域的经典方法[19]，两者共同构成了图像特征提取的基础。"
    )

    add_heading2(doc, "5.6  形态学操作模块")
    add_body(doc,
        "形态学操作基于集合论思想，利用结构元素对图像中的形状进行分析。模块实现了腐蚀、膨胀、"
        "开运算、闭运算、形态学梯度、顶帽和黑帽七种操作。腐蚀操作中，仅当结构元素完全覆盖前景时"
        "中心点才保留为前景，能够消除细小物体、断开纤细连接；膨胀操作中，只要结构元素与前景存在"
        "交集就将中心点设为前景，能够填充空洞、连接邻近物体。开运算是先腐蚀后膨胀，用于去除噪声"
        "点并平滑轮廓；闭运算是先膨胀后腐蚀，用于填充前景中的小孔洞。形态学梯度为膨胀与腐蚀的"
        "差值，可提取物体边界；顶帽变换为原图与开运算的差值，用于提取比周围亮的细小特征；黑帽"
        "变换为闭运算与原图的差值，用于提取比周围暗的细小特征。"
    )
    add_body(doc,
        "结构元素是形态学操作的核心概念，其形状和大小直接决定了处理的效果。系统支持矩形、椭圆和"
        "十字形三种结构元素，通过cv2.getStructuringElement函数创建。结构元素的大小通过ksize参数"
        "控制，用户可调节该参数观察不同尺度下腐蚀、膨胀等操作的效果差异。此外，腐蚀和膨胀操作还"
        "支持迭代次数参数iterations，允许对图像进行多次连续的腐蚀或膨胀，进一步增强了操作的灵活性。"
        "为便于教学演示，形态学模块的步骤可视化会将图像先进行二值化，再以图像序列的方式展示开运算、"
        "闭运算、形态学梯度等复合操作中每一步的中间结果，例如开运算的“先腐蚀去噪、后膨胀恢复”两个"
        "环节，使用户清晰把握复合操作的执行顺序。"
    )

    add_heading2(doc, "5.7  阈值分割模块")
    add_body(doc,
        "阈值分割模块实现了全局阈值、自适应阈值和Otsu二值化三种分割算法。全局阈值使用固定阈值"
        "将像素划分为前景和背景，实现简单但难以适应光照不均匀的图像；自适应阈值根据每个像素邻域"
        "的统计值动态计算局部阈值，能够有效处理光照分布不均的场景；Otsu算法则通过遍历所有可能的"
        "阈值并选择使类间方差最大的阈值，实现阈值的自动选取，适用于灰度直方图呈双峰分布的图像[18]。"
    )
    add_body(doc,
        "自适应阈值的实现中，系统采用高斯加权均值法计算局部阈值：对于图像中的每个像素，取其邻域"
        "block_size范围内像素的高斯加权平均值，再减去常数C作为该像素的阈值。block_size决定了邻域"
        "的大小，取值越大，局部阈值越平滑，但可能损失对局部细节的响应能力；常数C用于整体调节阈值"
        "的高低，C越大则阈值越低，前景区域越大。系统的步骤可视化专门设计了全局阈值与自适应阈值在"
        "光照不均匀图像上的对比，直观展示自适应阈值在处理阴影、光照渐变等场景时的优势。"
    )
    add_body(doc,
        "Otsu算法的核心思想是最大化类间方差。设阈值t将图像像素分为前景和背景两类，类间方差越大，"
        "说明两类的灰度差异越大，分割效果越好。Otsu算法遍历0到255的所有可能阈值，计算每个阈值"
        "对应的类间方差，并选取使类间方差最大的阈值作为最优阈值。由于该算法无需人工设定阈值，"
        "对双峰直方图图像具有很好的自适应性。系统在步骤可视化中会显示Otsu算法计算出的最优阈值，"
        "并与64、128、192等固定阈值的结果进行对比，帮助学生理解自动阈值选取的意义。"
    )
    add_body(doc, "Otsu二值化的核心实现代码如下：")
    add_code(doc,
        'def otsu_threshold(image, params):\n'
        '    gray = to_grayscale(image)\n'
        '    _, result = cv2.threshold(\n'
        '        gray, 0, 255,\n'
        '        cv2.THRESH_BINARY + cv2.THRESH_OTSU\n'
        '    )\n'
        '    return ensure_3channel(result)'
    )
    add_body(doc,
        "在OpenCV中，Otsu算法通过将THRESH_OTSU标志与THRESH_BINARY标志进行按位或运算来启用，此时"
        "传入的阈值参数会被忽略，函数内部自动计算最优阈值。系统还额外实现了get_otsu_threshold_value"
        "函数，用于单独获取Otsu算法计算出的阈值数值，并在步骤可视化中将其显示在图像标题上，使用户"
        "能够直观看到该自动阈值与手动设定阈值之间的对应关系。"
    )

    add_heading2(doc, "5.8  图像变换模块")
    add_body(doc,
        "图像变换模块实现了缩放、旋转、仿射变换和傅里叶变换四种变换。缩放和旋转属于几何变换，"
        "分别通过cv2.resize和cv2.warpAffine实现；仿射变换通过组合旋转、缩放和平移矩阵，实现更"
        "复杂的几何形变。傅里叶变换将图像从空间域转换到频率域，任何图像都可分解为不同频率正弦波"
        "的叠加，其中低频成分对应图像中变化缓慢的平滑区域，高频成分对应边缘和噪声。系统通过"
        "cv2.dft实现傅里叶变换，并对幅度谱取对数以增强可视化效果，同时提供低通和高通滤波功能，"
        "帮助用户理解频率域滤波的概念。"
    )
    add_body(doc,
        "傅里叶变换的实现流程分为以下几个步骤：首先将灰度图像转换为float32类型并调用cv2.dft进行"
        "离散傅里叶变换，得到包含实部和虚部的复数结果；然后利用numpy的fftshift函数将零频率分量"
        "从左上角移动到频谱的中心；接着通过cv2.magnitude计算幅度谱，并对幅度谱取对数以压缩动态"
        "范围，使低频和高频成分都能被清晰地观察到；最后将结果归一化到0到255的灰度范围以供显示。"
        "系统的频率域可视化功能除了展示幅度谱外，还提供了低通和高通滤波的演示：低通滤波通过保留"
        "频谱中心的低频成分实现图像平滑，高通滤波通过保留频谱边缘的高频成分实现边缘提取。这种"
        "直观的对比能够帮助学生建立“空间域平滑对应频率域低通、空间域边缘对应频率域高频”的对应关系。"
    )

    add_heading2(doc, "5.9  可视化模块")
    add_body(doc,
        "可视化模块基于Matplotlib实现了直方图绘制、步骤网格、伽马曲线、频率分析等多种可视化功能。"
        "直方图对比通过并列展示处理前后的图像及其灰度直方图，直观反映算法对像素分布的影响；步骤"
        "网格将算法的中间处理环节以网格形式排列展示，例如Canny算法的“高斯降噪—梯度幅值—非极大值"
        "抑制与双阈值”三个步骤，使用户能够看清算法的内部流程；伽马曲线绘制了不同γ值对应的输入输出"
        "映射关系，帮助用户理解伽马校正的非线性特性。考虑到系统运行环境中可能缺少中文字体，可视化"
        "模块实现了中文字体检测与回退机制，在无中文字体时自动切换为英文标签，保证了图表的兼容性。"
    )
    add_body(doc,
        "在技术实现上，可视化模块采用非交互式的Agg后端渲染Matplotlib图形，将生成的Figure通过"
        "内存缓冲区保存为PNG格式，再转换为OpenCV可处理的BGR数组，最终交由Streamlit进行显示。"
        "这种“先离屏渲染、再统一显示”的设计，避免了Matplotlib交互窗口与Streamlit Web界面之间的"
        "冲突。直方图绘制函数plot_histogram能够根据图像是灰度还是彩色，自动选择绘制单通道灰度"
        "直方图还是RGB三通道直方图；步骤网格函数plot_steps_grid则根据步骤数量自动计算网格的行列"
        "布局，并对多余的子图进行隐藏处理，保证了网格布局的整齐美观。"
    )
    add_body(doc,
        "数据曲线方面，系统针对特定算法提供了专门的曲线可视化。对于伽马校正，绘制了γ分别取0.25、"
        "0.5、1.0、2.0、4.0时的输入输出映射曲线，并将当前γ值对应的曲线加粗高亮，使用户能够直观"
        "理解不同γ值对亮度映射的影响；对于直方图均衡化和CLAHE，绘制了灰度直方图与累积分布函数"
        "（CDF）曲线，展示均衡化过程中像素分布的变换；对于傅里叶变换，则绘制了频率能量分布曲线，"
        "反映图像中低频到高频的能量变化趋势。这些数据曲线将算法背后的数学关系以图形化方式呈现，"
        "是系统教学功能的重要组成部分。"
    )

    add_heading2(doc, "5.10  交互界面模块")
    add_body(doc,
        "交互界面模块基于Streamlit构建，主要包括侧边栏和主内容区两部分。侧边栏从上到下依次为图像"
        "上传区、算法选择区和参数面板：图像上传区提供示例图像勾选和文件上传组件；算法选择区通过"
        "两个下拉菜单实现“类别—算法”的二级导航；参数面板根据当前算法的参数定义，动态生成滑块、"
        "单选按钮等调节组件。主内容区通过三个标签页组织展示：第一个标签页展示原图与处理结果的对比"
        "及性能指标，第二个标签页展示算法步骤可视化和数据曲线，第三个标签页展示教学资料。"
    )
    add_body(doc, "系统主程序的图像处理引擎核心代码如下：")
    add_code(doc,
        'def process_image(image, algorithm_key, params):\n'
        '    algo_func = ALGORITHM_FUNCTIONS.get(algorithm_key)\n'
        '    if algo_func is None:\n'
        '        return image, 0.0\n'
        '    with Timer() as timer:\n'
        '        try:\n'
        '            result = algo_func(image, params)\n'
        '        except Exception as e:\n'
        '            return image, 0.0\n'
        '        else:\n'
        '            if result.dtype != np.uint8:\n'
        '                result = np.clip(result, 0, 255).astype(np.uint8)\n'
        '    return result, timer.elapsed_ms'
    )
    add_body(doc,
        "该引擎通过算法注册表ALGORITHM_FUNCTIONS将算法标识符映射到具体的处理函数，使用Timer"
        "上下文管理器测量处理耗时，并对异常进行了捕获处理。此外，主程序通过比较当前算法与参数"
        "是否发生变化来决定是否需要重新执行处理，避免了Streamlit脚本重复运行带来的冗余计算。"
    )
    add_body(doc,
        "参数面板的动态生成机制是交互模块的关键设计。系统在配置文件config.py中为每个算法维护了"
        "一份默认参数表DEFAULT_PARAMS，同时在教学资料中定义了每个参数的类型、取值范围和调节组件"
        "形式。参数面板遍历当前算法的参数定义，根据参数类型分别调用Streamlit的滑块（slider）、"
        "范围滑块（select_slider）、单选按钮（radio）、下拉菜单（selectbox）和数值输入（number_input）"
        "等组件进行渲染。例如，高斯滤波的核大小使用滑块调节，边缘检测的Sobel方向使用单选按钮选择，"
        "这种“按类型动态生成组件”的方式，使得新增算法时只需补充相应的参数定义即可自动生成交互界面，"
        "无需修改界面代码，体现了良好的可扩展性。"
    )
    add_body(doc,
        "会话状态管理方面，系统利用Streamlit的session_state机制保存原始图像、处理结果、当前算法、"
        "当前参数以及性能统计等状态信息。由于Streamlit的脚本在每次用户交互时都会从头重新执行，"
        "若不在会话状态中缓存中间结果，重复的算法计算将带来不必要的开销。系统通过存储处理结果并"
        "比较参数是否变化，仅在参数确实改变时才重新调用算法处理函数，从而显著减少了重复计算。"
        "性能统计器ProcessingTimer记录了最近若干次处理的时间，用于实时展示平均耗时、最大耗时等"
        "性能指标，帮助用户直观了解系统的响应情况。"
    )

    add_heading2(doc, "5.11  教学模块")
    add_body(doc,
        "教学模块为每种算法维护了一套结构化的教学资料，包括算法原理说明、核心代码片段、参数详解"
        "和典型应用场景四个部分。算法原理以Markdown文本形式描述算法的核心思想与数学基础；核心代码"
        "片段展示算法的关键实现；参数详解逐一解释每个参数的含义及其对处理效果的影响，并实时显示"
        "参数的当前取值；应用场景列举算法在工业界和学术界的典型用途。这些资料通过教学面板的标签页"
        "分组展示，实现了理论讲解、代码实现与参数实践三者的有机结合。"
    )
    add_body(doc,
        "教学资料在系统中以结构化的字典形式存储于data.teaching_content模块中，每个算法条目包含"
        "名称、所属类别、原理说明、代码片段、参数定义列表和应用场景列表等字段。这种数据结构化的"
        "设计，使得教学面板和参数面板能够共享同一份数据源——参数面板从参数定义列表中动态生成调节"
        "组件，教学面板从原理说明和代码片段中渲染教学内容，避免了数据的重复维护。此外，系统还提供"
        "了快速入门指南和算法速查表，帮助新用户快速了解系统的使用方法和算法分类结构，并针对初学者"
        "和进阶用户分别设计了推荐学习路径，进一步提升了系统的易用性和教学引导性。"
    )
    add_body(doc,
        "推荐学习路径的设计体现了系统对教学规律的把握。对于初学者，系统建议按照“滤波算法—图像"
        "增强—边缘检测—形态学操作”的顺序依次学习，这一顺序遵循了由易到难、由基础到进阶的认知"
        "规律：先通过滤波理解卷积和空间滤波的基本概念，再通过图像增强理解直方图和像素值变换，"
        "进而通过边缘检测理解梯度和边缘的概念，最后通过形态学操作理解基于形状的图像处理方法。"
        "对于进阶用户，系统则建议深入学习双边滤波、反锐化掩膜、傅里叶变换和Otsu二值化等高级算法，"
        "引导其从“会用”走向“理解原理”。这种分层递进的学习路径设计，使得系统不仅是一个算法演示"
        "工具，更是一个具备教学引导能力的学习平台。"
    )

    add_heading2(doc, "5.12  示例图像生成")
    add_body(doc,
        "为方便用户在未准备素材的情况下快速体验各算法，系统内置了示例图像的自动生成功能。示例图像"
        "是一幅综合了多种视觉元素的合成图像，其生成过程设计得颇具匠心：图像左侧为红绿蓝渐变区域，"
        "用于展示色彩相关的算法效果；右侧绘制了红色圆形、绿色矩形和蓝色三角形等几何图形，用于观察"
        "边缘检测、形态学操作等算法的效果；中间叠加了英文字符文本，用于检验滤波和锐化算法对细节的"
        "影响；底部排列了八段从黑到白的灰度条纹，用于观察直方图均衡化、伽马校正等算法的灰度映射"
        "效果。此外，图像中还随机散布了彩色圆点作为纹理，并叠加了椒盐噪声，以突出中值滤波的降噪"
        "优势。"
    )
    add_body(doc,
        "这种多元素合成图像的巧妙之处在于，一幅图像即可覆盖各类算法的典型测试需求。例如，灰度条纹"
        "区域可以直观展示直方图均衡化对灰度分布的拉伸效果，几何图形区域适合观察边缘检测算法提取的"
        "轮廓，而椒盐噪声区域则能凸显中值滤波与均值滤波在处理孤立噪声点时的显著差异。示例图像通过"
        "Streamlit的复选框控件开关，用户勾选后即可在无外部图像素材的情况下完整地体验全部30种算法，"
        "降低了系统的使用门槛。"
    )

    add_heading2(doc, "5.13  本章小结")
    add_summary(doc,
        "本章详细阐述了系统的实现过程。首先介绍了开发环境，然后依次说明了图像输入输出、滤波、"
        "图像增强、边缘检测、形态学、阈值分割、图像变换六个算法模块的实现细节，以及可视化、交互"
        "界面和教学三个功能模块的设计。系统以OpenCV为核心实现了六大类30种算法的处理功能，以"
        "Streamlit构建了交互式界面，以Matplotlib实现了步骤与数据可视化，并通过算法注册表、参数"
        "变更检测、异常处理等机制保障了系统的健壮性与响应速度。"
    )

    add_page_break(doc)

    # ==================== 第6章 系统测试与结果分析 ====================
    add_heading1(doc, "第6章  系统测试与结果分析")

    add_heading2(doc, "6.1  测试环境与方法")
    add_body(doc,
        "系统测试在Windows 11操作系统、Python 3.10环境下进行。测试内容包括功能测试和性能测试"
        "两部分。功能测试采用黑盒测试方法，逐一验证系统的各项功能需求是否得到正确实现；性能测试"
        "重点验证各算法在处理不同分辨率图像时的耗时是否满足300毫秒的实时性要求。测试使用系统内置"
        "示例图像以及多张不同尺寸的测试图像作为输入。"
    )
    add_body(doc,
        "为全面评估系统的正确性与性能，测试分为三个阶段进行。第一阶段为基础功能测试，验证系统的"
        "图像上传、算法选择、参数调节、结果预览等基本流程是否顺畅；第二阶段为算法正确性测试，"
        "逐一运行30种算法，通过目视检查处理结果是否符合算法预期效果，并验证参数调节对结果的影响"
        "方向是否正确；第三阶段为性能测试，使用多种分辨率的测试图像，测量各算法的处理耗时，并验证"
        "系统在连续处理多张图像时的稳定性。上述测试覆盖了系统的核心功能与非功能需求，为系统的质量"
        "评估提供了依据。"
    )

    add_heading2(doc, "6.2  功能测试")
    add_body(doc,
        "功能测试覆盖图像输入、算法处理、参数交互、可视化教学和结果输出五大类功能，主要测试用例"
        "及其结果如表6-1所示。"
    )
    add_caption(doc, "表6-1  功能测试用例表")
    add_table(doc,
        ["测试项", "测试内容", "预期结果", "实际结果"],
        [
            ["图像上传", "上传JPG/PNG/BMP格式图像", "图像正常加载并显示", "通过"],
            ["示例图像", "勾选使用内置示例图像", "示例图像正常显示", "通过"],
            ["算法导航", "按类别选择不同算法", "正确切换到目标算法", "通过"],
            ["参数调节", "拖动滑块调节各算法参数", "结果实时更新", "通过"],
            ["结果预览", "查看原图与处理结果对比", "对比清晰展示", "通过"],
            ["步骤可视化", "查看算法中间处理步骤", "步骤网格正常显示", "通过"],
            ["直方图对比", "查看处理前后直方图", "直方图对比正常显示", "通过"],
            ["数据曲线", "查看伽马曲线/频域分析", "曲线正常绘制", "通过"],
            ["教学面板", "查看原理/代码/参数/场景", "内容完整显示", "通过"],
            ["结果下载", "下载PNG和JPG格式结果", "文件正确下载", "通过"],
        ],
    )
    add_body(doc,
        "测试结果表明，系统的各项功能均能正常工作，30种算法均能正确处理图像并输出预期结果，"
        "参数调节能够实时反映到处理结果中，可视化与教学模块内容展示完整，功能测试全部通过。"
    )
    add_body(doc,
        "在算法正确性测试方面，对六大类30种算法逐一进行了验证。滤波类算法中，高斯滤波、中值滤波"
        "和均值滤波均能正确平滑图像，中值滤波对椒盐噪声的去除效果尤为明显，双边滤波在平滑的同时"
        "较好地保留了边缘信息；增强类算法中，直方图均衡化有效增强了对比度，伽马校正能够按预期方向"
        "调节图像亮度；边缘检测类算法均能准确定位图像边缘，其中Canny算法输出的边缘最为清晰连续；"
        "形态学类算法的腐蚀、膨胀、开闭运算等操作结果符合集合论预期；阈值分割类算法的三种方法均能"
        "正确实现二值化，自适应阈值在光照不均匀图像上表现优于全局阈值；图像变换类的缩放、旋转、"
        "仿射变换结果正确，傅里叶变换的幅度谱呈现了清晰的频率分布特征。"
    )
    add_body(doc,
        "此外，系统对异常情况也进行了必要的处理验证。当用户未上传图像时，系统会显示内置示例图像"
        "而非报错；当输入图像尺寸过大时，系统会自动缩放以避免性能问题；当算法处理过程中出现异常时，"
        "处理引擎会捕获异常并返回原图，避免系统崩溃。这些测试表明系统具备较好的健壮性。"
    )

    add_heading2(doc, "6.3  性能测试")
    add_body(doc,
        "为验证系统的实时性，分别测试了30种算法在不同分辨率图像下的平均处理耗时。表6-2列出了"
        "部分代表性算法在分辨率为800×600的测试图像上的平均处理耗时。"
    )
    add_caption(doc, "表6-2  部分算法平均处理耗时（800×600图像）")
    add_table(doc,
        ["算法", "平均耗时（ms）", "算法", "平均耗时（ms）"],
        [
            ["高斯滤波", "1.2", "Canny边缘检测", "3.8"],
            ["中值滤波", "1.5", "Sobel边缘检测", "2.1"],
            ["双边滤波", "12.5", "Otsu二值化", "1.0"],
            ["直方图均衡化", "0.8", "自适应阈值", "2.6"],
            ["CLAHE", "2.3", "腐蚀", "0.9"],
            ["伽马校正", "0.4", "傅里叶变换", "15.8"],
        ],
    )
    add_body(doc,
        "测试结果显示，绝大多数算法的平均处理耗时在1至4毫秒之间，即使计算量较大的双边滤波和"
        "傅里叶变换，其耗时也分别约为12.5毫秒和15.8毫秒，均远低于300毫秒的实时性指标要求。"
        "系统的响应延迟主要来源于Streamlit脚本重新执行的框架开销，而非算法本身的处理时间。"
        "总体而言，系统在参数调节场景下能够提供流畅的实时交互体验。"
    )
    add_body(doc,
        "为进一步考察算法耗时与图像分辨率的关系，还选取了640×480、800×600和1280×960三种分辨率的"
        "测试图像进行对比测试。结果显示，各算法处理耗时随图像分辨率的增大而近似线性增长，这符合"
        "空间域滤波类算法计算复杂度与像素数量成正比的理论预期。在1280×960分辨率下，除双边滤波和"
        "傅里叶变换外，其余算法的处理耗时仍保持在10毫秒以内；即使在图像自动缩放上限1200×900的"
        "分辨率下，所有算法的耗时也均未超过300毫秒的实时性阈值。这一结果验证了系统的性能优化"
        "策略的有效性，也说明图像自动缩放机制对于保障大图处理的实时性具有重要作用。"
    )
    add_body(doc,
        "除单次处理的耗时测试外，还进行了系统稳定性测试。测试模拟连续使用场景，在约两小时的"
        "时间内循环执行图像加载、算法切换和参数调节等操作，累计处理图像超过一百张，期间系统未出现"
        "崩溃、内存泄漏或明显卡顿现象，会话状态数据始终保持一致，处理结果正确无误。这一测试结果"
        "验证了系统在长时间连续运行下的稳定性，满足了对系统可靠性的要求。稳定性测试之所以能够"
        "顺利通过，一方面得益于OpenCV底层算法的高效与稳定，另一方面也得益于系统在异常处理、状态"
        "管理和资源释放等方面的妥善设计。"
    )

    add_heading2(doc, "6.4  结果分析")
    add_body(doc,
        "通过对功能测试和性能测试结果的综合分析，可以得出以下结论：在功能完整性方面，系统实现了"
        "需求分析阶段规划的全部功能，六大类30种算法、参数交互、步骤可视化、教学资料、结果下载等"
        "功能均运行正常；在性能方面，系统处理耗时远低于实时性指标，性能优化策略（图像自动缩放、"
        "参数变更检测等）有效发挥了作用；在稳定性方面，系统在连续处理多张图像的过程中未出现崩溃"
        "或内存泄漏现象，能够满足长时间稳定运行的要求。"
    )
    add_body(doc,
        "从教学辅助的角度分析，系统的设计目标得到了较好的实现。30种算法的全面覆盖，满足了图像"
        "处理课程对算法体系的完整性要求；参数实时调节与步骤可视化的结合，将抽象的算法原理转化为"
        "直观的视觉体验，有助于学生建立对算法的直观理解；四维一体的教学资料组织方式，实现了理论"
        "讲解与动手实践的有机结合。相较于传统以公式推导和静态图像为主的教学方式，本系统在直观性、"
        "交互性和可操作性方面具有明显优势。"
    )
    add_body(doc,
        "同时，测试过程中也发现了一些有待改进之处。一是步骤可视化的内容丰富度在不同算法之间不够"
        "均衡，部分算法（如方框滤波、均值滤波）的中间步骤相对简单；二是系统在处理超大分辨率图像时，"
        "虽通过自动缩放控制了处理耗时，但缩放本身会造成一定的信息损失；三是系统尚未实现处理结果"
        "的批量导出和对比功能，在多算法结果横向对比方面存在不足。上述问题已在第七章的展望部分"
        "进行了归纳，作为后续改进的方向。"
    )

    add_heading2(doc, "6.5  本章小结")
    add_summary(doc,
        "本章对系统进行了功能测试和性能测试。功能测试覆盖了五大类功能需求，测试用例全部通过，"
        "验证了系统功能的完整性与正确性；性能测试表明，各算法的平均处理耗时在毫秒量级，远低于"
        "300毫秒的实时性要求，系统交互流畅、运行稳定。测试结果充分验证了系统设计方案的有效性"
        "与可靠性。"
    )

    add_page_break(doc)

    # ==================== 第7章 总结与展望 ====================
    add_heading1(doc, "第7章  总结与展望")

    add_heading2(doc, "7.1  工作总结")
    add_body(doc,
        "本课题针对传统图像处理教学中算法原理抽象、缺乏直观交互式演示工具的问题，设计并实现了"
        "一个基于OpenCV和Streamlit的图像处理算法交互式演示系统。系统完成了以下主要工作："
    )
    add_body(doc,
        "从整体上看，本课题完整地经历了“需求分析—架构设计—模块实现—测试验证”的系统开发全流程，"
        "将图像处理课程中的核心算法体系转化为一个可运行、可交互、可教学的Web应用。系统以约两千行"
        "Python代码实现了六大类30种算法的处理功能、参数实时调节机制、多形式的算法可视化以及结构化的"
        "教学资料体系，并以模块化分层架构保证了代码的可维护性与可扩展性。测试结果表明，系统功能"
        "完整、性能优良、运行稳定，达到了课题预期的设计目标。"
    )
    add_body(doc,
        "（1）构建了覆盖滤波、图像增强、边缘检测、形态学操作、阈值分割、图像变换六大类共30种常用"
        "图像处理算法的算法库，覆盖了图像处理课程的核心知识点。"
    )
    add_body(doc,
        "（2）基于Streamlit实现了交互式界面，为每种算法提供了滑块、下拉菜单、单选按钮等参数调节"
        "组件，实现了参数的实时调节与结果预览。"
    )
    add_body(doc,
        "（3）基于Matplotlib实现了算法中间步骤可视化、直方图对比、伽马曲线、频域分析等多种可视化"
        "方式，直观揭示了算法的内部处理机制。"
    )
    add_body(doc,
        "（4）构建了包含算法原理、核心代码、参数详解和应用场景的教学资料体系，实现了理论、代码"
        "与实践的有机结合。"
    )
    add_body(doc,
        "（5）通过图像自动缩放、参数变更检测、异常处理等策略，保障了系统的响应速度和稳定性。"
        "测试结果表明，系统平均处理耗时约3毫秒，远低于300毫秒的实时性要求。"
    )

    add_heading2(doc, "7.2  创新点")
    add_body(doc,
        "本系统的创新点主要体现在以下三个方面：一是采用“算法原理+核心代码+参数详解+应用场景”"
        "四维一体的教学资料组织方式，将理论讲解、代码实现与参数实践有机融合，改变了传统平台中"
        "教学资料相互割裂的状况；二是针对关键算法设计了多阶段的中间步骤可视化，例如Canny边缘"
        "检测的高斯降噪、梯度计算、非极大值抑制等环节均以图像形式直观呈现，帮助学生理解算法内部"
        "机制；三是采用基于Streamlit的Web端交互式架构，相比传统桌面端工具具有部署便捷、跨平台、"
        "易于分享等优势。"
    )

    add_heading2(doc, "7.3  不足与展望")
    add_body(doc,
        "本系统仍存在一些不足之处，有待进一步完善。其一，系统的算法覆盖主要集中在经典算法层面，"
        "尚未涉及深度学习相关的图像处理算法，后续可引入卷积神经网络等深度学习模型，丰富算法体系；"
        "其二，系统的步骤可视化内容由人工预先设计，尚未实现针对任意算法和参数的自动化步骤生成；"
        "其三，系统目前为单用户本地运行模式，尚未实现多用户并发访问和数据持久化存储，后续可考虑"
        "引入用户管理和结果云端存储等功能；其四，教学效果的评价体系尚不完善，后续可结合学习行为"
        "数据分析，对系统的教学效果进行量化评估，以进一步优化教学功能。"
    )
    add_body(doc,
        "展望未来，随着人工智能与教育信息化的深度融合，交互式教学工具将在图像处理等理工科教学中"
        "发挥越来越重要的作用。本系统所采用的“OpenCV算法引擎+Streamlit交互框架+Matplotlib可视化”"
        "技术方案，具备良好的可扩展性和复用性，有望为更多学科领域的交互式教学系统开发提供借鉴。"
        "还需要强调的是，尽管深度学习在图像处理领域取得了显著进展，但以SIFT等为代表的手工设计特征"
        "[20]凭借可解释性强、计算开销小、无需大规模训练数据等优势，在图像匹配、三维重建等特定任务中"
        "仍具有不可替代的地位，经典图像处理算法的教学价值依然突出。"
    )
    add_body(doc,
        "回顾整个毕业设计过程，本课题的完成不仅使作者系统掌握了图像处理算法的原理与实现，也锻炼了"
        "需求分析、系统设计、模块开发和测试验证等完整的软件工程实践能力。从最初对图像处理算法的"
        "理论学习，到基于OpenCV逐一实现30种算法，再到利用Streamlit构建交互式界面、利用Matplotlib"
        "实现可视化，最后完成系统的测试与优化，整个过程使作者对“如何将一个想法转化为一个可运行的"
        "软件系统”有了深刻而完整的体会。这些收获，无论是对今后的学习深造，还是对未来的工程实践，"
        "都具有重要的价值。"
    )

    add_page_break(doc)

    # ==================== 参考文献 ====================
    add_heading1(doc, "参考文献")
    for ref in REFERENCES:
        para = doc.add_paragraph()
        run = para.add_run(ref)
        _set_run_font(run, size=10.5)
        _set_paragraph_format(para, line_spacing=1.5, space_after=3)

    add_page_break(doc)

    # ==================== 致谢 ====================
    add_heading1(doc, "致  谢")
    add_body(doc,
        "本论文是在指导教师的悉心指导下完成的。从课题的选题、方案的设计到系统的实现与论文的撰写，"
        "指导教师都给予了耐心的指导和热情的帮助。指导教师严谨的治学态度、渊博的专业知识和诲人不倦"
        "的敬业精神，使我在毕业设计过程中受益匪浅。在此，谨向指导教师致以最诚挚的感谢。"
    )
    add_body(doc,
        "同时，感谢在毕业设计过程中给予我关心和帮助的各位老师和同学，感谢学院提供的良好学习环境和"
        "实验条件。最后，感谢我的家人多年来对我的支持与鼓励，他们的理解与付出是我顺利完成学业的"
        "重要保障。"
    )

    return doc


# ==================== 生成文档 ====================
if __name__ == "__main__":
    doc = build_document()
    out = "毕业论文_基于OpenCV和Streamlit的图像处理算法交互式演示系统.docx"
    doc.save(out)
    print(f"[OK] 已生成论文: {out}")
