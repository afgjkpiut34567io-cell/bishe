# -*- coding: utf-8 -*-
import sys, re
sys.stdout.reconfigure(encoding="utf-8")
p = r'd:\1\bishe\毕设\技术栈问题_杨康康.html'
txt = re.sub(r'<[^>]+>', ' ', open(p, encoding='utf-8').read())
txt = re.sub(r'\s+', ' ', txt)
for m in re.finditer("自研", txt):
    print("---- @", m.start())
    print(txt[max(0, m.start() - 700): m.start() + 500])
    print()
