"""
毕业论文参考文献重排序脚本（GB/T 7714 顺序编码制）

要求：
  1) 严格按参考文献在正文中首次出现的先后顺序排列；
  2) 统一标点、字体、悬挂缩进格式；
  3) 正文引用标记同步重编号，与列表一一对应。

实现：
  - 参考文献使用 numPr 自动编号（numId=20），仅需重排段落顺序即可自动更新 [n]；
  - 正文引用为字面 [n] 文本，需按 old→new 映射手动重编号；
  - 清理残留的字面 "[ " 与末尾空段落。

输出覆盖 _最终.docx。
"""

import sys
import re

sys.stdout.reconfigure(encoding="utf-8")

from docx import Document
from docx.oxml.ns import qn

DOC = "毕设/（先用1）科文学院本科生毕业论文模板-中文模板（理工科)_最终.docx"
REF_STYLE = "论文参考文献内容"

# ==================== 37 篇参考文献（旧顺序 old[1]..old[37]）的规范字符串 ====================

REFERENCES_OLD = [
    # old[1]
    "冈萨雷斯,伍兹.数字图像处理（第三版）[M].阮秋琦,阮宇智,译.北京:电子工业出版社,2011.",
    # old[2]
    "阮秋琦.数字图像处理学（第四版）[M].北京:电子工业出版社,2013.",
    # old[3]
    "章毓晋.图像工程（第四版）[M].北京:清华大学出版社,2018.",
    # old[4]
    "毛星云,冷雪飞.OpenCV3编程入门[M].北京:电子工业出版社,2015.",
    # old[5]
    "李立宗.OpenCV轻松入门：面向Python[M].北京:电子工业出版社,2019.",
    # old[6]
    "Bradski G, Kaehler A. Learning OpenCV 3: Computer Vision in C++ with the OpenCV Library[M]. Sebastopol: O'Reilly Media, 2017.",
    # old[7]
    "Canny J. A computational approach to edge detection[J]. IEEE Transactions on Pattern Analysis and Machine Intelligence, 1986, 8(6): 679-698.",
    # old[8]
    "Otsu N. A threshold selection method from gray-level histograms[J]. IEEE Transactions on Systems, Man, and Cybernetics, 1979, 9(1): 62-66.",
    # old[9]
    "Harris C, Stephens M. A combined corner and edge detector[C]//Proceedings of the Alvey Vision Conference. 1988: 147-151.",
    # old[10]
    "Lowe D G. Distinctive image features from scale-invariant keypoints[J]. International Journal of Computer Vision, 2004, 60(2): 91-110.",
    # old[11]
    "Rudin L I, Osher S, Fatemi E. Nonlinear total variation based noise removal algorithms[J]. Physica D: Nonlinear Phenomena, 1992, 60(1-4): 259-268.",
    # old[12]
    "Tomasi C, Manduchi R. Bilateral filtering for gray and color images[C]//Proceedings of the IEEE International Conference on Computer Vision. 1998: 839-846.",
    # old[13]
    "贾小军,喻擎苍.基于开源计算机视觉库OpenCV的图像处理[J].计算机应用与软件,2008,25(4):276-278.",
    # old[14]
    "刘立强,蔡晓华,吴泽全.基于OpenCV的除草机器人图像处理技术[J].农机化研究,2013(12):162-165.",
    # old[15]
    "李振杰,臧春华,苏宝玉,等.基于OpenCV图像处理软件的设计[J].物联网技术,2024,14(6).",
    # old[16]
    "杨蕊遥.基于嵌入式和OpenCV的智能视频监控系统研究[D].大连:大连海事大学,2018.",
    # old[17]
    "Shalini G M, Anand R, Sankeerth T, et al. Integrated colorization and styling approach for enhancing image clarity[C]//2024 3rd International Conference on Applied Artificial Intelligence and Computing (ICAAIC). IEEE, 2024: 798-804.",
    # old[18]
    "迟盛元,张晓洁,周登贤,等.基于OpenCV的车辆压线行为检测系统设计与实现[J].中国汽车,2026,36(07):422-426.",
    # old[19]
    "李锋霞,尹君驰,贺树贤,等.基于支持向量机的水果识别系统设计[J].农机化研究,2026.",
    # old[20]
    "李婷,刘雨函,刘彬,等.基于OpenCV图像处理识别车道线的算法研究[J].机械工程与自动化,2026,55(03):45-47+52.",
    # old[21]
    "同佳欣,段欣宇,冯月春.基于OpenCV与TensorFlow的轻量级蘑菇种类识别系统设计[J].河南科技,2026.",
    # old[22]
    "陈凯文,周雪寒.基于OpenCV的图像识别与智能定价系统[J].中阿科技论坛(中英文),2026(04):94-98.",
    # old[23]
    "阳甜欣,王伟业,秦立坤,等.基于OpenCV的污水处理混凝监控系统研究[J].物联网技术,2025,15(23):73-76.",
    # old[24]
    "蒋碧萱,张玉柱,郝志彩.基于OpenCV的浮法玻璃完整性检测系统[J].玻璃,2025,52(12):27-31.",
    # old[25]
    "李储成,邵永明,余钰洋,等.基于OpenCV的多特征融合检测算法及其实时应用研究[J].电脑知识与技术,2025,21(30):15-17+20.",
    # old[26]
    "黄婧,胡利超,杨雪.基于多孔介质孔隙结构的图像处理方法研究[J].内江师范学院学报,2025,40(10):55-62.",
    # old[27]
    "薛文,缑瑞宾,陈义明,等.基于Python-OpenCV的鲜食毛豆形貌特征提取算法研究[J].黑龙江工业学院学报(综合版),2025,25(09):132-139.",
    # old[28]
    "兰帅丹,赵伟,江三林.基于Python及OpenCV的银行卡卡号识别系统的设计与实现[J].电脑编程技巧与维护,2025(07):139-142.",
    # old[29]
    "张侃,何方印,石兆彬,等.OpenCV图像处理在水稻考种中的应用[J].智慧农业导刊,2025,5(11):26-29+35.",
    # old[30]
    "韩轶菲,冯军磊.基于OpenCV机器视觉的水尺识别系统开发与应用[C]//2025第三届长三角水利学术大会暨水利先进技术（产品）推介会.中国浙江义乌,2025.",
    # old[31]
    "熊宇奇,李昱莹,张腾,等.基于OpenCV的SLM成形TC4合金缺陷识别与分析[J].特种铸造及有色合金,2025,45(04):528-534.",
    # old[32]
    "何祥芝,涂海宁,刘建胜.基于OpenCV的人脸黑头识别算法[J].南昌大学学报(工科版),2024,46(01):111-116.",
    # old[33]
    "曹磊,纪国法,彭超,等.基于OpenCV图像处理的支撑剂颗粒圆度和球度检测方法[J].中国科技论文,2024,19(01):85-91.",
    # old[34]
    "赵洁,杨涛,常皓婵.基于OpenCV的绿幕背景视频抠图[J].通信与信息技术,2023(06):18-21.",
    # old[35]
    "唐健.基于OpenCV的LED针脚夹角偏差视觉检测方法研究[J].电子制作,2025(19):30-33.",
    # old[36]
    "YALAMARTHI R N S V, SHAIK S, SINGH D, et al. Real-time face mask detection using streamlit, tensorflow, keras and open-CV[C]//2022 IEEE International Conference on Data Science and Information System (ICDSIS). IEEE, 2022: 75-79.",
    # old[37]
    "PARKER A, HEFLIN A, JONES L C. Analyzing University of Virginia Health publications using open data, Python, and Streamlit[J]. Journal of the Medical Library Association, 2021, 109(4): 688-689.",
]

