# -*- coding: utf-8 -*-
"""
可行性探针：无头调用系统算法，验证 SRCNN 可跑并给出真实 PSNR/SSIM。
不写任何文件，仅打印。
"""
import sys, os, time
sys.path.insert(0, r'd:\1\bishe')
os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")

import numpy as np
import cv2

# ---------- 复刻 app.py 的内置示例图（固定种子42, 600x800） ----------
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

# ---------- 复刻 ui/compare.py 的指标实现 ----------
_WIN = None
def _ssim_window():
    global _WIN
    if _WIN is None:
        k = cv2.getGaussianKernel(7, 1.5)
        _WIN = (k @ k.T).astype(np.float64)
    return _WIN

def _to_single(img):
    if img.ndim == 2: return img
    if img.shape[2] == 1: return img[:, :, 0]
    return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

def metrics(a, b):
    a = _to_single(a); b = _to_single(b)
    if a.shape != b.shape: return None
    af = a.astype(np.float64); bf = b.astype(np.float64)
    mse = float(np.mean((af - bf) ** 2))
    psnr = float("inf") if mse == 0 else 10.0 * float(np.log10(255.0 ** 2 / mse))
    w = _ssim_window(); c1, c2 = (0.01*255)**2, (0.03*255)**2
    ma = cv2.filter2D(af, -1, w); mb = cv2.filter2D(bf, -1, w)
    saab = cv2.filter2D(af*bf, -1, w) - ma*mb
    ca = cv2.filter2D(af*af, -1, w) - ma*ma
    cb = cv2.filter2D(bf*bf, -1, w) - mb*mb
    ssim = float((((2*ma*mb + c1) * (2*saab + c2)) / ((ma*ma + mb*mb + c1) * (ca + cb + c2))).mean())
    return {"mse": mse, "psnr": psnr, "ssim": ssim}

def snr(clean, x):
    """SNR = 10*log10( var(signal)/var(residual) ), 单位 dB"""
    c = clean.astype(np.float64); r = (clean.astype(np.float64) - x.astype(np.float64))
    vc = float(np.var(c)); vr = float(np.var(r))
    return float("inf") if vr == 0 else 10.0*float(np.log10(vc/vr))

img = create_sample_image()
print("示例图:", img.shape, "通道数", img.shape[2])

# ============ 1. SRCNN vs 双三次（超分 Y 通道） ============
print("\n===== 超分辨率: 双三次 vs SRCNN =====")
try:
    from modules.deep_learning import super_resolution
    ycrcb = cv2.cvtColor(img, cv2.COLOR_BGR2YCrCb)
    y = ycrcb[:, :, 0]
    h, w = y.shape
    for scale in (2, 3):
        lr = cv2.resize(y, (w//scale, h//scale), interpolation=cv2.INTER_AREA)
        bicubic = cv2.resize(lr, (w, h), interpolation=cv2.INTER_CUBIC)
        t0 = time.time()
        out = super_resolution(img, {"scale": scale})
        dt = (time.time()-t0)*1000
        sr_y = cv2.cvtColor(out, cv2.COLOR_BGR2YCrCb)[:, :, 0]
        m_bi = metrics(y, bicubic); m_sr = metrics(y, sr_y)
        print(f"  scale={scale}x  bicubic: PSNR={m_bi['psnr']:.2f}dB SSIM={m_bi['ssim']:.4f} | "
              f"SRCNN: PSNR={m_sr['psnr']:.2f}dB SSIM={m_sr['ssim']:.4f}  (耗时{dt:.0f}ms)")
    print("  [OK] SRCNN 可无头运行")
except Exception as e:
    print("  [FAIL] SRCNN:", repr(e))

# ============ 2. 加噪前后 SNR（高斯噪声 + 中值/高斯/双边） ============
print("\n===== 加噪前后 SNR =====")
try:
    from modules.filters import gaussian_blur, median_blur, bilateral_filter
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    rng = np.random.default_rng(7)
    for sigma_n in (10, 20):
        noise = rng.normal(0, sigma_n, gray.shape)
        noisy = np.clip(gray.astype(np.float64) + noise, 0, 255).astype(np.uint8)
        print(f"  噪声σ={sigma_n}: 加噪后SNR={snr(gray, noisy):.2f}dB")
        for name, fn, p in [
            ("中值滤波ksize=5", median_blur, {"ksize": 5}),
            ("高斯滤波ksize=5", gaussian_blur, {"ksize": (5,5), "sigma_x": 1.0}),
            ("双边滤波d=9", bilateral_filter, {"d": 9, "sigma_color": 75, "sigma_space": 75}),
        ]:
            out = fn(noisy, p)
            print(f"      {name}: 去噪后SNR={snr(gray, out):.2f}dB")
except Exception as e:
    print("  [FAIL] filters:", repr(e))

# ============ 3. 参数-效果消融（示例：高斯核大小 / γ / Canny阈值） ============
print("\n===== 参数消融(示例) =====")
try:
    from modules.filters import gaussian_blur, median_blur
    from modules.enhancement import gamma_correction
    from modules.edge_detection import canny_edge
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    rng = np.random.default_rng(7)
    noisy = np.clip(gray.astype(np.float64) + rng.normal(0, 20, gray.shape), 0, 255).astype(np.uint8)
    print("  高斯核 ksize -> 去噪PSNR:", end=" ")
    for k in (3,5,7,9,11,15):
        o = gaussian_blur(noisy, {"ksize": (k,k), "sigma_x": 0})
        print(f"{k}:{metrics(gray,o)['psnr']:.2f}", end="  ")
    print()
    print("  γ -> 平均灰度:", end=" ")
    for g in (0.3,0.5,0.8,1.0,1.5,2.0,3.0):
        o = gamma_correction(img, {"gamma": g})
        print(f"{g}:{o.mean():.1f}", end="  ")
    print()
    print("  Canny t1 -> 边缘像素数:", end=" ")
    for t in (30,50,80,120,160,200):
        o = canny_edge(img, {"threshold1": t, "threshold2": min(t*3, 255)})
        print(f"{t}:{int((o>0).sum())}", end="  ")
    print()
except Exception as e:
    print("  [FAIL] ablation:", repr(e))
