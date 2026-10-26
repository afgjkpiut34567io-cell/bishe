# -*- coding: utf-8 -*-
"""
内存实测（三档模式，各在独立子进程中运行，避免相互干扰）：
  models      : 预训练模型常驻内存（加载前/后 RSS 增量，MB）
  loop_cache  : 连续处理 120 轮，含结果缓存（复刻 st.cache_data 行为）
  loop_nocache: 连续处理 120 轮，不含缓存
输出 _mem_models.json / _mem_loop_cache.json / _mem_loop_nocache.json
"""
import sys, os, json, ctypes, ctypes.wintypes as wt
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r'd:\1\bishe')

OUT = r'd:\1\bishe'


class PMC(ctypes.Structure):
    _fields_ = [("cb", wt.DWORD), ("PageFaultCount", wt.DWORD),
                ("PeakWorkingSetSize", ctypes.c_size_t),
                ("WorkingSetSize", ctypes.c_size_t),
                ("QuotaPeakPagedPoolUsage", ctypes.c_size_t),
                ("QuotaPagedPoolUsage", ctypes.c_size_t),
                ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t),
                ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
                ("PagefileUsage", ctypes.c_size_t),
                ("PeakPagefileUsage", ctypes.c_size_t)]


_k32 = ctypes.WinDLL('kernel32')
_psapi = ctypes.WinDLL('psapi')
_k32.GetCurrentProcess.restype = wt.HANDLE
_psapi.GetProcessMemoryInfo.argtypes = [wt.HANDLE, ctypes.POINTER(PMC), wt.DWORD]
_psapi.GetProcessMemoryInfo.restype = wt.BOOL


def mem():
    c = PMC(); c.cb = ctypes.sizeof(c)
    ok = _psapi.GetProcessMemoryInfo(_k32.GetCurrentProcess(), ctypes.byref(c), c.cb)
    if not ok:
        raise RuntimeError("GetProcessMemoryInfo 失败")
    return round(c.WorkingSetSize / 1048576.0, 1), round(c.PeakWorkingSetSize / 1048576.0, 1)


def create_sample_image():
    import numpy as np, cv2
    rng = np.random.default_rng(42)
    h, w = 600, 800
    img = np.full((h, w, 3), 240, dtype=np.uint8)
    gradient = np.linspace(0, 255, 400, dtype=np.uint8)
    img[50:250, 50:450, 0] = gradient
    img[50:250, 50:450, 1] = 255 - gradient
    img[50:250, 50:450, 2] = 128
    cv2.circle(img, (580, 150), 60, (50, 50, 220), -1)
    cv2.rectangle(img, (480, 250), (680, 350), (50, 180, 50), -1)
    pts = np.array([[530, 500], [630, 400], [730, 500]], dtype=np.int32)
    cv2.fillPoly(img, [pts], (200, 100, 50))
    cv2.putText(img, "Image Processing", (200, 320), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (30, 30, 30), 2)
    for i in range(8):
        val = i * 32
        cv2.rectangle(img, (50 + i * 90, 500), (130 + i * 90, 560), (val, val, val), -1)
    return img


def nbytes(x):
    try:
        return int(x.nbytes)
    except Exception:
        return 0


