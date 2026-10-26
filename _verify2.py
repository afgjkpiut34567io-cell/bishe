# -*- coding: utf-8 -*-
"""回读校验新记录表与中期检查表"""
import sys, os, time

sys.stdout.reconfigure(encoding="utf-8")
import pythoncom
import win32com.client as wc

D = r"c:\Users\25626\Desktop\7230267148 杨康康 过程检查记录表"
NEW = os.path.join(D, "4.7230267148_杨康康_过程检查记录表.doc")
MID = os.path.join(D, "3.中期检查表.doc")


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


def open_doc(path):
    lock = os.path.join(os.path.dirname(path), "~$" + os.path.basename(path)[2:])
    if os.path.exists(lock):
        try:
            os.remove(lock)
        except Exception:
            pass
    app = wc.DispatchEx("Word.Application")
    app.Visible = False
    app.DisplayAlerts = 0
    return app, retry(lambda: app.Documents.Open(path, ReadOnly=True, AddToRecentFiles=False, Visible=False))


# ---- 记录表 ----
app, doc = open_doc(NEW)
time.sleep(1.2)
tb = retry(lambda: doc.Tables(1))
print("=== 记录表 行6~行13 ===")
for r in range(6, 14):
    d = retry(lambda r=r: tb.Cell(r, 1).Range.Text).replace('\x07', '').strip()
    rec = " ".join(retry(lambda r=r: tb.Cell(r, 2).Range.Text).replace('\x07', '').split())
    body = rec.replace("指导教师（签名）：", "")
    print(f"[行{r}] {d}  签名行保留={'指导教师（签名）：' in rec}  字数={len(body.strip())}")
    print(f"        {body[:58]}...")
print("表头:", " | ".join(
    " ".join(retry(lambda r=r, c=c: tb.Cell(r, c).Range.Text).replace('\x07', '').split())
    for r, c in ((1, 2), (2, 2), (2, 4), (2, 6), (4, 2), (4, 4))))
doc.Close(False)
app.Quit()

# ---- 中期检查表 ----
app, doc = open_doc(MID)
time.sleep(1.2)
tb = retry(lambda: doc.Tables(1))
print("\n=== 中期检查表 表头 ===")
for r, c in ((1, 2), (1, 4), (1, 6), (2, 2), (2, 4), (2, 6), (3, 2)):
    v = " ".join(retry(lambda r=r, c=c: tb.Cell(r, c).Range.Text).replace('\x07', '').split())
    print(f"  行{r}列{c}: {v}")
for r in (4, 5):
    cell = retry(lambda r=r: tb.Cell(r, 1))
    n = retry(lambda: cell.Range.Paragraphs.Count)
    print(f"\n--- 行{r}（共{n}段）---")
    for i in range(1, n + 1):
        p = retry(lambda i=i: cell.Range.Paragraphs(i))
        t = retry(lambda: p.Range.Text).replace('\x07', '').strip()
        if t:
            fs = retry(lambda: p.Range.Font.Size)
            ls = retry(lambda: p.Range.ParagraphFormat.LineSpacingRule)
            print(f"  [{i}] 字号={fs} 行距规则={ls}  {t[:60]}")
for r in (6, 7, 9):
    v = " ".join(retry(lambda r=r: tb.Cell(r, 1).Range.Text).replace('\x07', '').split())
    print(f"\n行{r}: {v if v else '(空)'}")
doc.Close(False)
app.Quit()
print("\nDONE")
