# -*- coding: utf-8 -*-
"""[审查项#18] 统一缩放发生位置口径：image_io 在加载时 auto_resize（影响处理与导出），
界面预览另由 resize_for_preview 负责；同步 5.x(image_io 段) 与 6.x(边界处理段)"""
import sys, shutil, copy
sys.stdout.reconfigure(encoding="utf-8")
from docx import Document
from docx.oxml.ns import qn

PATH = r'd:\1\bishe\毕设\7230267148_杨康康_基于opencv和streamlit的图像处理算法交互式演示系统 - 降重改写版.docx'
BAK = r'd:\1\bishe\毕设\_bak_降重改写版_20261014_before_scale.docx'
shutil.copy2(PATH, BAK)
print("备份:", BAK)

doc = Document(PATH)

def copy_rpr(src_run, dst_run):
    """把源 run 的字符格式复制到目标 run，保证英文/数字用同一字体"""
    src = src_run._r.find(qn('w:rPr'))
    dst = dst_run._r
    old = dst.find(qn('w:rPr'))
    if old is not None:
        dst.remove(old)
    if src is not None:
        dst.insert(0, copy.deepcopy(src))

# ---------- [180] utils.image_io 段 ----------
p = doc.paragraphs[180]
assert p.text.startswith("utils.image_io")
assert p.runs[12].text == "1200" and p.runs[14].text == "900"
copy_rpr(p.runs[6], p.runs[17])    # cv2.imdecode -> auto_resize
copy_rpr(p.runs[6], p.runs[19])    # cv2.imdecode -> resize_for_preview
copy_rpr(p.runs[14], p.runs[21])   # 900 -> 600
新版 = {
    16: "；缩放是在加载这一步由",
    17: "auto_resize",
    18: "函数完成的，它按最长边算出缩放比例，再用双线性面积插值重采样，处理与导出用的都是缩放后的图像，并不只是预览；界面预览另有",
    19: "resize_for_preview",
    20: "来负责，把宽度继续压到",
    21: "600",
    22: "像素以内，只服务于显示。另外，各个算法的输入格式得统一起来，模块为此准备灰度转换（",
}
for idx, text in 新版.items():
    p.runs[idx].text = text
print("\n[180]:", p.text)

# ---------- [282] 异常与边界处理段 ----------
q = doc.paragraphs[282]
assert q.text.startswith("针对异常和边界输入")
OLD = "超过阈值的图像，只在预览分支里按最长边等比缩小，导出依旧基于原图"
NEW = "超过阈值的图像，在加载这一步就被按最长边等比缩小，处理与导出用的都是缩放后的图像"
hit = False
for r in q.runs:
    if OLD in r.text:
        r.text = r.text.replace(OLD, NEW); hit = True
assert hit, "未匹配到 6.x 缩放表述"
print("\n[282]:", q.text[-160:])

doc.save(PATH)
print("\n已保存。")
