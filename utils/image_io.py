"""
图像IO工具模块 - 负责图像的加载、保存、格式转换和预处理
"""

import cv2
import numpy as np
import time
from typing import Optional, Tuple

from .config import MAX_IMAGE_WIDTH, MAX_IMAGE_HEIGHT, PREVIEW_MAX_WIDTH


def load_image(uploaded_file) -> Tuple[Optional[np.ndarray], Optional[str]]:
    """
    加载上传的图像文件

    Args:
        uploaded_file: Streamlit UploadedFile对象
    Returns:
        (image, error)：成功时 image 为 BGR 数组、error 为 None；
        失败时 image 为 None、error 为可读的错误原因。
    """
    if uploaded_file is None:
        return None, None
    try:
        # 读取文件字节
        file_bytes = np.frombuffer(uploaded_file.read(), dtype=np.uint8)
        # 解码图像
        image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
        if image is None:
            return None, "无法解码该文件，请确认是有效的图像文件"
        # 自动缩放大图像
        image = auto_resize(image)
        return image, None
    except Exception as e:
        return None, f"图像加载失败：{type(e).__name__}: {e}"


def auto_resize(image: np.ndarray) -> np.ndarray:
    """
    自动缩放过大图像到合理尺寸
    """
    h, w = image.shape[:2]
    if w > MAX_IMAGE_WIDTH or h > MAX_IMAGE_HEIGHT:
        scale = min(MAX_IMAGE_WIDTH / w, MAX_IMAGE_HEIGHT / h)
        new_w = int(w * scale)
        new_h = int(h * scale)
        return cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_AREA)
    return image


def resize_for_preview(image: np.ndarray, max_width: int = PREVIEW_MAX_WIDTH) -> np.ndarray:
    """
    缩放图像用于预览显示（默认宽度取自 config.PREVIEW_MAX_WIDTH）
    """
    h, w = image.shape[:2]
    if w > max_width:
        scale = max_width / w
        new_w = max_width
        new_h = int(h * scale)
        return cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_AREA)
    return image


def bgr_to_rgb(image: np.ndarray) -> np.ndarray:
    """BGR转RGB"""
    return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)


def to_grayscale(image: np.ndarray) -> np.ndarray:
    """转换为灰度图像"""
    if len(image.shape) == 2:
        return image
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)


def ensure_3channel(image: np.ndarray) -> np.ndarray:
    """确保图像是3通道（灰度转为BGR）"""
    if len(image.shape) == 2:
        return cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
    return image


def image_to_bytes(image: np.ndarray, format: str = "PNG") -> bytes:
    """
    将图像编码为字节（用于下载）
    """
    # 确保是BGR格式
    if len(image.shape) == 2:
        image_bgr = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
    elif image.shape[2] == 4:
        image_bgr = cv2.cvtColor(image, cv2.COLOR_BGRA2BGR)
    else:
        image_bgr = image

    success, buffer = cv2.imencode(f".{format.lower()}", image_bgr)
    if success:
        return buffer.tobytes()
    return b""


def get_image_info(image: np.ndarray) -> dict:
    """
    获取图像基本信息
    """
    h, w = image.shape[:2]
    channels = 1 if len(image.shape) == 2 else image.shape[2]
    return {
        "尺寸": f"{w} × {h} px",
        "通道数": channels,
        "数据类型": str(image.dtype),
        "像素范围": f"[{image.min()}, {image.max()}]",
    }


class Timer:
    """性能计时器"""

    def __init__(self):
        self._start = 0.0
        self._elapsed = 0.0

    def __enter__(self):
        self._start = time.perf_counter()
        return self

    def __exit__(self, *args):
        self._elapsed = time.perf_counter() - self._start

    @property
    def elapsed_ms(self) -> float:
        return self._elapsed * 1000

    @property
    def elapsed_str(self) -> str:
        ms = self.elapsed_ms
        if ms < 1:
            return f"{ms*1000:.1f}μs"
        elif ms < 1000:
            return f"{ms:.1f}ms"
        else:
            return f"{ms/1000:.2f}s"
