# -*- coding: utf-8 -*-
"""
第6章客观指标实测脚本（无头调用系统算法，写入真实测量值）
产出:
  - 超分辨率: 双三次 vs SRCNN 的 PSNR/SSIM
  - 加噪前后 SNR: 高斯噪声(σ=20) 与 椒盐噪声(5%) 下 四类滤波器的去噪 SNR
  - 参数消融: 高斯核大小 / 双边sigma_color / γ / Canny阈值1 的取值-效果曲线
结果写入 _ch6_metrics.json, 曲线存 figures/fig6_3_参数消融曲线.png
"""
import sys, os, json
sys.path.insert(0, r'd:\1\bishe')
os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")

import numpy as np
import cv2
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei"]
plt.rcParams["axes.unicode_minus"] = False

# ---------- 复刻 app.py 内置示例图 ----------
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
    n_dots = 100
    xs = rng.integers(50, 750, size=n_dots); ys = rng.integers(50, 550, size=n_dots)
    radii = rng.integers(2, 6, size=n_dots); colors = rng.integers(30, 220, size=(n_dots, 3))
    for x, y, r, c in zip(xs, ys, radii, colors):
        cv2.circle(img, (int(x), int(y)), int(r), tuple(int(v) for v in c), -1)
    n_noise = 300
    nx = rng.integers(0, w, size=n_noise); ny = rng.integers(0, h, size=n_noise)
    is_salt = rng.random(n_noise) < 0.5
    img[ny[is_salt], nx[is_salt]] = [255, 255, 255]
    img[ny[~is_salt], nx[~is_salt]] = [0, 0, 0]
    return img

# ---------- 指标实现（与 ui/compare.py 一致） ----------
_WIN = None
def _win():
    global _WIN
    if _WIN is None:
        k = cv2.getGaussianKernel(7, 1.5); _WIN = (k @ k.T).astype(np.float64)
    return _WIN

def metrics(a, b):
    if a.ndim == 3: a = cv2.cvtColor(a, cv2.COLOR_BGR2GRAY)
    if b.ndim == 3: b = cv2.cvtColor(b, cv2.COLOR_BGR2GRAY)
    if a.shape != b.shape: return None
    af = a.astype(np.float64); bf = b.astype(np.float64)
    mse = float(np.mean((af - bf) ** 2))
    psnr = float("inf") if mse == 0 else 10.0 * float(np.log10(255.0 ** 2 / mse))
    w = _win(); c1, c2 = (0.01*255)**2, (0.03*255)**2
    ma = cv2.filter2D(af,-1,w); mb = cv2.filter2D(bf,-1,w)
    saab = cv2.filter2D(af*bf,-1,w) - ma*mb
    ca = cv2.filter2D(af*af,-1,w) - ma*ma
    cb = cv2.filter2D(bf*bf,-1,w) - mb*mb
    ssim = float((((2*ma*mb+c1)*(2*saab+c2))/((ma*ma+mb*mb+c1)*(ca+cb+c2))).mean())
    return {"psnr": psnr, "ssim": ssim}

def snr_db(clean, x):
    c = clean.astype(np.float64); r = c - x.astype(np.float64)
    vc, vr = float(np.var(c)), float(np.var(r))
    return float("inf") if vr == 0 else 10.0*float(np.log10(vc/vr))

def sp_noise(gray, amount, seed=7):
    rng = np.random.default_rng(seed)
    out = gray.copy(); n = int(amount * gray.size)
    idx = rng.choice(gray.size, n, replace=False)
    half = n // 2
    flat = out.reshape(-1); flat[idx[:half]] = 255; flat[idx[half:]] = 0
    return out

