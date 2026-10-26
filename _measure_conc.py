# -*- coding: utf-8 -*-
"""
并发实测：
 A. 服务层：启动 Streamlit 服务，用 1/5/10/20 路并发 HTTP 请求测响应时间与成功率
 B. 计算层：多线程并发调用高斯滤波，测 1/2/4/8 并发下的单次延迟与吞吐
结果写入 _conc_metrics.json
"""
import sys, os, json, time, statistics, subprocess, urllib.request
from concurrent.futures import ThreadPoolExecutor
sys.stdout.reconfigure(encoding="utf-8")

import numpy as np
import cv2

ROOT = r'd:\1\bishe'
PY = r'd:\1\bishe\.venv\Scripts\python.exe'
PORT = 8533
BASE = f'http://127.0.0.1:{PORT}'

def create_sample_image():
    rng = np.random.default_rng(42)
    h, w = 600, 800
    img = np.full((h, w, 3), 240, dtype=np.uint8)
    gradient = np.linspace(0, 255, 400, dtype=np.uint8)
    img[50:250, 50:450, 0] = gradient
    img[50:250, 50:450, 1] = 255 - gradient
    img[50:250, 50:450, 2] = 128
    cv2.circle(img, (580, 150), 60, (50, 50, 220), -1)
    cv2.circle(img, (580, 150), 60, (0, 0, 0), 2)
    cv2.rectangle(img, (480, 250), (680, 350), (50, 180, 50), -1)
    cv2.rectangle(img, (480, 250), (680, 350), (0, 0, 0), 2)
    pts = np.array([[530, 500], [630, 400], [730, 500]], dtype=np.int32)
    cv2.fillPoly(img, [pts], (200, 100, 50))
    cv2.polylines(img, [pts], True, (0, 0, 0), 2)
    cv2.putText(img, "Image Processing", (200, 320), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (30, 30, 30), 2)
    cv2.putText(img, "OpenCV + Streamlit", (200, 370), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (60, 60, 60), 2)
    for i in range(8):
        val = i * 32
        x0, x1 = 50 + i * 90, 130 + i * 90
        cv2.rectangle(img, (x0, 500), (x1, 560), (val, val, val), -1)
        cv2.rectangle(img, (x0, 500), (x1, 560), (0, 0, 0), 1)
    n = 100
    xs = rng.integers(50, 750, size=n); ys = rng.integers(50, 550, size=n)
    radii = rng.integers(2, 6, size=n); colors = rng.integers(30, 220, size=(n, 3))
    for x, y, r, c in zip(xs, ys, radii, colors):
        cv2.circle(img, (int(x), int(y)), int(r), tuple(int(v) for v in c), -1)
    return img

RES = {"cpu": os.cpu_count()}
print("CPU 逻辑核心:", RES["cpu"])

# ================= A. 服务层并发 =================
t_start = time.perf_counter()
proc = subprocess.Popen(
    [PY, "-m", "streamlit", "run", "app.py", "--server.headless", "true",
     "--server.port", str(PORT), "--server.address", "127.0.0.1",
     "--browser.gatherUsageStats", "false"],
    cwd=ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
)
ready = False
for _ in range(120):
    try:
        urllib.request.urlopen(f"{BASE}/_stcore/health", timeout=2).read()
        ready = True; break
    except Exception:
        time.sleep(1)
boot = time.perf_counter() - t_start
print(f"服务就绪: {ready}, 启动耗时 {boot:.1f}s")
RES["server_ready"] = ready
RES["boot_s"] = round(boot, 1)

def one_get():
    t0 = time.perf_counter()
    try:
        with urllib.request.urlopen(BASE, timeout=30) as r:
            r.read()
        return (time.perf_counter() - t0) * 1000, True
    except Exception:
        return (time.perf_counter() - t0) * 1000, False

svc = []
ROUNDS = 3
if ready:
    # 预热：先串行请求几次，跳过首次页面编译的一次性开销
    for _ in range(5):
        one_get()
    for n in (1, 5, 10, 20):
        lat, ok, total = [], 0, 0
        for _ in range(ROUNDS):
            with ThreadPoolExecutor(max_workers=n) as ex:
                res = list(ex.map(lambda _: one_get(), range(n)))
            lat += [r[0] for r in res]
            ok += sum(1 for r in res if r[1])
            total += n
        svc.append({"concurrency": n, "ok": ok, "total": total,
                    "avg_ms": round(statistics.mean(lat), 1),
                    "max_ms": round(max(lat), 1)})
        print(f"  服务层 并发{n}: 成功{ok}/{total} 平均{statistics.mean(lat):.1f}ms 最大{max(lat):.1f}ms")
RES["server_rounds"] = ROUNDS
RES["server"] = svc
try:
    proc.terminate(); proc.wait(timeout=10)
except Exception:
    proc.kill()

# ================= B. 计算层并发 =================
from modules.filters import gaussian_blur
img = create_sample_image()
REP = 8
for _ in range(10):          # 预热 JIT/缓存
    gaussian_blur(img, {"ksize": (5, 5), "sigma_x": 1.0})
comp = []
for n in (1, 2, 4, 8):
    def work(_):
        t0 = time.perf_counter()
        r = gaussian_blur(img, {"ksize": (5, 5), "sigma_x": 1.0})
        return (time.perf_counter() - t0) * 1000
    t0 = time.perf_counter()
    with ThreadPoolExecutor(max_workers=n) as ex:
        lat = list(ex.map(work, range(n * REP)))
    wall = time.perf_counter() - t0
    comp.append({"concurrency": n, "calls": n * REP,
                 "avg_ms": round(statistics.mean(lat), 2),
                 "max_ms": round(max(lat), 2),
                 "throughput": round(len(lat) / wall, 1)})
    print(f"  计算层 并发{n}: 单次平均{statistics.mean(lat):.2f}ms 吞吐{len(lat)/wall:.1f}次/秒")
RES["compute"] = comp

with open(r"d:\1\bishe\_conc_metrics.json", "w", encoding="utf-8") as f:
    json.dump(RES, f, ensure_ascii=False, indent=2)
print("结果已写入 _conc_metrics.json")
