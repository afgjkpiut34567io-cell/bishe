"""
毕业论文参考文献统一脚本

对齐开题报告 + 保留必需文献：
  1) 重建参考文献列表为 37 篇（开题 28 篇全部纳入 + 论文必需教材/经典算法 9 篇）；
  2) 重写第1章"国内外研究现状"三段，删去 7 篇冗余文献的引用、补充 20 篇开题文献的引用；
  3) 对其余正文引用标注做 old→new 重编号；
  4) 保持原排版样式、字体、格式不变。

输出覆盖 _最终.docx。
"""

import sys
import re

sys.stdout.reconfigure(encoding="utf-8")

from docx import Document
from docx.oxml import OxmlElement


DOC = "毕设/（先用1）科文学院本科生毕业论文模板-中文模板（理工科)_最终.docx"
REF_STYLE = "论文参考文献内容"

# ==================== 37 篇参考文献（最终顺序） ====================

REFERENCES = [
    "冈萨雷斯,伍兹.数字图像处理（第三版）[M].阮秋琦,阮宇智,译.北京:电子工业出版社,2011.",
    "阮秋琦.数字图像处理学（第四版）[M].北京:电子工业出版社,2013.",
    "章毓晋.图像工程（第四版）[M].北京:清华大学出版社,2018.",
    "毛星云,冷雪飞.OpenCV3编程入门[M].北京:电子工业出版社,2015.",
    "李立宗.OpenCV轻松入门：面向Python[M].北京:电子工业出版社,2019.",
    "Bradski G, Kaehler A. Learning OpenCV 3: Computer Vision in C++ with the OpenCV Library[M]. Sebastopol: O'Reilly Media, 2017.",
    "Canny J. A computational approach to edge detection[J]. IEEE Transactions on Pattern Analysis and Machine Intelligence, 1986, 8(6): 679-698.",
    "Otsu N. A threshold selection method from gray-level histograms[J]. IEEE Transactions on Systems, Man, and Cybernetics, 1979, 9(1): 62-66.",
    "Harris C, Stephens M. A combined corner and edge detector[C]//Proceedings of the Alvey Vision Conference. 1988: 147-151.",
    "Lowe D G. Distinctive image features from scale-invariant keypoints[J]. International Journal of Computer Vision, 2004, 60(2): 91-110.",
    "Rudin L I, Osher S, Fatemi E. Nonlinear total variation based noise removal algorithms[J]. Physica D: Nonlinear Phenomena, 1992, 60(1-4): 259-268.",
    "Tomasi C, Manduchi R. Bilateral filtering for gray and color images[C]//Proceedings of the IEEE International Conference on Computer Vision. 1998: 839-846.",
    "贾小军,喻擎苍.基于开源计算机视觉库OpenCV的图像处理[J].计算机应用与软件,2008,25(4):276-278.",
    "刘立强,蔡晓华,吴泽全.基于OpenCV的除草机器人图像处理技术[J].农机化研究,2013(12):162-165.",
    "李振杰,臧春华,苏宝玉,等.基于OpenCV图像处理软件的设计[J].物联网技术,2024,14(6).",
    "杨蕊遥.基于嵌入式和OpenCV的智能视频监控系统研究[D].大连:大连海事大学,2018.",
    "Shalini G M, Anand R, Sankeerth T, et al. Integrated colorization and styling approach for enhancing image clarity[C]//2024 3rd International Conference on Applied Artificial Intelligence and Computing (ICAAIC). IEEE, 2024: 798-804.",
    "迟盛元,张晓洁,周登贤,等.基于OpenCV的车辆压线行为检测系统设计与实现[J].中国汽车,2026,36(07):422-426.",
    "李锋霞,尹君驰,贺树贤,等.基于支持向量机的水果识别系统设计[J].农机化研究,2026.",
    "李婷,刘雨函,刘彬,等.基于OpenCV图像处理识别车道线的算法研究[J].机械工程与自动化,2026,55(03):45-47+52.",
    "同佳欣,段欣宇,冯月春.基于OpenCV与TensorFlow的轻量级蘑菇种类识别系统设计[J].河南科技,2026.",
    "陈凯文,周雪寒.基于OpenCV的图像识别与智能定价系统[J].中阿科技论坛(中英文),2026(04):94-98.",
    "阳甜欣,王伟业,秦立坤,等.基于OpenCV的污水处理混凝监控系统研究[J].物联网技术,2025,15(23):73-76.",
    "蒋碧萱,张玉柱,郝志彩.基于OpenCV的浮法玻璃完整性检测系统[J].玻璃,2025,52(12):27-31.",
    "李储成,邵永明,余钰洋,等.基于OpenCV的多特征融合检测算法及其实时应用研究[J].电脑知识与技术,2025,21(30):15-17+20.",
    "黄婧,胡利超,杨雪.基于多孔介质孔隙结构的图像处理方法研究[J].内江师范学院学报,2025,40(10):55-62.",
    "薛文,缑瑞宾,陈义明,等.基于Python-OpenCV的鲜食毛豆形貌特征提取算法研究[J].黑龙江工业学院学报(综合版),2025,25(09):132-139.",
    "兰帅丹,赵伟,江三林.基于Python及OpenCV的银行卡卡号识别系统的设计与实现[J].电脑编程技巧与维护,2025(07):139-142.",
    "张侃,何方印,石兆彬,等.OpenCV图像处理在水稻考种中的应用[J].智慧农业导刊,2025,5(11):26-29+35.",
    "韩轶菲,冯军磊.基于OpenCV机器视觉的水尺识别系统开发与应用[C]//2025第三届长三角水利学术大会暨水利先进技术（产品）推介会.中国浙江义乌,2025.",
    "熊宇奇,李昱莹,张腾,等.基于OpenCV的SLM成形TC4合金缺陷识别与分析[J].特种铸造及有色合金,2025,45(04):528-534.",
    "何祥芝,涂海宁,刘建胜.基于OpenCV的人脸黑头识别算法[J].南昌大学学报(工科版),2024,46(01):111-116.",
    "曹磊,纪国法,彭超,等.基于OpenCV图像处理的支撑剂颗粒圆度和球度检测方法[J].中国科技论文,2024,19(01):85-91.",
    "赵洁,杨涛,常皓婵.基于OpenCV的绿幕背景视频抠图[J].通信与信息技术,2023(06):18-21.",
    "唐健.基于OpenCV的LED针脚夹角偏差视觉检测方法研究[J].电子制作,2025(19):30-33.",
    "YALAMARTHI R N S V, SHAIK S, SINGH D, et al. Real-time face mask detection using streamlit, tensorflow, keras and open-CV[C]//2022 IEEE International Conference on Data Science and Information System (ICDSIS). IEEE, 2022: 75-79.",
    "PARKER A, HEFLIN A, JONES L C. Analyzing University of Virginia Health publications using open data, Python, and Streamlit[J]. Journal of the Medical Library Association, 2021, 109(4): 688-689.",
]

