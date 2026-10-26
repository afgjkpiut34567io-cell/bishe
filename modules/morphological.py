"""
形态学操作模块 - 基于形状的图像处理
包含：腐蚀、膨胀、开运算、闭运算、形态学梯度、顶帽、黑帽
"""

import cv2
import numpy as np
from typing import Dict, Any, Tuple, List

from utils.image_io import to_grayscale, ensure_3channel

def _get_kernel(ksize: int, shape: str = "rect") -> np.ndarray:
    """获取形态学操作的结构元素"""
    shape_map = {
        "rect": cv2.MORPH_RECT,
        "ellipse": cv2.MORPH_ELLIPSE,
        "cross": cv2.MORPH_CROSS,
    }
    return cv2.getStructuringElement(
        shape_map.get(shape, cv2.MORPH_RECT), (ksize, ksize)
    )

def erosion(image: np.ndarray, params: Dict[str, Any]) -> np.ndarray:
    """
    腐蚀操作 - 缩小前景区域

    原理：结构元素在图像上滑动，只有当结构元素完全覆盖前景时，
    中心点才保留为前景。腐蚀会消除小物体、断开纤细连接。

    参数:
        ksize: 结构元素大小 (越大腐蚀效果越强)
        iterations: 迭代次数 (重复腐蚀的次数)
    """
    gray = to_grayscale(image)
    ksize = params.get("ksize", 5)
    iterations = params.get("iterations", 1)
    kernel = _get_kernel(ksize)
    result = cv2.erode(gray, kernel, iterations=iterations)
    return ensure_3channel(result)

def dilation(image: np.ndarray, params: Dict[str, Any]) -> np.ndarray:
    """
    膨胀操作 - 扩大前景区域

    原理：结构元素在图像上滑动，只要结构元素与前景有交集，
    中心点就设为前景。膨胀会填充空洞、连接邻近物体。

    参数:
        ksize: 结构元素大小 (越大膨胀效果越强)
        iterations: 迭代次数
    """
    gray = to_grayscale(image)
    ksize = params.get("ksize", 5)
    iterations = params.get("iterations", 1)
    kernel = _get_kernel(ksize)
    result = cv2.dilate(gray, kernel, iterations=iterations)
    return ensure_3channel(result)

def opening(image: np.ndarray, params: Dict[str, Any]) -> np.ndarray:
    """
    开运算 - 先腐蚀后膨胀

    原理：先腐蚀去除小物体（噪声），再膨胀恢复主要物体大小。
    用于消除小噪声点、断开纤细连接、平滑物体轮廓。

    参数:
        ksize: 结构元素大小
    """
    ksize = params.get("ksize", 5)
    kernel = _get_kernel(ksize)
    gray = to_grayscale(image)
    result = cv2.morphologyEx(gray, cv2.MORPH_OPEN, kernel)
    return ensure_3channel(result)

def closing(image: np.ndarray, params: Dict[str, Any]) -> np.ndarray:
    """
    闭运算 - 先膨胀后腐蚀

    原理：先膨胀填充物体内小空洞，再腐蚀恢复物体大小。
    用于填充前景中的小孔洞、连接邻近物体。

    参数:
        ksize: 结构元素大小
    """
    ksize = params.get("ksize", 5)
    kernel = _get_kernel(ksize)
    gray = to_grayscale(image)
    result = cv2.morphologyEx(gray, cv2.MORPH_CLOSE, kernel)
    return ensure_3channel(result)

def morphological_gradient(image: np.ndarray, params: Dict[str, Any]) -> np.ndarray:
    """
    形态学梯度 - 膨胀与腐蚀的差值

    原理：gradient = dilation - erosion
    结果显示了物体的边界轮廓，类似于边缘检测但更粗。

    参数:
        ksize: 结构元素大小
    """
    ksize = params.get("ksize", 3)
    kernel = _get_kernel(ksize)
    gray = to_grayscale(image)
    result = cv2.morphologyEx(gray, cv2.MORPH_GRADIENT, kernel)
    return ensure_3channel(result)

def top_hat(image: np.ndarray, params: Dict[str, Any]) -> np.ndarray:
    """
    顶帽变换 - 原图与开运算的差值

    原理：top_hat = original - opening
    提取比周围亮的细小特征，用于在光照不均匀时分离亮斑。

    参数:
        ksize: 结构元素大小 (应大于要提取的特征)
    """
    ksize = params.get("ksize", 9)
    kernel = _get_kernel(ksize)
    gray = to_grayscale(image)
    result = cv2.morphologyEx(gray, cv2.MORPH_TOPHAT, kernel)
    return ensure_3channel(result)

def black_hat(image: np.ndarray, params: Dict[str, Any]) -> np.ndarray:
    """
    黑帽变换 - 闭运算与原图的差值

    原理：black_hat = closing - original
    提取比周围暗的细小特征，用于在光照不均匀时分离暗斑。

    参数:
        ksize: 结构元素大小 (应大于要提取的特征)
    """
    ksize = params.get("ksize", 9)
    kernel = _get_kernel(ksize)
    gray = to_grayscale(image)
    result = cv2.morphologyEx(gray, cv2.MORPH_BLACKHAT, kernel)
    return ensure_3channel(result)

def get_morphology_steps(
    image: np.ndarray, algorithm: str, params: Dict[str, Any]
) -> List[Tuple[str, np.ndarray]]:
    """
    获取形态学操作的中间步骤
    """
    steps = []
    gray = to_grayscale(image)

    # 二值化以便演示
    _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)

    ksize = params.get("ksize", 5)
    kernel = _get_kernel(ksize)

    if algorithm == "opening":
        eroded = cv2.erode(binary, kernel, iterations=1)
        steps.append(("① 腐蚀 (去除小噪点)", eroded))
        opened = cv2.dilate(eroded, kernel, iterations=1)
        steps.append(("② 膨胀 (恢复物体大小)", opened))
        steps.append(("开运算 = 腐蚀 → 膨胀", opened))

    elif algorithm == "closing":
        dilated = cv2.dilate(binary, kernel, iterations=1)
        steps.append(("① 膨胀 (填充空洞)", dilated))
        closed = cv2.erode(dilated, kernel, iterations=1)
        steps.append(("② 腐蚀 (恢复物体大小)", closed))
        steps.append(("闭运算 = 膨胀 → 腐蚀", closed))

    elif algorithm == "morphological_gradient":
        eroded = cv2.erode(binary, kernel, iterations=1)
        dilated = cv2.dilate(binary, kernel, iterations=1)
        steps.append(("腐蚀结果", eroded))
        steps.append(("膨胀结果", dilated))
        gradient = cv2.morphologyEx(binary, cv2.MORPH_GRADIENT, kernel)
        steps.append(("形态学梯度 = 膨胀 - 腐蚀", gradient))

    elif algorithm == "top_hat":
        opened = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)
        steps.append(("开运算结果", opened))
        tophat = cv2.morphologyEx(binary, cv2.MORPH_TOPHAT, kernel)
        steps.append(("顶帽 = 原图 - 开运算 (亮特征)", tophat))

    elif algorithm == "black_hat":
        closed = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
        steps.append(("闭运算结果", closed))
        blackhat = cv2.morphologyEx(binary, cv2.MORPH_BLACKHAT, kernel)
        steps.append(("黑帽 = 闭运算 - 原图 (暗特征)", blackhat))

    return steps