# ==================== 模式：models ====================
def run_models():
    import torch
    from torchvision import models as tvm
    import torchvision.models.segmentation  # 提前 import，避免计入首个模型增量
    from modules.dl_models import SRCNN, CIFAR10Net, MODELS_DIR

    rss0 = mem()[0]
    res = {"rss_after_import_mb": rss0, "models": []}
    prev = rss0

    def record(name, model, ckpt_bytes=None):
        nonlocal prev
        r = mem()[0]
        res["models"].append({
            "name": name,
            "params": int(sum(p.numel() for p in model.parameters())),
            "file_mb": round(ckpt_bytes / 1048576.0, 1) if ckpt_bytes else None,
            "rss_before_mb": prev,
            "rss_after_mb": r,
            "delta_mb": round(r - prev, 1),
        })
        print(f"  {name}: 参数量 {res['models'][-1]['params']:,} | RSS {prev}->{r} MB (+{r - prev:.1f})")
        prev = r

    m1 = tvm.mobilenet_v2(weights=tvm.MobileNet_V2_Weights.DEFAULT).eval()
    record("MobileNetV2（图像分类）", m1)

    m2 = tvm.segmentation.deeplabv3_mobilenet_v3_large(
        weights=tvm.segmentation.DeepLabV3_MobileNet_V3_Large_Weights.DEFAULT).eval()
    record("DeepLabV3（语义分割）", m2)

    p_sr = os.path.join(MODELS_DIR, "srcnn.pth")
    m3 = SRCNN(); m3.load_state_dict(torch.load(p_sr, map_location="cpu")); m3.eval()
    record("SRCNN（超分辨率）", m3, os.path.getsize(p_sr))

    p_c = os.path.join(MODELS_DIR, "cifar10_cnn.pth")
    m4 = CIFAR10Net(num_classes=10)
    m4.load_state_dict(torch.load(p_c, map_location="cpu")); m4.eval()
    record("CIFAR10Net（自定义分类）", m4, os.path.getsize(p_c))

    res["peak_rss_mb"] = mem()[1]
    res["rss_final_mb"] = mem()[0]
    res["total_delta_mb"] = round(res["rss_final_mb"] - rss0, 1)
    json.dump(res, open(os.path.join(OUT, "_mem_models.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)


# ==================== 模式：连续处理循环 ====================
def run_loop(cache_on):
    from modules.registry import ALGORITHM_FUNCTIONS as AF
    img = create_sample_image()

    WORK = [
        ("gaussian_blur", lambda i: {"ksize": (5, 5), "sigma_x": 0.5 + 0.02 * i}),
        ("median_blur", lambda i: {"ksize": 3 + 2 * (i % 6)}),
        ("mean_blur", lambda i: {"ksize": (3 + 2 * (i % 5), 3 + 2 * (i % 5))}),
        ("bilateral_filter", lambda i: {"d": 9, "sigma_color": 30 + 5 * (i % 20), "sigma_space": 75}),
        ("gamma_correction", lambda i: {"gamma": 0.3 + 0.05 * (i % 20)}),
        ("canny_edge", lambda i: {"threshold1": 20 + 5 * (i % 20), "threshold2": 60 + 15 * (i % 20)}),
        ("otsu_threshold", lambda i: {}),
        ("resize_scale", lambda i: {"scale": 0.3 + 0.03 * (i % 20)}),
        ("fourier_lowpass", lambda i: {"cutoff_ratio": 0.05 + 0.02 * (i % 20)}),
    ]

    N, STEP = 120, 10
    base = mem()[0]
    curve, cache, cache_bytes = [], {} if cache_on else None, 0
    for i in range(N):
        key, mk = WORK[i % len(WORK)]
        params = mk(i)
        out = AF[key](img.copy(), params)
        if cache_on:
            ck = (key, tuple(sorted(params.items())))
            if ck not in cache:
                cache[ck] = out.copy()
                cache_bytes += nbytes(cache[ck])
        if (i + 1) % STEP == 0:
            r = mem()[0]
            curve.append({"iter": i + 1, "rss_mb": r})
            print(f"  轮次 {i + 1:>3}: RSS {r} MB")

    res = {"mode": "cache" if cache_on else "nocache", "iters": N,
           "base_rss_mb": base, "curve": curve,
           "peak_rss_mb": mem()[1], "final_rss_mb": mem()[0],
           "growth_mb": round(mem()[0] - base, 1),
           "cache_entries": len(cache) if cache_on else 0,
           "cache_bytes_mb": round(cache_bytes / 1048576.0, 1)}
    fn = "_mem_loop_cache.json" if cache_on else "_mem_loop_nocache.json"
    json.dump(res, open(os.path.join(OUT, fn), "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)


if __name__ == "__main__":
    mode = sys.argv[1]
    print("模式:", mode, "| 起始 RSS", mem()[0], "MB")
    if mode == "models":
        run_models()
    elif mode == "loop_cache":
        run_loop(True)
    elif mode == "loop_nocache":
        run_loop(False)
    print("完成:", mode, "| 最终 RSS", mem()[0], "MB | 峰值", mem()[1], "MB")
