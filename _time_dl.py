# -*- coding: utf-8 -*-
"""实测 MobileNetV2 / DeepLabV3 首次加载耗时（权重已在本地缓存，不触发联网）"""
import sys, time
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r'd:\1\bishe')
import torch, torchvision
from torchvision import models

print("torch:", torch.__version__, "| torchvision:", torchvision.__version__)
print("device:", "cuda" if torch.cuda.is_available() else "cpu")
print("torch hub 缓存:", torch.hub.get_dir())

def timed(fn, n=2):
    out = []
    for _ in range(n):
        t0 = time.perf_counter(); m = fn(); dt = (time.perf_counter() - t0) * 1000
        out.append(dt)
    return m, out

m1, t1 = timed(lambda: models.mobilenet_v2(weights=models.MobileNet_V2_Weights.DEFAULT).eval())
print(f"MobileNetV2: 第1次 {t1[0]:.0f} ms, 第2次 {t1[1]:.0f} ms | 参数量 {sum(p.numel() for p in m1.parameters()):,}")
m2, t2 = timed(lambda: models.segmentation.deeplabv3_mobilenet_v3_large(weights=models.segmentation.DeepLabV3_MobileNet_V3_Large_Weights.DEFAULT).eval())
print(f"DeepLabV3 : 第1次 {t2[0]:.0f} ms, 第2次 {t2[1]:.0f} ms | 参数量 {sum(p.numel() for p in m2.parameters()):,}")
print("权重 URL:")
print("  MobileNetV2:", models.MobileNet_V2_Weights.DEFAULT.url)
print("  DeepLabV3 :", models.segmentation.DeepLabV3_MobileNet_V3_Large_Weights.DEFAULT.url)