# 首次出现顺序（new 编号 → old 编号）
NEW_TO_OLD = [
    13, 18, 20, 14, 29, 27, 24, 31, 35, 33, 16, 28, 21, 19, 32, 15, 22, 23, 25, 26,
    30, 34, 17, 36, 37, 1, 2, 3, 6, 4, 5, 12, 11, 7, 9, 8, 10,
]
# old → new 映射（用于正文引用重编号）
OLD_TO_NEW = {old: new for new, old in enumerate(NEW_TO_OLD, start=1)}


def set_para_text(p, text):
    """替换段落文本，保留首 run 字体格式与段落 pPr（含 numPr 自动编号）。"""
    fmt_run = p.runs[0] if p.runs else None
    for r in list(p.runs):
        r._element.getparent().remove(r._element)
    run = p.add_run(text)
    if fmt_run is not None:
        run.font.name = fmt_run.font.name
        run.font.size = fmt_run.font.size
        run.font.bold = fmt_run.font.bold
    return p


def main():
    doc = Document(DOC)

    # ---- 1. 重编号正文引用（跳过代码段） ----
    print("== 正文引用重编号 ==")
    code_markers = ("def ", "params.get", "cv2.", "return ", "import ", "np.")
    for p in doc.paragraphs:
        if p.style.name == REF_STYLE:
            continue
        if any(m in p.text for m in code_markers):
            continue
        if re.search(r"\[\d{1,2}\]", p.text):
            def repl(m):
                n = int(m.group(1))
                return f"[{OLD_TO_NEW[n]}]" if n in OLD_TO_NEW else m.group(0)
            new_text = re.sub(r"\[(\d{1,2})\]", repl, p.text)
            if new_text != p.text:
                set_para_text(p, new_text)

    # ---- 2. 收集当前参考文献段落（含空段落），删除空段落 ----
    refs = [p for p in doc.paragraphs if p.style.name == REF_STYLE]
    # 分离：空段落删除，非空段落按旧顺序保留
    nonempty = [p for p in refs if p.text.strip()]
    empty = [p for p in refs if not p.text.strip()]
    for p in empty:
        p._element.getparent().remove(p._element)
    print(f"  有效参考文献 {len(nonempty)} 条，删除空段落 {len(empty)} 个")

    assert len(nonempty) == 37, f"预期 37 条，实际 {len(nonempty)}"

    # 按新顺序重排段落元素
    ordered_els = [nonempty[old - 1]._p for old in NEW_TO_OLD]

    # 找到锚点（最后一条参考文献之后的下一段，或参考文献标题）
    anchor = refs[0]._p.getprevious()  # 参考文献标题
    # 先全部摘除
    for el in ordered_els:
        el.getparent().remove(el)
    # 再按新顺序插回标题之后
    for el in ordered_els:
        anchor.addnext(el)
        anchor = el

    # ---- 3. 重写文本为规范字符串（新顺序） ----
    from docx.text.paragraph import Paragraph
    for new_idx, old in enumerate(NEW_TO_OLD, start=1):
        p = nonempty[old - 1]  # Paragraph 对象仍有效
        set_para_text(p, REFERENCES_OLD[old - 1])

    # ---- 4. 保存 ----
    doc.save(DOC)
    print(f"已保存: {DOC}")


if __name__ == "__main__":
    main()
