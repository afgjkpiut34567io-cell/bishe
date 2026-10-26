# -*- coding: utf-8 -*-
"""绘制图6-3 连续处理过程内存增长曲线"""
import sys, json
sys.stdout.reconfigure(encoding="utf-8")
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei"]
plt.rcParams["axes.unicode_minus"] = False

A = json.load(open(r'd:\1\bishe\_mem_loop_cache.json', encoding='utf-8'))
B = json.load(open(r'd:\1\bishe\_mem_loop_nocache.json', encoding='utf-8'))
out_png = r'd:\1\bishe\figures\fig6_3_内存增长曲线.png'

xa = [0] + [p["iter"] for p in A["curve"]]
ya = [A["base_rss_mb"]] + [p["rss_mb"] for p in A["curve"]]
xb = [0] + [p["iter"] for p in B["curve"]]
yb = [B["base_rss_mb"]] + [p["rss_mb"] for p in B["curve"]]

fig, ax = plt.subplots(figsize=(7.2, 4.4))
ax.plot(xa, ya, "-o", ms=4, lw=1.8, color="#1f77b4", label="含结果缓存（st.cache_data）")
ax.plot(xb, yb, "-s", ms=4, lw=1.8, color="#d62728", label="不含结果缓存")
ax.axhline(A["peak_rss_mb"], ls="--", lw=1.1, color="#1f77b4", alpha=0.7)
ax.annotate(f'峰值 {A["peak_rss_mb"]:.1f} MB', xy=(104, A["peak_rss_mb"] - 5),
            xytext=(96, A["peak_rss_mb"] - 20), fontsize=9, color="#1f77b4", ha="right")
ax.annotate(f'稳定在 {B["final_rss_mb"]:.1f} MB', xy=(24, B["final_rss_mb"]),
            xytext=(40, B["final_rss_mb"] + 7), fontsize=9, color="#d62728")
ax.set_xlabel("连续处理轮次")
ax.set_ylabel("进程驻留内存 RSS（MB）")
ax.set_title("连续处理过程的进程驻留内存变化")
ax.set_xlim(0, 122)
ax.set_ylim(205, 380)
ax.grid(alpha=0.3)
ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.15), ncol=2, fontsize=9)
plt.tight_layout()
plt.savefig(out_png, dpi=200)
print("图已保存:", out_png)