# ==================== 第1章 研究现状三段重写 ====================

P90_NEW = "图像处理教学工具的演进呈现出两条清晰脉络：一是载体由本地桌面应用向Web端迁移，二是功能由结果展示型静态演示转向支持参数调节与即时反馈的交互式探索。早期的图像处理教学平台大多基于MATLAB及其GUI工具构建，通过可视化界面集成多种经典算法，实现了处理结果的直观展示和参数的可交互调节，但这类平台算法库虽丰富、开发便捷，却依赖商业软件、可移植性较差，不利于网络化传播。"

P91_NEW = "随着开源计算机视觉库OpenCV的普及，基于OpenCV的图像处理平台与工程应用逐渐成为主流。贾小军等人较早介绍了利用OpenCV进行图像处理的方法，展示了其在图像平滑、边缘检测等方面的应用[13]。近年来，OpenCV在众多工程领域得到了广泛应用：在智能交通领域，迟盛元等人设计了车辆压线行为检测系统[18]，李婷等人研究了车道线识别算法[20]；在农业领域，刘立强等人将OpenCV用于除草机器人图像处理[14]，张侃等人实现了水稻考种的自动化图像分析[29]，薛文等人提取了鲜食毛豆的形貌特征[27]；在工业检测领域，蒋碧萱等人构建了浮法玻璃完整性检测系统[24]，熊宇奇等人对SLM成形TC4合金进行缺陷识别[31]，唐健提出了LED针脚夹角偏差的视觉检测方法[35]，曹磊等人测量了支撑剂颗粒的圆度和球度[33]；在安防与识别领域，杨蕊遥研究了基于嵌入式和OpenCV的智能视频监控系统[16]，兰帅丹等人实现了银行卡卡号识别[28]，同佳欣等人设计了轻量级蘑菇种类识别系统[21]，李锋霞等人构建了水果识别系统[19]，何祥芝等人研究了人脸黑头识别算法[32]；此外，李振杰等人设计了图像处理软件[15]，陈凯文等人实现了图像识别与智能定价系统[22]，阳甜欣等人开发了污水处理混凝监控系统[23]，李储成等人研究了多特征融合检测算法[25]，黄婧等人将图像处理用于多孔介质孔隙结构分析[26]，韩轶菲等人开发了水尺识别系统[30]，赵洁等人实现了绿幕背景视频抠图[34]。这些应用充分体现了OpenCV作为通用图像处理工具的强大能力与广泛适用性。"