RES = {}
img = create_sample_image()
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# ============ 1. 超分辨率: 双三次 vs SRCNN ============
from modules.deep_learning import super_resolution
sr_rows = []
ycrcb = cv2.cvtColor(img, cv2.COLOR_BGR2YCrCb); y = ycrcb[:, :, 0]
h, w = y.shape
for scale in (2, 3):
    lr = cv2.resize(y, (w//scale, h//scale), interpolation=cv2.INTER_AREA)
    bicubic = cv2.resize(lr, (w, h), interpolation=cv2.INTER_CUBIC)
    out = super_resolution(img, {"scale": scale})
    sr_y = cv2.cvtColor(out, cv2.COLOR_BGR2YCrCb)[:, :, 0]
    mb = metrics(y, bicubic); ms = metrics(y, sr_y)
    sr_rows.append({"scale": scale, "bicubic": mb, "srcnn": ms})
    print(f"[超分] {scale}x  bicubic PSNR={mb['psnr']:.2f} SSIM={mb['ssim']:.4f} | "
          f"SRCNN PSNR={ms['psnr']:.2f} SSIM={ms['ssim']:.4f}")
RES["sr"] = sr_rows

# ============ 2. 加噪前后 SNR ============
from modules.filters import mean_blur, gaussian_blur, median_blur, bilateral_filter
RNG = np.random.default_rng(7)
noisy_g = np.clip(gray.astype(np.float64) + RNG.normal(0, 20, gray.shape), 0, 255).astype(np.uint8)
noisy_sp = sp_noise(gray, 0.05)
filters = [
    ("均值滤波", mean_blur, {"ksize": (5, 5)}),
    ("高斯滤波", gaussian_blur, {"ksize": (5, 5), "sigma_x": 1.0}),
    ("中值滤波", median_blur, {"ksize": 5}),
    ("双边滤波", bilateral_filter, {"d": 9, "sigma_color": 75, "sigma_space": 75}),
]
noise_tbl = {}
print(f"[SNR] 高斯σ=20 加噪后={snr_db(gray, noisy_g):.2f}dB  椒盐5% 加噪后={snr_db(gray, noisy_sp):.2f}dB")
noise_tbl["高斯噪声σ=20"] = {"加噪后": snr_db(gray, noisy_g)}
noise_tbl["椒盐噪声5%"] = {"加噪后": snr_db(gray, noisy_sp)}
for name, fn, p in filters:
    g_out = fn(noisy_g, p); sp_out = fn(noisy_sp, p)
    noise_tbl["高斯噪声σ=20"][name] = snr_db(gray, g_out)
    noise_tbl["椒盐噪声5%"][name] = snr_db(gray, sp_out)
    print(f"   {name}: 高斯噪声后={noise_tbl['高斯噪声σ=20'][name]:.2f}dB  椒盐噪声后={noise_tbl['椒盐噪声5%'][name]:.2f}dB")
RES["snr"] = noise_tbl

# ============ 3. 参数消融 ============
from modules.enhancement import gamma_correction
from modules.edge_detection import canny_edge

abl = {}
ks = [3, 5, 7, 9, 11, 15]
abl["gaussian_ksize"] = {"x": ks,
    "y": [round(metrics(gray, gaussian_blur(noisy_g, {"ksize": (k, k), "sigma_x": 0}))["psnr"], 2) for k in ks]}
scs = [25, 50, 75, 100, 150, 200]
abl["bilateral_sigma_color"] = {"x": scs,
    "y": [round(metrics(gray, bilateral_filter(noisy_g, {"d": 9, "sigma_color": s, "sigma_space": 75}))["psnr"], 2) for s in scs]}
gs = [0.3, 0.5, 0.8, 1.0, 1.5, 2.0, 3.0]
abl["gamma"] = {"x": gs,
    "y": [round(float(gamma_correction(img, {"gamma": g}).mean()), 1) for g in gs]}
ts = [30, 50, 80, 120, 160, 200]
abl["canny_threshold1"] = {"x": ts,
    "y": [int((canny_edge(img, {"threshold1": t, "threshold2": min(t * 3, 255)}) > 0).sum()) for t in ts]}
RES["ablation"] = abl
for k, v in abl.items():
    print(f"[消融] {k}: x={v['x']} y={v['y']}")

with open(r"d:\1\bishe\_ch6_metrics.json", "w", encoding="utf-8") as f:
    json.dump(RES, f, ensure_ascii=False, indent=2)

# ============ 绘图 ============
fig, axes = plt.subplots(2, 2, figsize=(9.2, 6.4))
ax = axes[0][0]
ax.plot(abl["gaussian_ksize"]["x"], abl["gaussian_ksize"]["y"], "o-", color="#1f77b4")
ax.set_xlabel("高斯滤波核大小（像素）"); ax.set_ylabel("去噪后 PSNR (dB)")
ax.set_title("(a) 高斯滤波：核大小—去噪效果"); ax.grid(alpha=0.3)

ax = axes[0][1]
ax.plot(abl["bilateral_sigma_color"]["x"], abl["bilateral_sigma_color"]["y"], "s-", color="#d62728")
ax.set_xlabel("双边滤波颜色域标准差 σ"); ax.set_ylabel("去噪后 PSNR (dB)")
ax.set_title("(b) 双边滤波：颜色域标准差—去噪效果"); ax.grid(alpha=0.3)

ax = axes[1][0]
ax.plot(abl["gamma"]["x"], abl["gamma"]["y"], "^-", color="#2ca02c")
ax.set_xlabel("伽马校正参数 γ"); ax.set_ylabel("输出图像平均灰度")
ax.set_title("(c) 伽马校正：γ—平均亮度"); ax.grid(alpha=0.3)

ax = axes[1][1]
ax.plot(abl["canny_threshold1"]["x"], abl["canny_threshold1"]["y"], "d-", color="#9467bd")
ax.set_xlabel("Canny 低阈值"); ax.set_ylabel("检测到的边缘像素数")
ax.set_title("(d) Canny：低阈值—边缘像素数"); ax.grid(alpha=0.3)

plt.tight_layout()
out_png = r"d:\1\bishe\figures\fig6_3_参数消融曲线.png"
plt.savefig(out_png, dpi=200)
print("图已保存:", out_png)
print("JSON:", r"d:\1\bishe\_ch6_metrics.json")
