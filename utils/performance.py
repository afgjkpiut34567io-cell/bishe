"""
性能优化模块 - 处理计时器（纯统计，不依赖界面框架）

缓存职责在 app.py / ui/compare.py 中由 st.cache_data 承担。
"""

from collections import deque


class ProcessingTimer:
    """处理计时器，记录最近N次处理的时间

    使用 collections.deque 替代 list，追加与丢弃最旧元素均为 O(1)。
    """

    def __init__(self, history_size: int = 20):
        self.history: deque = deque(maxlen=history_size)
        self.history_size = history_size
        self.last_time_ms: float = 0.0

    def record(self, elapsed_ms: float):
        """记录一次处理时间"""
        self.last_time_ms = elapsed_ms
        self.history.append(elapsed_ms)  # 超过 maxlen 时自动丢弃最旧元素

    @property
    def avg_time_ms(self) -> float:
        """平均处理时间"""
        if not self.history:
            return 0.0
        return sum(self.history) / len(self.history)

    @property
    def max_time_ms(self) -> float:
        """最大处理时间"""
        if not self.history:
            return 0.0
        return max(self.history)