P92_NEW = "在交互界面的实现上，早期教学系统普遍基于Qt／PyQt等桌面框架构建。此类方案虽功能完备，却存在开发周期长、跨平台部署繁琐等问题。近年来，Streamlit、Dash等Python Web框架逐步成熟，为教学类交互系统的快速搭建提供了一条更为轻量的技术路线。Streamlit凭借“用纯Python编写交互式Web应用”的理念，大幅降低了数据应用和可视化工具的开发门槛，在国际上已被用于数据探索、机器学习演示和教学辅助等多个场景。Shalini等人基于Streamlit和OpenCV开发了图像着色与风格化的交互式工具，验证了二者结合构建图像处理Web应用的可行性[17]；YALAMARTHI等人基于Streamlit、TensorFlow和Keras实现了实时口罩检测系统，进一步展示了Streamlit在机器学习演示中的应用潜力[36]；PARKER等人利用Python和Streamlit分析了弗吉尼亚大学健康相关的公开数据，验证了Streamlit在数据探索与可视化中的便捷性[37]。"

# 需要重写的段落（按唯一子串定位）
REWRITE_PARAS = [
    ("图像处理教学工具的演进呈现出两条清晰脉络", P90_NEW),
    ("随着开源计算机视觉库OpenCV的普及", P91_NEW),
    ("在交互界面的实现上，早期教学系统普遍基于Qt", P92_NEW),
]

# 需要重编号的段落（仅含保留文献，无删除）——old→new 映射
REMAP_PARAS = [
    ("数字图像在计算机中以矩阵形式存储", {1: 1, 2: 2, 3: 3}),
    ("OpenCV（Open Source Computer Vision Library）是一个开源的", {4: 4, 5: 5, 23: 6}),
    ("滤波算法模块实现了高斯滤波", {22: 12}),
    ("双边滤波是上述五种方法中计算复杂度最高", {21: 11, 22: 12}),
    ("边缘检测模块实现了Canny", {17: 7}),
    ("该加权使Sobel在差分前对邻域施加了近似高斯", {19: 9}),
    ("阈值分割模块实现了全局阈值", {18: 8}),
    ("展望未来，随着人工智能与教育信息化的深度融合", {20: 10}),
]

# ==================== 工具 ====================

def find_para(doc, substr):
    for p in doc.paragraphs:
        if substr in p.text:
            return p
    raise RuntimeError(f"未找到锚点: {substr!r}")


def set_para_text(p, text):
    """替换段落文本，保留首 run 字体格式。"""
    fmt_run = p.runs[0] if p.runs else None
    for r in list(p.runs):
        r._element.getparent().remove(r._element)
    run = p.add_run(text)
    if fmt_run is not None:
        run.font.name = fmt_run.font.name
        run.font.size = fmt_run.font.size
        run.font.bold = fmt_run.font.bold
    return p


def remap_citations(p, mapping):
    """把段落中的 [n] 按 mapping 重编号。"""
    def repl(m):
        n = int(m.group(1))
        return f"[{mapping[n]}]" if n in mapping else m.group(0)
    text = re.sub(r"\[(\d+)\]", repl, p.text)
    set_para_text(p, text)


# ==================== 主流程 ====================

def main():
    doc = Document(DOC)

    # ---- 1. 重写第1章研究现状三段 ----
    print("== 重写研究现状三段 ==")
    for sub, new in REWRITE_PARAS:
        p = find_para(doc, sub)
        set_para_text(p, new)
        print(f"  已重写: {sub[:20]}...")

    # ---- 2. 其余正文引用重编号 ----
    print("== 正文引用重编号 ==")
    for sub, mapping in REMAP_PARAS:
        p = find_para(doc, sub)
        remap_citations(p, mapping)
        print(f"  已重编号: {sub[:20]}...")

    # ---- 3. 重建参考文献列表 ----
    print("== 重建参考文献列表 ==")
    # 定位参考文献一级标题
    ref_heading = None
    for p in doc.paragraphs:
        if p.text.strip() == "参考文献" and p.style.name == "论文一级标题":
            ref_heading = p
            break
    assert ref_heading is not None, "未找到参考文献标题"

    # 收集并删除旧的参考文献段落（标题之后、致谢之前的『论文参考文献内容』样式段落）
    old_refs = []
    for p in doc.paragraphs:
        if p.style.name == REF_STYLE:
            old_refs.append(p)
    for p in old_refs:
        p._element.getparent().remove(p._element)
    print(f"  已删除旧参考文献 {len(old_refs)} 条")

    # 在标题后插入 37 条新参考文献（依次 addnext 保持顺序）
    anchor = ref_heading
    for i, ref in enumerate(REFERENCES, start=1):
        new_p = OxmlElement("w:p")
        anchor._p.addnext(new_p)
        from docx.text.paragraph import Paragraph
        para = Paragraph(new_p, ref_heading._parent)
        para.style = doc.styles[REF_STYLE]
        para.add_run(f"[{i}] {ref}")
        anchor = para
    print(f"  已插入新参考文献 {len(REFERENCES)} 条")

    # ---- 4. 保存 ----
    doc.save(DOC)
    print(f"\n已保存: {DOC}")


if __name__ == "__main__":
    main()
