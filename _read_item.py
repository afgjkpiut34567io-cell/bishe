# -*- coding: utf-8 -*-
import sys, re
sys.stdout.reconfigure(encoding="utf-8")
p = r'd:\1\bishe\毕设\技术栈问题_杨康康.html'
html = open(p, encoding='utf-8').read()
# 按列表项/标题拆
items = re.split(r'(?=<h3|<li|<h2)', html)
for it in items:
    if "自研" in it or "5.10" in it:
        txt = re.sub(r'<[^>]+>', '', it)
        txt = re.sub(r'\n{2,}', '\n', txt).strip()
        print("=====")
        print(txt[:1200])
