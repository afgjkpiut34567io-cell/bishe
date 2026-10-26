"""
配置常量模块 - 定义平台全局配置参数
"""

# ==================== 应用配置 ====================
APP_TITLE = "图像处理算法交互式演示与教学平台"
APP_LAYOUT = "wide"
APP_SIDEBAR_STATE = "expanded"

# ==================== 性能配置 ====================
MAX_IMAGE_WIDTH = 1200       # 处理前自动缩放的最大宽度
MAX_IMAGE_HEIGHT = 900       # 处理前自动缩放的最大高度
PREVIEW_MAX_WIDTH = 600      # 预览区域最大宽度
CACHE_TTL = 300              # 缓存过期时间(秒)
MAX_RESPONSE_TIME_MS = 300   # 目标最大响应时间(ms)

# ==================== 文件配置 ====================
# 上传支持的格式（与下载支持格式保持一致，含 webp）
SUPPORTED_FORMATS = ["jpg", "jpeg", "png", "bmp", "tiff", "tif", "webp"]
SUPPORTED_FORMATS_UPLOAD = SUPPORTED_FORMATS

# ==================== 算法分类配置 ====================
ALGORITHM_CATEGORIES = {
    "📊 滤波算法": {
        "icon": "🔧",
        "description": "空间域滤波器，用于图像平滑、去噪等",
        "algorithms": [
            "gaussian_blur",
            "median_blur",
            "mean_blur",
            "bilateral_filter",
            "box_filter",
        ],
    },
    "🎨 图像增强": {
        "icon": "✨",
        "description": "改善图像视觉效果的技术",
        "algorithms": [
            "histogram_equalization",
            "clahe",
            "contrast_brightness",
            "gamma_correction",
            "sharpening",
            "unsharp_masking",
        ],
    },
    "📏 边缘检测": {
        "icon": "📐",
        "description": "检测图像中亮度变化显著的边缘",
        "algorithms": [
            "canny_edge",
            "sobel_edge",
            "laplacian_edge",
            "scharr_edge",
            "prewitt_edge",
        ],
    },
    "🔲 形态学操作": {
        "icon": "⬛",
        "description": "基于形状的图像处理操作",
        "algorithms": [
            "erosion",
            "dilation",
            "opening",
            "closing",
            "morphological_gradient",
            "top_hat",
            "black_hat",
        ],
    },
    "✂️ 阈值分割": {
        "icon": "🔪",
        "description": "将图像分割为前景和背景",
        "algorithms": [
            "global_threshold",
            "adaptive_threshold",
            "otsu_threshold",
        ],
    },
    "🔄 图像变换": {
        "icon": "🔀",
        "description": "图像的几何变换和频域变换",
        "algorithms": [
            "resize_scale",
            "rotation",
            "affine_transform",
            "fourier_transform",
            "fourier_lowpass",
            "fourier_highpass",
        ],
    },
    "🧠 深度学习": {
        "icon": "🧠",
        "description": "基于卷积神经网络的图像理解与生成（需安装 torch）",
        "algorithms": [
            "image_classification",
            "semantic_segmentation",
            "super_resolution",
            "cifar10_classification",
        ],
    },
}

# ==================== 默认参数配置 ====================
DEFAULT_PARAMS = {
    # 滤波算法
    "gaussian_blur": {"ksize": (5, 5), "sigma_x": 1.0},
    "median_blur": {"ksize": 5},
    "mean_blur": {"ksize": (5, 5)},
    "bilateral_filter": {"d": 9, "sigma_color": 75, "sigma_space": 75},
    "box_filter": {"ksize": (5, 5)},
    # 图像增强
    "histogram_equalization": {},
    "clahe": {"clip_limit": 2.0, "tile_grid_size": (8, 8)},
    "contrast_brightness": {"alpha": 1.0, "beta": 0},
    "gamma_correction": {"gamma": 1.0},
    "sharpening": {"strength": 1.0},
    "unsharp_masking": {"sigma": 1.0, "strength": 1.0},
    # 边缘检测
    "canny_edge": {"threshold1": 50, "threshold2": 150},
    "sobel_edge": {"ksize": 3, "dx": 1, "dy": 1},
    "laplacian_edge": {"ksize": 3},
    "scharr_edge": {"dx": 1, "dy": 0},
    "prewitt_edge": {},
    # 形态学操作
    "erosion": {"ksize": 5, "iterations": 1},
    "dilation": {"ksize": 5, "iterations": 1},
    "opening": {"ksize": 5},
    "closing": {"ksize": 5},
    "morphological_gradient": {"ksize": 3},
    "top_hat": {"ksize": 9},
    "black_hat": {"ksize": 9},
    # 阈值分割
    "global_threshold": {"thresh": 127, "maxval": 255},
    "adaptive_threshold": {"block_size": 11, "c": 2},
    "otsu_threshold": {},
    # 图像变换
    "resize_scale": {"scale": 0.5},
    "rotation": {"angle": 0, "scale": 1.0},
    "affine_transform": {"angle": 0, "scale": 1.0, "tx": 0, "ty": 0},
    "fourier_transform": {},
    "fourier_lowpass": {"cutoff_ratio": 0.1},
    "fourier_highpass": {"cutoff_ratio": 0.1},
    # 深度学习
    "image_classification": {"top_k": 3},
    "semantic_segmentation": {"opacity": 0.5},
    "super_resolution": {"scale": 2},
    "cifar10_classification": {"top_k": 3},
}
