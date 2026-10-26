# -*- coding: utf-8 -*-
"""核验改写结果: 覆盖率/字数比/引用图表保留/红线词"""
import json, re, glob

orig = json.load(open(r'd:\1\bishe\_orig_paras.json', encoding='utf-8'))
orig_map = {}
for batch in orig:
    for it in batch:
        orig_map[str(it['idx'])] = it['text']

rew = {}
for f in sorted(glob.glob(r'd:\1\bishe\_rew\b*.json')):
    d = json.load(open(f, encoding='utf-8'))
    for k, v in d.items():
        if k in rew:
            print(f"!! 重复键: {k} in {f}")
        rew[k] = v

print(f"原文段落数: {len(orig_map)}, 改写段落数: {len(rew)}")
missing = [k for k in orig_map if k not in rew]
extra = [k for k in rew if k not in orig_map]
print(f"缺失: {missing}")
print(f"多余: {extra}")

FORBIDDEN = ['说白了', '就拿', '可以这么讲', '不难发现', '值得注意', '综上所述', '总而言之',
             '总的来说', '换言之', '与此同时', '由此可见', '我觉得', '我认为', '在我看来']

def tokens(t, pat):
    return sorted(re.findall(pat, t))

bad_len, bad_tok, bad_word = [], [], []
tot_o, tot_r = 0, 0
for k, o in orig_map.items():
    r = rew.get(k, '')
    tot_o += len(o); tot_r += len(r)
    ratio = len(r) / max(len(o), 1)
    if not (0.8 <= ratio <= 1.2):
        bad_len.append((k, len(o), len(r), round(ratio, 2)))
    # 引用/图表/公式/英文术语核对
    for pat in [r'\[\d+\]', r'图\d+(?:-\d+)?', r'表\d+(?:-\d+)?', r'式\(\d', r'[A-Za-z][A-Za-z0-9_\.]{2,}']:
        to, tr = tokens(o, pat), tokens(r, pat)
        if to != tr:
            bad_tok.append((k, pat, to, tr))
    for w in FORBIDDEN:
        if w in r:
            bad_word.append((k, w))

print(f"\n总字数: 原文{tot_o} -> 改写{tot_r} ({tot_r/tot_o:.3f})")
print(f"\n字数比越界段(>{len(bad_len)}): ")
for x in bad_len: print("  ", x)
print(f"\n保留标记不一致段({len(bad_tok)}): ")
for x in bad_tok[:30]: print("  ", x)
print(f"\n红线词命中({len(bad_word)}): ")
for x in bad_word: print("  ", x)
