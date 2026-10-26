"""
教学内容数据模块 - 所有算法的教学资料
包含：原理说明、参数解释、核心代码片段、应用场景
"""

TEACHING_CONTENT = {
    # ==================== 滤波算法 ====================
    "gaussian_blur": {
        "name": "高斯滤波 (Gaussian Blur)",
        "category": "滤波算法",
        "principle": """
### 算法原理

**高斯滤波**是一种线性平滑滤波器，使用符合**高斯分布**（正态分布）的权重模板对图像进行卷积操作。

**核心思想：**
- 中心像素赋予最大权重
- 离中心越远的像素权重越小（服从高斯分布）
- 权重由高斯函数决定：$G(x,y) = \\frac{1}{2\\pi\\sigma^2} e^{-\\frac{x^2+y^2}{2\\sigma^2}}$

**数学过程：**
1. 根据核大小 ksize 和标准差 σ 生成高斯核
2. 将高斯核与图像进行卷积
3. 每个输出像素 = 邻域像素的加权平均

**为什么能去噪？**
- 高斯噪声每个像素独立且分布相同
- 加权平均使随机噪声互相抵消，信号得以保留
- σ 越大，平滑效果越强，但图像越模糊
""",
        "params": [
            {
                "name": "ksize",
                "label": "核大小",
                "type": "slider",
                "args": {"min_value": 1, "max_value": 31, "step": 2, "value": 5},
                "explanation": "高斯核的尺寸（宽, 高）。必须为正奇数。核越大，平滑范围越广，去噪效果越强，但图像细节丢失越多。",
            },
            {
                "name": "sigma_x",
                "label": "标准差 σ",
                "type": "slider",
                "args": {"min_value": 0.1, "max_value": 10.0, "step": 0.1, "value": 1.0},
                "explanation": "高斯分布的标准差。σ越大，权重分布越分散，平滑效果越强。σ=0时由核大小自动计算。",
            },
        ],
        "code": '''
import cv2

def gaussian_blur(image, ksize=(5, 5), sigma_x=1.0):
    """高斯滤波"""
    return cv2.GaussianBlur(image, ksize, sigmaX=sigma_x)
''',
        "scenarios": [
            "📷 摄影后期：去除高斯噪声，柔化皮肤",
            "🔬 医学图像：平滑CT/MRI图像中的随机噪声",
            "🤖 计算机视觉：Canny边缘检测前的预处理步骤",
            "🎮 游戏渲染：生成景深（DoF）效果",
        ],
    },

    "median_blur": {
        "name": "中值滤波 (Median Blur)",
        "category": "滤波算法",
        "principle": """
### 算法原理

**中值滤波**是一种非线性滤波器，用滤波器窗口内所有像素值的**中位数**替换中心像素。

**核心思想：**
- 排序窗口内所有像素值
- 取中间值作为输出
- 异常值（噪声）自然被排除

**为什么对椒盐噪声有效？**
- 椒盐噪声的像素值（0或255）是极端值
- 排序后极端值在两端
- 中位数不受极端值影响
- 正常像素的中位数≈真实值

**计算示例：** 窗口 [120, 125, 130, 0, 128] → 排序 [0, 120, 125, 128, 130] → 中值 = 125
""",
        "params": [
            {
                "name": "ksize",
                "label": "核大小",
                "type": "slider",
                "args": {"min_value": 3, "max_value": 35, "step": 2, "value": 5},
                "explanation": "滤波窗口大小，必须为大于1的奇数。核越大去除噪声能力越强，但可能会模糊细节和边缘。",
            },
        ],
        "code": '''
import cv2

def median_blur(image, ksize=5):
    """中值滤波 - 对椒盐噪声效果最佳"""
    if ksize % 2 == 0:
        ksize += 1  # 确保为奇数
    return cv2.medianBlur(image, ksize)
''',
        "scenarios": [
            "📷 老照片修复：去除扫描件中的灰尘和划痕",
            "🔍 工业检测：去除传感器采集中的脉冲噪声",
            "🖼️ 文档处理：去除扫描文档中的斑点",
            "🎥 视频去噪：实时去除视频中的随机闪烁噪点",
        ],
    },

    "mean_blur": {
        "name": "均值滤波 (Mean Blur)",
        "category": "滤波算法",
        "principle": """
### 算法原理

**均值滤波**是最简单的线性滤波器，用滤波器窗口内所有像素值的**算术平均值**替换中心像素。

**核心思想：**
- 窗口中每个像素权重相同
- 输出 = 窗口内像素之和 / 窗口面积

**优点：** 算法简单，计算速度快
**缺点：** 不能区分噪声和边缘，会模糊图像细节

**数学公式：** $g(x,y) = \\frac{1}{M} \\sum_{(i,j) \\in S} f(i,j)$
""",
        "params": [
            {
                "name": "ksize",
                "label": "核大小",
                "type": "slider",
                "args": {"min_value": 1, "max_value": 31, "step": 2, "value": 5},
                "explanation": "滤波核的宽度和高度。值越大，图像越模糊。注意：核太大会导致图像明显模糊。",
            },
        ],
        "code": '''
import cv2

def mean_blur(image, ksize=(5, 5)):
    """均值滤波"""
    return cv2.blur(image, ksize)
''',
        "scenarios": [
            "📊 快速图像平滑：对实时性要求高的场景",
            "🎨 图像预处理：去除轻微随机噪声",
        ],
    },

    "bilateral_filter": {
        "name": "双边滤波 (Bilateral Filter)",
        "category": "滤波算法",
        "principle": """
### 算法原理

**双边滤波**是一种**保边去噪**的非线性滤波器，同时考虑像素的**空间距离**和**像素值相似度**两个维度。

**核心创新：** 使用两个高斯核
1. **空间核** $G_s$：距离越近权重越大（同高斯滤波）
2. **值域核** $G_r$：像素值越接近权重越大（边缘保护的关键）

**总权重：** $W = G_s(||p - q||) \\times G_r(|I_p - I_q|)$

**为什么能保边？**
- 在平滑区域：邻域像素值相近，值域核≈1，行为类似高斯滤波
- 在边缘处：两侧像素值差异大，值域核使跨边缘的像素权重≈0，边缘被保留
""",
        "params": [
            {
                "name": "d",
                "label": "滤波直径",
                "type": "slider",
                "args": {"min_value": 1, "max_value": 25, "step": 2, "value": 9},
                "explanation": "像素邻域直径。越大影响范围越大，计算量也越大。d≤0时由sigma_space自动决定。",
            },
            {
                "name": "sigma_color",
                "label": "颜色空间 σ",
                "type": "slider",
                "args": {"min_value": 1, "max_value": 200, "step": 1, "value": 75},
                "explanation": "值域标准差。越大，更多不同颜色的像素被混合。是保护边缘的关键参数。",
            },
            {
                "name": "sigma_space",
                "label": "坐标空间 σ",
                "type": "slider",
                "args": {"min_value": 1, "max_value": 200, "step": 1, "value": 75},
                "explanation": "空间域标准差。越大，更远的像素被纳入计算。控制空间平滑程度。",
            },
        ],
        "code": '''
import cv2

def bilateral_filter(image, d=9, sigma_color=75, sigma_space=75):
    """双边滤波 - 保边去噪"""
    return cv2.bilateralFilter(image, d, sigma_color, sigma_space)
''',
        "scenarios": [
            "🎨 美颜磨皮：平滑皮肤同时保留五官轮廓",
            "🏗️ 建筑摄影：去除纹理噪声保留结构边缘",
            "🖼️ HDR合成：平滑色调映射中的细节层",
            "🔬 显微图像：去除噪声同时保留细胞边界",
        ],
    },

    "box_filter": {
        "name": "方框滤波 (Box Filter)",
        "category": "滤波算法",
        "principle": """
### 算法原理

**方框滤波**与均值滤波类似，使用均匀权重的核进行滤波。与均值滤波的区别在于可以控制是否归一化。

- **归一化模式** (normalize=True)：等同于均值滤波，输出=均值
- **非归一化模式** (normalize=False)：仅计算窗口内像素和，可能导致溢出

**特点：**
- 计算极其简单，可使用积分图加速到 O(1)
- 常用于快速模糊或作为其他算法的基础操作
""",
        "params": [
            {
                "name": "ksize",
                "label": "核大小",
                "type": "slider",
                "args": {"min_value": 1, "max_value": 31, "step": 2, "value": 5},
                "explanation": "方框滤波核的尺寸。与均值滤波一致，核越大平滑效果越强。",
            },
        ],
        "code": '''
import cv2

def box_filter(image, ksize=(5, 5)):
    """方框滤波 (归一化)"""
    return cv2.boxFilter(image, -1, ksize, normalize=True)
''',
        "scenarios": [
            "⚡ 实时视频处理：需要极快速度的场合",
            "📐 积分图应用：配合积分图实现任意大小滤波",
        ],
    },

    # ==================== 图像增强 ====================
    "histogram_equalization": {
        "name": "直方图均衡化 (Histogram Equalization)",
        "category": "图像增强",
        "principle": """
### 算法原理

**直方图均衡化**通过重新分布像素亮度值来增强图像对比度。

**核心思想：**
1. 计算原始图像的灰度直方图
2. 计算累积分布函数（CDF）
3. 将CDF映射为新的像素值
4. 结果：像素值均匀分布在整个范围

**数学公式：** $s_k = (L-1) \\sum_{j=0}^{k} p_r(r_j)$
其中 $p_r$ 是像素值 $r_j$ 的概率，$L$ 是灰度级数（通常256）

**最佳效果：** 原始图像对比度低（偏暗或偏亮），直方图集中在某个区域
""",
        "params": [],
        "code": '''
import cv2

def histogram_equalization(image):
    """直方图均衡化 - 增强图像对比度"""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return cv2.equalizeHist(gray)
''',
        "scenarios": [
            "🩻 医学影像：增强X光片的对比度以辅助诊断",
            "🌃 低光照片：提亮暗部细节",
            "🔬 科学图像：增强显微镜图像的微弱特征",
            "🛰️ 遥感图像：增强卫星图像的地物对比度",
        ],
    },

    "clahe": {
        "name": "自适应直方图均衡化 (CLAHE)",
        "category": "图像增强",
        "principle": """
### 算法原理

**CLAHE** (Contrast Limited Adaptive Histogram Equalization) 是对普通直方图均衡化的改进。

**解决的问题：** 普通直方图均衡化是全局操作，会过度放大噪声，且无法处理局部对比度差异。

**CLAHE的工作方式：**
1. 将图像分成多个小块（tiles）
2. 对每个小块分别进行直方图均衡化
3. **关键创新：** 限制对比度放大（clip limit），超过阈值的直方图部分被裁剪并均匀重分配
4. 块之间使用双线性插值消除边界伪影

**clip_limit 的作用：** 防止噪声被过度放大。clip_limit越小，对比度增强越温和。
""",
        "params": [
            {
                "name": "clip_limit",
                "label": "对比度限制",
                "type": "slider",
                "args": {"min_value": 0.5, "max_value": 10.0, "step": 0.5, "value": 2.0},
                "explanation": "对比度限制阈值。越小对比度增强越温和，越大对比度越强但噪声也越明显。",
            },
            {
                "name": "tile_grid_size",
                "label": "分块大小",
                "type": "slider",
                "args": {"min_value": 2, "max_value": 32, "step": 2, "value": 8},
                "explanation": "将图像分成tile_grid_size×tile_grid_size像素的小块。小块=更局部化，大块=更全局化。",
            },
        ],
        "code": '''
import cv2

def clahe(image, clip_limit=2.0, tile_size=(8, 8)):
    """自适应直方图均衡化"""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    clahe = cv2.createCLAHE(
        clipLimit=clip_limit,
        tileGridSize=tile_size
    )
    return clahe.apply(gray)
''',
        "scenarios": [
            "👁️ 眼底图像：增强视网膜血管对比度",
            "🏥 医学影像：增强局部组织对比度",
            "🌫️ 雾天图像：改善不均匀光照条件下的可见度",
            "📱 手机拍照：提升逆光照片的暗部细节",
        ],
    },

    "contrast_brightness": {
        "name": "对比度与亮度调整",
        "category": "图像增强",
        "principle": """
### 算法原理

对比度和亮度调整是最基本的图像增强操作，通过**线性变换**实现。

**数学公式：** $g(x,y) = \\alpha \\cdot f(x,y) + \\beta$

- $\\alpha$ (alpha)：对比度系数
  - $\\alpha > 1$：对比度增强（亮的更亮，暗的更暗）
  - $\\alpha < 1$：对比度减弱
  - $\\alpha = 1$：对比度不变
- $\\beta$ (beta)：亮度偏移
  - $\\beta > 0$：整体变亮
  - $\\beta < 0$：整体变暗

**注意：** 结果会被裁剪到 [0, 255] 范围。
""",
        "params": [
            {
                "name": "alpha",
                "label": "对比度 α",
                "type": "slider",
                "args": {"min_value": 0.0, "max_value": 3.0, "step": 0.05, "value": 1.0},
                "explanation": "对比度系数 α。α>1拉伸像素值范围增强对比度；α<1压缩像素值范围降低对比度。",
            },
            {
                "name": "beta",
                "label": "亮度 β",
                "type": "slider",
                "args": {"min_value": -100, "max_value": 100, "step": 1, "value": 0},
                "explanation": "亮度偏移 β。β>0使图像整体变亮；β<0使图像整体变暗。",
            },
        ],
        "code": '''
import cv2

def contrast_brightness(image, alpha=1.0, beta=0):
    """对比度亮度调整：dst = alpha * src + beta"""
    return cv2.convertScaleAbs(image, alpha=alpha, beta=beta)
''',
        "scenarios": [
            "🎨 图像后期：快速调整照片明暗和对比",
            "📄 文档扫描：增强文字与背景的对比",
        ],
    },

    "gamma_correction": {
        "name": "伽马校正 (Gamma Correction)",
        "category": "图像增强",
        "principle": """
### 算法原理

**伽马校正**通过幂律变换对图像亮度进行非线性调整。

**数学公式：** $V_{out} = 255 \\times (\\frac{V_{in}}{255})^{\\frac{1}{\\gamma}}$

**伽马值的影响：**
| γ值 | 效果 | 适用场景 |
|-----|------|----------|
| γ < 1 | 提升暗部，图像变亮 | 过暗照片补偿 |
| γ = 1 | 恒等变换 | 不做调整 |
| γ > 1 | 压缩亮部，图像变暗 | 过曝照片补救 |

**与线性调整的区别：**
- 线性调整（对比度/亮度）对所有亮度区域影响相同
- 伽马校正对暗部和亮部的影响不同，更符合人眼感知特性
""",
        "params": [
            {
                "name": "gamma",
                "label": "伽马值 γ",
                "type": "slider",
                "args": {"min_value": 0.1, "max_value": 5.0, "step": 0.05, "value": 1.0},
                "explanation": "γ<1：提升暗部细节（图像变亮）；γ=1：不变化；γ>1：压缩亮部（图像变暗）。",
            },
        ],
        "code": '''
import cv2
import numpy as np

def gamma_correction(image, gamma=1.0):
    """伽马校正 - 非线性亮度调整"""
    inv_gamma = 1.0 / gamma
    table = np.array(
        [(i / 255.0) ** inv_gamma * 255
         for i in range(256)]
    ).astype(np.uint8)
    return cv2.LUT(image, table)
''',
        "scenarios": [
            "🖥️ 显示器校准：补偿显示器的非线性响应",
            "📷 摄影后期：精细调整暗部和亮部层次",
            "🌌 天文摄影：拉伸暗弱天体的可见度",
        ],
    },

    "sharpening": {
        "name": "图像锐化 (Sharpening)",
        "category": "图像增强",
        "principle": """
### 算法原理

**图像锐化**通过增强图像中的高频成分（边缘和细节）来使图像看起来更清晰。

**核心思想（拉普拉斯锐化）：**
1. 使用拉普拉斯算子检测图像的边缘（二阶导数）
2. 从原图中减去（或加上）检测到的边缘
3. 边缘被增强，图像看起来更锐利

**锐化核（拉普拉斯）：**
```
[ 0 -1  0]
[-1  5 -1]    ← 中心权重>1表示增强
[ 0 -1  0]
```

**过锐化的风险：** 强度过大时会产生光晕伪影（边缘周围的亮/暗环）
""",
        "params": [
            {
                "name": "strength",
                "label": "锐化强度",
                "type": "slider",
                "args": {"min_value": 0.0, "max_value": 5.0, "step": 0.1, "value": 1.0},
                "explanation": "锐化强度。1.0为默认锐化，越大边缘越突出。过大会产生明显的光晕伪影。",
            },
        ],
        "code": '''
import cv2
import numpy as np

def sharpening(image, strength=1.0):
    """图像锐化 - 使用拉普拉斯算子"""
    kernel = np.array([
        [0, -1, 0],
        [-1, 4 + strength, -1],
        [0, -1, 0]
    ], dtype=np.float32)
    return cv2.filter2D(image, -1, kernel)
''',
        "scenarios": [
            "📸 摄影后期：让照片细节更锐利",
            "🔍 文档处理：增强文字边缘清晰度",
            "🖨️ 打印准备：补偿打印过程中的细节丢失",
        ],
    },

    "unsharp_masking": {
        "name": "反锐化掩膜 (Unsharp Masking)",
        "category": "图像增强",
        "principle": """
### 算法原理

**反锐化掩膜 (USM)** 是专业图像处理中最常用的锐化技术，名字来源于传统暗房技术。

**处理流程：**
1. **模糊原图：** 对原图进行高斯模糊 → 得到"模糊图层"
2. **提取细节：** 原图 - 模糊图层 = 细节层（掩膜）
3. **增强锐化：** 原图 + strength × 细节层 = 锐化结果

**参数影响：**
- **sigma（模糊半径）：** 控制被增强的细节尺度
  - 小sigma → 增强细小纹理
  - 大sigma → 增强大尺度轮廓
- **strength（强度）：** 控制增强幅度

**与拉普拉斯锐化的区别：** USM通过sigma参数可以控制锐化的"尺度"，更加灵活精确
""",
        "params": [
            {
                "name": "sigma",
                "label": "模糊半径 σ",
                "type": "slider",
                "args": {"min_value": 0.3, "max_value": 10.0, "step": 0.1, "value": 1.0},
                "explanation": "高斯模糊的标准差，决定增强细节的尺度。小值增强细纹理，大值增强大轮廓。",
            },
            {
                "name": "strength",
                "label": "锐化强度",
                "type": "slider",
                "args": {"min_value": 0.1, "max_value": 5.0, "step": 0.1, "value": 1.0},
                "explanation": "锐化增强的倍数。越大效果越强，0.5-1.5是常用范围。",
            },
        ],
        "code": '''
import cv2

def unsharp_masking(image, sigma=1.0, strength=1.0):
    """反锐化掩膜 - 专业级图像锐化"""
    blurred = cv2.GaussianBlur(image, (0, 0), sigma)
    result = cv2.addWeighted(
        image, 1.0 + strength,
        blurred, -strength, 0
    )
    return result
''',
        "scenarios": [
            "🖼️ 专业摄影：Photoshop中USM锐化的核心算法",
            "🎬 视频后期：提升画面清晰度",
            "📱 手机美颜：适度锐化而不产生过度锐化感",
        ],
    },

    # ==================== 边缘检测 ====================
    "canny_edge": {
        "name": "Canny边缘检测",
        "category": "边缘检测",
        "principle": """
### 算法原理

**Canny边缘检测**由John F. Canny于1986年提出，被视为边缘检测的**黄金标准**。它是一个多阶段算法，精心设计以实现最优边缘检测。

**四步流程：**

**① 高斯滤波降噪**
- 使用高斯滤波器平滑图像
- 减少噪声对梯度计算的影响

**② 计算梯度幅值和方向**
- 使用Sobel算子计算Gx和Gy
- 幅值：$|G| = \\sqrt{G_x^2 + G_y^2}$
- 方向：$\\theta = \\arctan(G_y / G_x)$

**③ 非极大值抑制 (NMS)**
- 沿梯度方向，只保留局部最大值
- 使粗边缘变为单像素宽的细边缘

**④ 双阈值检测与边缘连接**
- 高阈值 → 强边缘（确定为边缘）
- 低阈值 → 弱边缘（仅在连接强边缘时保留）
- 这使边缘连续而不过多噪声
""",
        "params": [
            {
                "name": "threshold1",
                "label": "低阈值",
                "type": "slider",
                "args": {"min_value": 0, "max_value": 255, "step": 1, "value": 50},
                "explanation": "弱边缘检测阈值。低于此值的不是边缘。影响边缘的连续性和噪声数量。",
            },
            {
                "name": "threshold2",
                "label": "高阈值",
                "type": "slider",
                "args": {"min_value": 0, "max_value": 255, "step": 1, "value": 150},
                "explanation": "强边缘检测阈值。高于此值的一定是边缘。通常设为低阈值的2-3倍。",
            },
        ],
        "code": '''
import cv2

def canny_edge(image, threshold1=50, threshold2=150):
    """Canny边缘检测"""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, threshold1, threshold2)
    return edges
''',
        "scenarios": [
            "🚗 自动驾驶：车道线检测、障碍物识别",
            "🤖 工业视觉：零件尺寸测量、缺陷检测",
            "📱 文档扫描：边缘检测用于自动裁剪",
            "🔬 生物图像：细胞边界检测",
        ],
    },

    "sobel_edge": {
        "name": "Sobel边缘检测",
        "category": "边缘检测",
        "principle": """
### 算法原理

**Sobel算子**是一种离散的一阶微分算子，用于近似计算图像的梯度。

**两个3×3核：**
```
Gx (检测垂直边缘):     Gy (检测水平边缘):
[-1  0  +1]            [-1 -1 -1]
[-2  0  +2]            [ 0  0  0]
[-1  0  +1]            [+1 +1 +1]
```

**设计理念：**
- 中心列/行权重为0（不做贡献）
- 离中心越近权重越大（-2/+2 vs -1/+1）
- 同时对噪声有一定的平滑效果

**梯度计算：**
- X方向梯度：检测垂直边缘（左右亮度变化）
- Y方向梯度：检测水平边缘（上下亮度变化）
- 总梯度：$|G| = \\sqrt{G_x^2 + G_y^2}$
""",
        "params": [
            {
                "name": "ksize",
                "label": "核大小",
                "type": "select_slider",
                "args": {"options": [3, 5, 7], "value": 3},
                "explanation": "Sobel核的大小。越大的核覆盖范围越广，对噪声越不敏感，但边缘定位精度降低。",
            },
            {
                "name": "dx",
                "label": "X方向导数",
                "type": "radio",
                "args": {"options": [0, 1], "value": 1, "format_func": lambda x: "计算" if x else "忽略"},
                "explanation": "是否计算X方向梯度（检测垂直边缘）。",
            },
            {
                "name": "dy",
                "label": "Y方向导数",
                "type": "radio",
                "args": {"options": [0, 1], "value": 1, "format_func": lambda x: "计算" if x else "忽略"},
                "explanation": "是否计算Y方向梯度（检测水平边缘）。",
            },
        ],
        "code": '''
import cv2

def sobel_edge(image, ksize=3):
    """Sobel边缘检测"""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    grad_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=ksize)
    grad_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=ksize)
    abs_x = cv2.convertScaleAbs(grad_x)
    abs_y = cv2.convertScaleAbs(grad_y)
    return cv2.addWeighted(abs_x, 0.5, abs_y, 0.5, 0)
''',
        "scenarios": [
            "🎨 图像分析：提取纹理特征",
            "🔍 缺陷检测：检测产品表面裂纹和划痕",
            "📊 特征提取：作为HOG等高级特征的子步骤",
        ],
    },

    "laplacian_edge": {
        "name": "Laplacian边缘检测",
        "category": "边缘检测",
        "principle": """
### 算法原理

**Laplacian算子**是一个**二阶导数**边缘检测器。

**与一阶导数的区别：**
- 一阶导数（Sobel）：边缘处梯度取极大值
- 二阶导数（Laplacian）：边缘处过零点 → 更精确的定位

**Laplacian核（4邻域）：**
```
[ 0  1  0]
[ 1 -4  1]
[ 0  1  0]
```

**核心特性：**
- 对噪声极其敏感（二阶导数放大噪声）
- 通常需要先进行高斯平滑（LoG：Laplacian of Gaussian）
- 边缘位置在过零点处，定位更精确
- 各向同性（对旋转不敏感）
""",
        "params": [
            {
                "name": "ksize",
                "label": "核大小",
                "type": "select_slider",
                "args": {"options": [1, 3, 5, 7], "value": 3},
                "explanation": "Laplacian核大小。1使用最小核，越大使用更宽的计算孔径。",
            },
        ],
        "code": '''
import cv2

def laplacian_edge(image, ksize=3):
    """Laplacian边缘检测"""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    lap = cv2.Laplacian(gray, cv2.CV_64F, ksize=ksize)
    return cv2.convertScaleAbs(lap)
''',
        "scenarios": [
            "🔬 精密检测：需要精确边缘定位的应用",
            "📐 计量学：精确测量物体尺寸",
        ],
    },

    "scharr_edge": {
        "name": "Scharr边缘检测",
        "category": "边缘检测",
        "principle": """
### 算法原理

**Scharr算子**是Sobel算子的改进版，使用优化的3×3核，对旋转对称性更好。

**Scharr核：**
```
Gx:                   Gy:
[-3   0  +3]          [-3  -10  -3]
[-10  0  +10]         [ 0    0   0]
[-3   0  +3]          [+3  +10  +3]
```

**与Sobel的区别：**
- Scharr核权重更大（3、10）vs Sobel（1、2）
- 对45°方向的边缘响应更均匀
- 精度比3×3 Sobel更高
- 仅支持3×3核
""",
        "params": [
            {
                "name": "dx",
                "label": "X方向",
                "type": "radio",
                "args": {"options": [1, 0], "value": 1, "format_func": lambda x: "计算" if x else "忽略"},
                "explanation": "检测垂直边缘。",
            },
            {
                "name": "dy",
                "label": "Y方向",
                "type": "radio",
                "args": {"options": [0, 1], "value": 0, "format_func": lambda x: "计算" if x else "忽略"},
                "explanation": "检测水平边缘。",
            },
        ],
        "code": '''
import cv2

def scharr_edge(image):
    """Scharr边缘检测"""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    grad_x = cv2.Scharr(gray, cv2.CV_64F, 1, 0)
    grad_y = cv2.Scharr(gray, cv2.CV_64F, 0, 1)
    abs_x = cv2.convertScaleAbs(grad_x)
    abs_y = cv2.convertScaleAbs(grad_y)
    return cv2.addWeighted(abs_x, 0.5, abs_y, 0.5, 0)
''',
        "scenarios": [
            "🎯 高精度检测：需要更精确梯度测量的场合",
            "🔍 细小特征：检测细小纹理和细微边缘",
        ],
    },

    "prewitt_edge": {
        "name": "Prewitt边缘检测",
        "category": "边缘检测",
        "principle": """
### 算法原理

**Prewitt算子**是Sobel算子的前身，也使用3×3核进行梯度计算。

**Prewitt核：**
```
Gx:                   Gy:
[-1  0  +1]           [-1 -1 -1]
[-1  0  +1]           [ 0  0  0]
[-1  0  +1]           [+1 +1 +1]
```

**与Sobel的区别：**
- Prewitt没有强调中心像素权重
- 计算更简单（所有权重为1）
- 对噪声的抑制不如Sobel
- 是历史上较早提出的算子
""",
        "params": [],
        "code": '''
import cv2
import numpy as np

def prewitt_edge(image):
    """Prewitt边缘检测"""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    kernel_x = np.array([[-1,0,1],[-1,0,1],[-1,0,1]])
    kernel_y = np.array([[-1,-1,-1],[0,0,0],[1,1,1]])
    grad_x = cv2.filter2D(gray, cv2.CV_64F, kernel_x)
    grad_y = cv2.filter2D(gray, cv2.CV_64F, kernel_y)
    abs_x = cv2.convertScaleAbs(grad_x)
    abs_y = cv2.convertScaleAbs(grad_y)
    return cv2.addWeighted(abs_x, 0.5, abs_y, 0.5, 0)
''',
        "scenarios": [
            "📚 教学演示：理解一阶导数边缘检测的基本原理",
            "⚡ 简单场景：对噪声较少的图像快速检测",
        ],
    },

    # ==================== 形态学操作 ====================
    "erosion": {
        "name": "腐蚀 (Erosion)",
        "category": "形态学操作",
        "principle": """
### 算法原理

**腐蚀**是形态学中最基本的操作之一，用结构元素"侵蚀"前景物体的边界。

**工作方式：**
1. 结构元素（小窗口）在图像上滑动
2. 只有当结构元素**完全**覆盖前景像素时，锚点才设为前景
3. 否则设为背景

**直观理解：** 像橡皮擦一样，从物体边界擦除一层像素

**效果：**
- 缩小白色（前景）区域
- 消除比结构元素小的物体
- 断开物体间的纤细连接
- 扩大黑色（背景）区域
""",
        "params": [
            {
                "name": "ksize",
                "label": "结构元素大小",
                "type": "slider",
                "args": {"min_value": 1, "max_value": 21, "step": 2, "value": 5},
                "explanation": "结构元素（核）的大小。越大腐蚀效果越强，会消除更大的物体。",
            },
            {
                "name": "iterations",
                "label": "迭代次数",
                "type": "slider",
                "args": {"min_value": 1, "max_value": 10, "step": 1, "value": 1},
                "explanation": "重复腐蚀的次数。多次腐蚀=使用更大结构元素的效果。",
            },
        ],
        "code": '''
import cv2

def erosion(image, ksize=5, iterations=1):
    """腐蚀操作"""
    kernel = cv2.getStructuringElement(
        cv2.MORPH_RECT, (ksize, ksize)
    )
    return cv2.erode(image, kernel, iterations=iterations)
''',
        "scenarios": [
            "✂️ 物体分离：断开连在一起的物体",
            "🧹 噪声去除：消除小于结构元素的白噪声",
            "📏 边界收缩：缩小物体以消除边界影响",
        ],
    },

    "dilation": {
        "name": "膨胀 (Dilation)",
        "category": "形态学操作",
        "principle": """
### 算法原理

**膨胀**是腐蚀的对偶操作，用结构元素"扩展"前景物体的边界。

**工作方式：**
1. 结构元素在图像上滑动
2. 只要结构元素与前景像素**有交集**，锚点就设为前景
3. 只有完全在背景内才设为背景

**直观理解：** 像刷子一样，沿物体边界画上一圈前景像素

**效果：**
- 扩大白色（前景）区域
- 填充物体内部的小空洞
- 连接邻近的物体
- 桥接裂缝
""",
        "params": [
            {
                "name": "ksize",
                "label": "结构元素大小",
                "type": "slider",
                "args": {"min_value": 1, "max_value": 21, "step": 2, "value": 5},
                "explanation": "结构元素的大小。越大膨胀效果越强。",
            },
            {
                "name": "iterations",
                "label": "迭代次数",
                "type": "slider",
                "args": {"min_value": 1, "max_value": 10, "step": 1, "value": 1},
                "explanation": "重复膨胀的次数。",
            },
        ],
        "code": '''
import cv2

def dilation(image, ksize=5, iterations=1):
    """膨胀操作"""
    kernel = cv2.getStructuringElement(
        cv2.MORPH_RECT, (ksize, ksize)
    )
    return cv2.dilate(image, kernel, iterations=iterations)
''',
        "scenarios": [
            "🔗 物体连接：将断裂的文字笔画连接起来",
            "🕳️ 孔洞填充：填补物体内部的小孔洞",
            "📐 边界扩展：扩大ROI区域",
        ],
    },

    "opening": {
        "name": "开运算 (Opening)",
        "category": "形态学操作",
        "principle": """
### 算法原理

**开运算** = **先腐蚀后膨胀**，使用相同的结构元素。

**执行过程：**
1. 腐蚀：去除小物体、断开连接、消除噪声
2. 膨胀：恢复被腐蚀物体的大小

**关键特性：**
- 能够去除比结构元素小的亮点/噪声
- 能够断开纤细的连接
- **保持主要物体的大小基本不变**（这是与单独腐蚀的区别）
- 平滑物体轮廓

**类比：** 先"削"掉突出的部分，再"补"回大的区域
""",
        "params": [
            {
                "name": "ksize",
                "label": "结构元素大小",
                "type": "slider",
                "args": {"min_value": 1, "max_value": 21, "step": 2, "value": 5},
                "explanation": "决定被去除的噪声/连接的最大尺寸。应大于要消除的噪声，小于要保留的物体。",
            },
        ],
        "code": '''
import cv2

def opening(image, ksize=5):
    """开运算 = 先腐蚀后膨胀"""
    kernel = cv2.getStructuringElement(
        cv2.MORPH_RECT, (ksize, ksize)
    )
    return cv2.morphologyEx(
        image, cv2.MORPH_OPEN, kernel
    )
''',
        "scenarios": [
            "🧹 去噪：去除二值图像中的小噪点",
            "🔗 分离计数：断开黏连的物体以便逐个计数",
            "📄 OCR预处理：清理文字识别前的噪声",
        ],
    },

    "closing": {
        "name": "闭运算 (Closing)",
        "category": "形态学操作",
        "principle": """
### 算法原理

**闭运算** = **先膨胀后腐蚀**，使用相同的结构元素。

**执行过程：**
1. 膨胀：填充物体内的小空洞、连接邻近区域
2. 腐蚀：恢复膨胀后的物体大小

**关键特性：**
- 能够填充比结构元素小的黑洞/缝隙
- 能够连接邻近的物体
- **保持主要物体的大小基本不变**
- 平滑物体轮廓（填充凹角）

**类比：** 先"填"坑，再"修"回原来的边界
""",
        "params": [
            {
                "name": "ksize",
                "label": "结构元素大小",
                "type": "slider",
                "args": {"min_value": 1, "max_value": 21, "step": 2, "value": 5},
                "explanation": "决定被填充的空洞/缝隙的最大尺寸。应大于要填充的空洞。",
            },
        ],
        "code": '''
import cv2

def closing(image, ksize=5):
    """闭运算 = 先膨胀后腐蚀"""
    kernel = cv2.getStructuringElement(
        cv2.MORPH_RECT, (ksize, ksize)
    )
    return cv2.morphologyEx(
        image, cv2.MORPH_CLOSE, kernel
    )
''',
        "scenarios": [
            "🕳️ 孔洞填充：填充文字或物体中的小孔洞",
            "🔗 断线连接：连接虚线或断开的轮廓",
            "🧩 区域合并：合并接近的连通区域",
        ],
    },

    "morphological_gradient": {
        "name": "形态学梯度",
        "category": "形态学操作",
        "principle": """
### 算法原理

**形态学梯度** = **膨胀 - 腐蚀**

**直观理解：**
- 膨胀使物体边界向外扩展
- 腐蚀使物体边界向内收缩
- 两者之差 = 物体的一圈边界轮廓

**为什么能检测边缘？**
- 非边缘区域：膨胀和腐蚀的值相同 → 差值为0（黑色）
- 边缘区域：膨胀值 > 腐蚀值 → 差值为正（亮色）

**特点：**
- 得到的边界比传统边缘检测（Canny等）更粗
- 边界粗细由结构元素大小控制
- 对噪声不如Canny敏感
""",
        "params": [
            {
                "name": "ksize",
                "label": "结构元素大小",
                "type": "slider",
                "args": {"min_value": 1, "max_value": 15, "step": 2, "value": 3},
                "explanation": "结构元素大小决定边界的粗细。越大边界越粗。",
            },
        ],
        "code": '''
import cv2

def morphological_gradient(image, ksize=3):
    """形态学梯度 = 膨胀 - 腐蚀"""
    kernel = cv2.getStructuringElement(
        cv2.MORPH_RECT, (ksize, ksize)
    )
    return cv2.morphologyEx(
        image, cv2.MORPH_GRADIENT, kernel
    )
''',
        "scenarios": [
            "📐 边界提取：获取物体的外轮廓",
            "🔍 缺陷检测：检测物体表面的不规则边缘",
        ],
    },

    "top_hat": {
        "name": "顶帽变换 (Top Hat)",
        "category": "形态学操作",
        "principle": """
### 算法原理

**顶帽变换** = **原图 - 开运算结果**

**开运算**去除了比结构元素小的亮特征 → 顶帽提取了这些被去除的亮特征。

**直观理解：**
- 开运算像一把"抹刀"，抹平了比核小的亮突起
- 从原图减去"抹平"的结果 → 只留下被抹掉的亮突起

**适用场景：** 在光照不均匀的背景上提取亮的细小特征
""",
        "params": [
            {
                "name": "ksize",
                "label": "结构元素大小",
                "type": "slider",
                "args": {"min_value": 3, "max_value": 51, "step": 2, "value": 9},
                "explanation": "应设置为大于要提取的目标特征，小于特征之间的间距。",
            },
        ],
        "code": '''
import cv2

def top_hat(image, ksize=9):
    """顶帽变换 = 原图 - 开运算"""
    kernel = cv2.getStructuringElement(
        cv2.MORPH_RECT, (ksize, ksize)
    )
    return cv2.morphologyEx(
        image, cv2.MORPH_TOPHAT, kernel
    )
''',
        "scenarios": [
            "🔬 细胞计数：在不均匀光照下分离细胞",
            "🌌 天文图像：检测星点",
            "🏭 缺陷检测：检测表面上的异常亮点",
        ],
    },

    "black_hat": {
        "name": "黑帽变换 (Black Hat)",
        "category": "形态学操作",
        "principle": """
### 算法原理

**黑帽变换** = **闭运算结果 - 原图**

**闭运算**填充了比结构元素小的暗特征 → 黑帽提取了这些被填充的暗特征。

**直观理解：**
- 闭运算像一把"填缝刀"，填平了比核小的暗凹陷
- 从闭运算结果减去原图 → 只留下被填掉的暗凹陷

**适用场景：** 在光照不均匀的背景上提取暗的细小特征
""",
        "params": [
            {
                "name": "ksize",
                "label": "结构元素大小",
                "type": "slider",
                "args": {"min_value": 3, "max_value": 51, "step": 2, "value": 9},
                "explanation": "应设置为大于要提取的暗特征，小于特征之间的间距。",
            },
        ],
        "code": '''
import cv2

def black_hat(image, ksize=9):
    """黑帽变换 = 闭运算 - 原图"""
    kernel = cv2.getStructuringElement(
        cv2.MORPH_RECT, (ksize, ksize)
    )
    return cv2.morphologyEx(
        image, cv2.MORPH_BLACKHAT, kernel
    )
''',
        "scenarios": [
            "🔍 裂纹检测：检测材料表面的暗色裂纹",
            "🩸 血管检测：检测视网膜图像中的暗色血管",
        ],
    },

    # ==================== 阈值分割 ====================
    "global_threshold": {
        "name": "全局阈值分割",
        "category": "阈值分割",
        "principle": """
### 算法原理

**全局阈值分割**是最简单的图像分割方法，使用一个固定的阈值将图像分为前景和背景。

**公式：**
$$\\text{dst}(x,y) = \\begin{cases} \\text{maxval} & \\text{if } \\text{src}(x,y) > \\text{thresh} \\\\ 0 & \\text{otherwise} \\end{cases}$$

**关键：** 阈值的选取直接影响分割效果
- 阈值太低 → 太多背景被误判为前景
- 阈值太高 → 前景物体丢失

**局限性：** 对光照不均匀的图像效果很差
""",
        "params": [
            {
                "name": "thresh",
                "label": "阈值",
                "type": "slider",
                "args": {"min_value": 0, "max_value": 255, "step": 1, "value": 127},
                "explanation": "分类阈值。大于此值的像素置为maxval，小于等于此值的置为0。",
            },
            {
                "name": "maxval",
                "label": "最大值",
                "type": "slider",
                "args": {"min_value": 1, "max_value": 255, "step": 1, "value": 255},
                "explanation": "前景像素的值，通常设为255（白色）。",
            },
        ],
        "code": '''
import cv2

def global_threshold(image, thresh=127, maxval=255):
    """全局阈值分割"""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(
        gray, thresh, maxval, cv2.THRESH_BINARY
    )
    return binary
''',
        "scenarios": [
            "📄 文档二值化：均匀光照下的文字提取",
            "🔲 简单目标检测：高对比度的物体分割",
        ],
    },

    "adaptive_threshold": {
        "name": "自适应阈值分割",
        "category": "阈值分割",
        "principle": """
### 算法原理

**自适应阈值**为每个像素动态计算局部阈值，解决了全局阈值在光照不均匀时失效的问题。

**工作方式：**
1. 对每个像素，取其 block_size × block_size 邻域
2. 计算邻域内像素的**加权平均值**（高斯加权或算术平均）
3. 局部阈值 = 平均值 - 常数C
4. 像素值 > 局部阈值 → 前景，否则 → 背景

**参数影响：**
- **block_size：** 越大，阈值变化越平滑，但可能丢失局部细节
- **C：** 从均值减去的常数。C越大阈值越低，更多像素被判为前景（更亮）
""",
        "params": [
            {
                "name": "block_size",
                "label": "邻域大小",
                "type": "slider",
                "args": {"min_value": 3, "max_value": 101, "step": 2, "value": 11},
                "explanation": "计算局部阈值的邻域大小。必须是奇数。小值适应局部变化，大值更平滑。",
            },
            {
                "name": "c",
                "label": "常数 C",
                "type": "slider",
                "args": {"min_value": -10, "max_value": 30, "step": 1, "value": 2},
                "explanation": "从局部均值中减去的常数。C越小阈值越高（更暗），C越大阈值越低（更多像素为前景）。",
            },
        ],
        "code": '''
import cv2

def adaptive_threshold(image, block_size=11, C=2):
    """自适应阈值分割"""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return cv2.adaptiveThreshold(
        gray, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        block_size, C
    )
''',
        "scenarios": [
            "📷 非均匀光照：拍摄光照不均匀的文档",
            "🖼️ 阴影处理：有阴影场景下的目标提取",
            "📱 手机扫描：手机拍摄的文档二值化",
        ],
    },

    "otsu_threshold": {
        "name": "Otsu二值化",
        "category": "阈值分割",
        "principle": """
### 算法原理

**Otsu二值化**（大津法）由日本学者大津展之于1979年提出，能**自动计算最优阈值**。

**核心思想：最大化类间方差**

1. **类内方差：** 同一类（前景或背景）内部像素的离散程度
2. **类间方差：** 前景类和背景类之间的分离程度
3. **Otsu准则：** 最优阈值 = 使类间方差最大的阈值

**数学表示：**
$$\\sigma^2_B(t) = \\omega_0(t)\\omega_1(t)[\\mu_0(t) - \\mu_1(t)]^2$$
其中 $\\omega_0$、$\\omega_1$ 是两类的像素比例，$\\mu_0$、$\\mu_1$ 是两类的均值

**前提条件：** 图像直方图具有双峰结构（bimodal），即前景和背景的亮度有明显差异
""",
        "params": [],
        "code": '''
import cv2

def otsu_threshold(image):
    """Otsu自动二值化"""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(
        gray, 0, 255,
        cv2.THRESH_BINARY + cv2.THRESH_OTSU
    )
    return binary
''',
        "scenarios": [
            "🤖 自动二值化：无需手动指定阈值的场景",
            "📄 文档分析：自动分离文字和背景",
            "🔬 细胞图像：自动分割细胞和背景",
            "📦 二维码检测：快速二值化以检测QR码",
        ],
    },

    # ==================== 图像变换 ====================
    "resize_scale": {
        "name": "图像缩放",
        "category": "图像变换",
        "principle": """
### 算法原理

**图像缩放**通过插值算法改变图像分辨率。

**常用插值方法：**
- **最近邻 (INTER_NEAREST)：** 取最近像素值，最快但质量最差，有锯齿
- **双线性 (INTER_LINEAR)：** 2×2邻域线性插值，速度与质量平衡
- **双三次 (INTER_CUBIC)：** 4×4邻域三次插值，质量好但较慢
- **Lanczos (INTER_LANCZOS4)：** 8×8邻域，最高质量

**缩小 (scale<1)：** 使用INTER_AREA效果最好（抗锯齿）
**放大 (scale>1)：** 使用INTER_CUBIC或INTER_LANCZOS4质量更好
""",
        "params": [
            {
                "name": "scale",
                "label": "缩放比例",
                "type": "slider",
                "args": {"min_value": 0.1, "max_value": 3.0, "step": 0.05, "value": 0.5},
                "explanation": "缩放因子。0.5=缩小为一半，1.0=不变，2.0=放大两倍。",
            },
        ],
        "code": '''
import cv2

def resize_scale(image, scale=0.5):
    """图像缩放"""
    h, w = image.shape[:2]
    new_w, new_h = int(w * scale), int(h * scale)
    return cv2.resize(
        image, (new_w, new_h),
        interpolation=cv2.INTER_CUBIC
    )
''',
        "scenarios": [
            "🖼️ 缩略图生成：创建图像预览",
            "🤖 深度学习：调整输入图像到模型要求尺寸",
            "🌐 网页优化：创建不同分辨率的图像版本",
        ],
    },

    "rotation": {
        "name": "图像旋转",
        "category": "图像变换",
        "principle": """
### 算法原理

**图像旋转**将图像绕指定中心点旋转指定角度。

**变换矩阵：**
$$M = \\begin{bmatrix} \\cos\\theta & -\\sin\\theta & (1-\\cos\\theta)c_x + \\sin\\theta \\cdot c_y \\\\ \\sin\\theta & \\cos\\theta & (1-\\cos\\theta)c_y - \\sin\\theta \\cdot c_x \\end{bmatrix}$$

其中 $(c_x, c_y)$ 是旋转中心，$\\theta$ 是旋转角度（逆时针为正）

**注意事项：**
- 旋转后图像可能超出原画布范围
- 默认填充黑色（可修改borderMode）
- 大角度旋转时画布需要扩大以避免裁剪
""",
        "params": [
            {
                "name": "angle",
                "label": "旋转角度 (°)",
                "type": "slider",
                "args": {"min_value": -180, "max_value": 180, "step": 1, "value": 0},
                "explanation": "绕图像中心旋转的角度。正值为逆时针，负值为顺时针。",
            },
            {
                "name": "scale",
                "label": "缩放比例",
                "type": "slider",
                "args": {"min_value": 0.1, "max_value": 2.0, "step": 0.05, "value": 1.0},
                "explanation": "旋转的同时进行缩放。1.0保持原尺寸。",
            },
        ],
        "code": '''
import cv2

def rotation(image, angle=0, scale=1.0):
    """图像旋转"""
    h, w = image.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, scale)
    return cv2.warpAffine(image, M, (w, h))
''',
        "scenarios": [
            "📐 图像矫正：纠正拍摄倾斜的图像",
            "🔍 数据增强：为深度学习生成训练变体",
        ],
    },

    "affine_transform": {
        "name": "仿射变换",
        "category": "图像变换",
        "principle": """
### 算法原理

**仿射变换**是线性变换（旋转、缩放、错切）与平移的组合。

**性质：**
- 保持"直线性"：直线变换后仍是直线
- 保持"平行性"：平行线变换后仍然平行
- 不保持角度和长度

**变换矩阵（2×3）：**
$$M = \\begin{bmatrix} a_{11} & a_{12} & t_x \\\\ a_{21} & a_{22} & t_y \\end{bmatrix}$$

前三列定义旋转+缩放+错切，最后一列定义平移

**与透视变换的区别：** 仿射变换保持平行性，透视变换不保持
""",
        "params": [
            {
                "name": "angle",
                "label": "旋转角度 (°)",
                "type": "slider",
                "args": {"min_value": -180, "max_value": 180, "step": 1, "value": 0},
                "explanation": "图像绕中心旋转的角度。",
            },
            {
                "name": "scale",
                "label": "缩放比例",
                "type": "slider",
                "args": {"min_value": 0.1, "max_value": 2.0, "step": 0.05, "value": 1.0},
                "explanation": "各向同性的缩放因子。",
            },
            {
                "name": "tx",
                "label": "X平移 (px)",
                "type": "slider",
                "args": {"min_value": -200, "max_value": 200, "step": 1, "value": 0},
                "explanation": "水平方向平移量。正值向右移动，负值向左移动。",
            },
            {
                "name": "ty",
                "label": "Y平移 (px)",
                "type": "slider",
                "args": {"min_value": -200, "max_value": 200, "step": 1, "value": 0},
                "explanation": "垂直方向平移量。正值向下移动，负值向上移动。",
            },
        ],
        "code": '''
import cv2
import numpy as np

def affine_transform(image, angle=0, scale=1.0,
                     tx=0, ty=0):
    """仿射变换"""
    h, w = image.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, scale)
    M[0, 2] += tx  # X平移
    M[1, 2] += ty  # Y平移
    return cv2.warpAffine(image, M, (w, h))
''',
        "scenarios": [
            "🧩 图像配准：将不同图像对齐到同一坐标系",
            "🔄 几何校正：校正拍摄角度造成的几何变形",
            "🔀 图像拼接：多张图像拼接时的对齐操作",
        ],
    },

    "fourier_transform": {
        "name": "傅里叶变换",
        "category": "图像变换",
        "principle": """
### 算法原理

**傅里叶变换**将图像从**空间域**（像素位置）转换到**频率域**（频率成分）。

**核心思想（傅里叶定理）：**
任何信号（包括图像）都可以表示为不同频率、不同振幅的正弦波的叠加。

**频率域的含义：**
- **低频成分：** 图像中变化缓慢的部分
  - 平滑区域、渐变、整体亮度 → 聚集在频谱中心
- **高频成分：** 图像中变化剧烈的部分
  - 边缘、纹理、噪声 → 分布在频谱边缘

**幅度谱：** 每个频率成分的强度
**相位谱：** 每个频率成分的相位偏移

**应用思路：** 在频率域对特定频率进行处理 → 逆变换回空间域

**为什么用对数显示？** 低频幅度通常远大于高频，log变换使两者都可见
""",
        "params": [],
        "code": '''
import cv2
import numpy as np

def fourier_transform(image):
    """傅里叶变换 - 频率域可视化"""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    dft = cv2.dft(np.float32(gray),
                   flags=cv2.DFT_COMPLEX_OUTPUT)
    dft_shift = np.fft.fftshift(dft)
    magnitude = cv2.magnitude(
        dft_shift[:,:,0], dft_shift[:,:,1])
    return np.log(1 + magnitude)  # 对数尺度
''',
        "scenarios": [
            "🔍 频域滤波：低通去噪、高通锐化、带通纹理分析",
            "👁️ 图像压缩：JPEG压缩基于DCT（傅里叶相关变换）",
            "📡 信号处理：图像去模糊、去卷积",
            "🔬 纹理分析：通过频谱特征识别纹理模式",
        ],
    },

    "fourier_lowpass": {
        "name": "傅里叶低通滤波 (Fourier Low-Pass)",
        "category": "图像变换",
        "principle": """
### 算法原理

**傅里叶低通滤波**在频率域中保留低频成分、滤除高频成分，从而实现图像平滑去噪。

**核心步骤：**
1. 对原图做傅里叶变换，得到频谱（零频移至中心）
2. 构造一个以频谱中心为圆心的圆形掩膜，半径内为 1（保留），半径外为 0（滤除）
3. 频谱 × 掩膜 → 只保留中心低频区域
4. 逆傅里叶变换回到空间域

**参数含义：**
- `cutoff_ratio`：截止半径占图像短边的比例
  - 值越小，保留的频率越少 → 图像越模糊（强平滑）
  - 值越大，保留的频率越多 → 图像越接近原图

**与高斯滤波的关系：** 理想低通在频域是矩形掩膜，会产生振铃效应；
高斯低通在频域也是高斯形，无振铃但平滑更柔和。
""",
        "params": [
            {
                "name": "cutoff_ratio",
                "label": "截止频率比例",
                "type": "slider",
                "args": {"min_value": 0.01, "max_value": 0.5, "step": 0.01, "value": 0.1},
                "explanation": "截止半径占图像短边的比例。越小平滑越强；越大越接近原图。",
            },
        ],
        "code": '''
import cv2
import numpy as np

def fourier_lowpass(image, cutoff_ratio=0.1):
    """傅里叶低通滤波"""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    h, w = gray.shape
    # 傅里叶变换
    dft = cv2.dft(np.float32(gray), flags=cv2.DFT_COMPLEX_OUTPUT)
    dft_shift = np.fft.fftshift(dft)
    # 低通掩膜
    mask = np.zeros((h, w, 2), np.float32)
    radius = int(min(h, w) * cutoff_ratio)
    cv2.circle(mask, (w // 2, h // 2), radius, (1, 1), -1)
    # 滤波 + 逆变换
    dft_filtered = dft_shift * mask
    img_back = cv2.idft(np.fft.ifftshift(dft_filtered))
    return cv2.magnitude(img_back[:, :, 0], img_back[:, :, 1])
''',
        "scenarios": [
            "🧹 图像去噪：滤除高频噪声，保留主体结构",
            "🎨 艺术效果：模拟柔焦、梦幻模糊",
            "📉 数据降采样前的抗混叠预处理",
            "🔬 医学图像：平滑CT/MRI中的高频噪声",
        ],
    },

    "fourier_highpass": {
        "name": "傅里叶高通滤波 (Fourier High-Pass)",
        "category": "图像变换",
        "principle": """
### 算法原理

**傅里叶高通滤波**在频率域中滤除低频成分、保留高频成分，从而提取图像的边缘和细节。

**核心步骤：**
1. 对原图做傅里叶变换，得到频谱（零频移至中心）
2. 构造掩膜：中心圆形区域为 0（滤除低频），其余为 1（保留高频）
3. 频谱 × 掩膜 → 去除直流分量与缓慢变化部分
4. 逆傅里叶变换回到空间域

**参数含义：**
- `cutoff_ratio`：中心被滤除区域的半径比例
  - 值越小，滤除的低频越少 → 保留更多整体信息
  - 值越大，滤除的低频越多 → 边缘/纹理越突出，但可能丢失主体

**效果：** 输出图像以边缘和纹理为主，整体亮度被去除（因为直流分量被滤除）。
""",
        "params": [
            {
                "name": "cutoff_ratio",
                "label": "截止频率比例",
                "type": "slider",
                "args": {"min_value": 0.01, "max_value": 0.5, "step": 0.01, "value": 0.1},
                "explanation": "中心被滤除的低频区域半径比例。越大边缘提取越激进。",
            },
        ],
        "code": '''
import cv2
import numpy as np

def fourier_highpass(image, cutoff_ratio=0.1):
    """傅里叶高通滤波"""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    h, w = gray.shape
    dft = cv2.dft(np.float32(gray), flags=cv2.DFT_COMPLEX_OUTPUT)
    dft_shift = np.fft.fftshift(dft)
    # 高通掩膜（中心置0）
    mask = np.ones((h, w, 2), np.float32)
    radius = int(min(h, w) * cutoff_ratio)
    cv2.circle(mask, (w // 2, h // 2), radius, (0, 0), -1)
    dft_filtered = dft_shift * mask
    img_back = cv2.idft(np.fft.ifftshift(dft_filtered))
    return cv2.magnitude(img_back[:, :, 0], img_back[:, :, 1])
''',
        "scenarios": [
            "📐 边缘检测：提取图像中的高频边缘信息",
            "🔍 纹理增强：突出图像中的细节纹理",
            "🧠 特征提取：作为模式识别的预处理步骤",
            "🩺 医学影像：增强血管、纤维等细微结构",
        ],
    },

    # ==================== 深度学习 ====================
    "image_classification": {
        "name": "图像分类 (Image Classification)",
        "category": "深度学习",
        "principle": """
### 算法原理

**图像分类**是卷积神经网络最经典的应用，目标是判断图像所属的类别。本系统采用 **MobileNetV2**（在 ImageNet 1000 类上预训练）。

**与经典算法的区别：**
- 经典算法需要手工设计特征（如 HOG、SIFT），CNN 则**自动学习**特征；
- CNN 通过卷积层逐层提取特征：浅层检测边缘/纹理，深层编码语义概念；
- 最后的全连接层将特征映射为各类别的得分，经 Softmax 得到概率分布。

**MobileNetV2 的核心思想：**
- **深度可分离卷积**：将标准卷积分解为「逐通道卷积 + 1×1 逐点卷积」，大幅降低参数量与计算量；
- **倒残差结构**：先升维再降维，在保持精度的同时实现轻量化，适合 CPU 实时推理。
""",
        "params": [
            {
                "name": "top_k",
                "label": "显示类别数 Top-K",
                "type": "slider",
                "args": {"min_value": 1, "max_value": 5, "step": 1, "value": 3},
                "explanation": "展示置信度最高的 K 个类别及其概率。",
            },
        ],
        "code": '''
import torch
from torchvision import models, transforms

model = models.mobilenet_v2(weights="DEFAULT").eval()
preprocess = transforms.Compose([
    transforms.Resize(224),
    transforms.ToTensor(),
    transforms.Normalize([0.485,0.456,0.406],[0.229,0.224,0.225]),
])
with torch.no_grad():
    probs = torch.softmax(model(preprocess(img).unsqueeze(0))[0], dim=0)
''',
        "scenarios": [
            "🖼️ 相册自动归类：按内容自动整理照片",
            "🛡️ 内容审核：识别违规/敏感图像",
            "🚗 自动驾驶：识别道路上的交通标志",
            "🏥 医疗辅助：皮肤病变、病理切片初筛",
        ],
    },

    "semantic_segmentation": {
        "name": "语义分割 (Semantic Segmentation)",
        "category": "深度学习",
        "principle": """
### 算法原理

**语义分割**是像素级的分类任务，为图像中每个像素分配一个类别标签。本系统采用 **DeepLabV3**（MobileNetV3 骨干，COCO 数据集预训练）。

**与图像分类的对比：**
- 图像分类输出「整张图属于哪个类」；
- 语义分割输出「每个像素属于哪个类」，得到逐像素的分割掩码。

**DeepLabV3 的核心技术：**
- **空洞卷积**：在不增加参数、不降低分辨率的前提下扩大感受野；
- **ASPP（空洞空间金字塔池化）**：用多个不同膨胀率的卷积并行捕获多尺度上下文；
- 输出经上采样恢复到原图尺寸，得到逐像素类别图。
""",
        "params": [
            {
                "name": "opacity",
                "label": "掩码透明度",
                "type": "slider",
                "args": {"min_value": 0.0, "max_value": 1.0, "step": 0.1, "value": 0.5},
                "explanation": "控制分割掩码叠加在原图上的透明度，值越大掩码越不透明。",
            },
        ],
        "code": '''
import torch
from torchvision import models

model = models.deeplabv3_mobilenet_v3_large(weights="DEFAULT").eval()
with torch.no_grad():
    out = model(input_batch)["out"][0]      # (21, H, W)
mask = torch.argmax(out, dim=0)             # 逐像素取类别
''',
        "scenarios": [
            "🚗 自动驾驶：道路、车辆、行人像素级分割",
            "🏥 医学影像：肿瘤、器官区域的精确勾画",
            "🛰️ 遥感图像：土地类型、建筑物识别",
            "🛒 电商：商品抠图与背景替换",
        ],
    },

    "super_resolution": {
        "name": "图像超分辨率 (Super-Resolution)",
        "category": "深度学习",
        "principle": """
### 算法原理

**图像超分辨率**旨在从低分辨率图像重建出高分辨率细节。本系统采用经典的三层 **SRCNN**（需先运行 `python -m modules.training` 训练权重）。

**SRCNN 结构（Dong et al. 2014）：**
1. 第一层（9×9 卷积）：提取低分辨率图像的特征块；
2. 第二层（1×1 卷积）：将特征块非线性映射到高维表示；
3. 第三层（5×5 卷积）：将高维特征重建为高分辨率亮度。

**工作流程：**
- 将原图下采样得到低分辨率图像 LR；
- 用双三次插值将 LR 放大回原尺寸；
- SRCNN 对放大后的图像进行细节重建，输出更清晰的结果。
""",
        "params": [
            {
                "name": "scale",
                "label": "缩放倍数",
                "type": "selectbox",
                "args": {"options": [2, 3, 4], "value": 2},
                "explanation": "低分辨率相对原图的缩小倍数，SRCNN 学习将 LR 重建回原尺寸。",
            },
        ],
        "code": '''
import torch

class SRCNN(torch.nn.Module):
    def __init__(self):
        super().__init__()
        self.conv1 = torch.nn.Conv2d(1, 64, 9, padding=4)
        self.conv2 = torch.nn.Conv2d(64, 32, 1)
        self.conv3 = torch.nn.Conv2d(32, 1, 5, padding=2)
        self.relu = torch.nn.ReLU(inplace=True)
    def forward(self, x):
        x = self.relu(self.conv1(x))
        x = self.relu(self.conv2(x))
        return self.conv3(x)
''',
        "scenarios": [
            "🖼️ 老照片修复：提升老旧低分辨率照片清晰度",
            "📺 视频增强：将低清视频放大到高清",
            "🔬 医学影像：提高 MRI/CT 图像分辨率",
            "🛰️ 遥感影像：增强卫星图像细节",
        ],
    },

    "cifar10_classification": {
        "name": "CIFAR-10 分类 (自定义模型)",
        "category": "深度学习",
        "principle": """
### 算法原理

本算法使用**在 CIFAR-10 数据集上从零训练的小型卷积网络**（需先运行 `python -m modules.training` 训练权重），演示完整的深度学习训练流水线。

**CIFAR-10 数据集：**
- 10 个类别：飞机、汽车、鸟、猫、鹿、狗、青蛙、马、船、卡车；
- 每类 6000 张 32×32 彩色图像，共 60000 张。

**网络结构（CIFAR10Net）：**
- 三层「卷积 + 激活 + 池化」堆叠提取特征；
- 展平后接两层全连接，输出 10 类得分；
- 训练时使用交叉熵损失 + Adam 优化器。

**教学意义：** 与预训练模型不同，本算法展示了「数据集 → 训练 → 权重 → 推理」的完整闭环。
""",
        "params": [
            {
                "name": "top_k",
                "label": "显示类别数 Top-K",
                "type": "slider",
                "args": {"min_value": 1, "max_value": 5, "step": 1, "value": 3},
                "explanation": "展示置信度最高的 K 个类别及其概率。",
            },
        ],
        "code": '''
# 训练入口（命令行）
# python -m modules.training --task cifar10 --epochs 5

# 推理
import torch
model = CIFAR10Net(num_classes=10)
model.load_state_dict(torch.load("models/cifar10_cnn.pth"))
with torch.no_grad():
    probs = torch.softmax(model(x)[0], dim=0)
''',
        "scenarios": [
            "📚 教学演示：展示深度学习训练全流程",
            "🔬 迁移学习：作为其他小型分类任务的基础",
            "🧪 实验对照：与经典特征分类方法对比",
        ],
    },
}

# 算法简易查找表 (algorithm_key -> display_name)
ALGORITHM_NAMES = {
    key: content["name"]
    for key, content in TEACHING_CONTENT.items()
}

# 算法分类查找
ALGORITHM_CATEGORY_MAP = {
    key: content["category"]
    for key, content in TEACHING_CONTENT.items()
}
