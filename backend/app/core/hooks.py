"""
钩子系统 - 插件化架构核心
支持动作钩子和过滤器钩子
"""

from typing import Callable, Dict, List, Any, Optional
from collections import defaultdict
import functools


class HookManager:
    """钩子管理器"""
    
    def __init__(self):
        self.actions: Dict[str, List[Callable]] = defaultdict(list)
        self.filters: Dict[str, List[Callable]] = defaultdict(list)
        self.action_priorities: Dict[str, Dict[int, List[Callable]]] = defaultdict(
            lambda: defaultdict(list)
        )
        self.filter_priorities: Dict[str, Dict[int, List[Callable]]] = defaultdict(
            lambda: defaultdict(list)
        )
    
    # ==================== 动作钩子 ====================
    
    def add_action(self, hook: str, callback: Callable, priority: int = 10) -> None:
        """添加动作钩子
        
        Args:
            hook: 钩子名称
            callback: 回调函数
            priority: 优先级，数字越小越先执行
        """
        self.action_priorities[hook][priority].append(callback)
        # 重新构建有序列表
        self._rebuild_action_list(hook)
    
    def remove_action(self, hook: str, callback: Callable, priority: int = 10) -> bool:
        """移除动作钩子"""
        try:
            self.action_priorities[hook][priority].remove(callback)
            self._rebuild_action_list(hook)
            return True
        except ValueError:
            return False
    
    def do_action(self, hook: str, *args, **kwargs) -> None:
        """执行动作钩子"""
        for callback in self.actions.get(hook, []):
            try:
                callback(*args, **kwargs)
            except Exception as e:
                # 记录错误但不中断其他钩子
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Action hook '{hook}' callback error: {e}")
    
    def has_action(self, hook: str) -> bool:
        """检查是否有动作钩子"""
        return hook in self.actions and len(self.actions[hook]) > 0
    
    # ==================== 过滤器钩子 ====================
    
    def add_filter(self, hook: str, callback: Callable, priority: int = 10) -> None:
        """添加过滤器钩子"""
        self.filter_priorities[hook][priority].append(callback)
        self._rebuild_filter_list(hook)
    
    def remove_filter(self, hook: str, callback: Callable, priority: int = 10) -> bool:
        """移除过滤器钩子"""
        try:
            self.filter_priorities[hook][priority].remove(callback)
            self._rebuild_filter_list(hook)
            return True
        except ValueError:
            return False
    
    def apply_filters(self, hook: str, value: Any, *args, **kwargs) -> Any:
        """应用过滤器钩子"""
        result = value
        for callback in self.filters.get(hook, []):
            try:
                result = callback(result, *args, **kwargs)
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Filter hook '{hook}' callback error: {e}")
        return result
    
    def has_filter(self, hook: str) -> bool:
        """检查是否有过滤器钩子"""
        return hook in self.filters and len(self.filters[hook]) > 0
    
    # ==================== 内部方法 ====================
    
    def _rebuild_action_list(self, hook: str) -> None:
        """重新构建动作钩子的有序列表"""
        priorities = sorted(self.action_priorities[hook].keys())
        self.actions[hook] = []
        for p in priorities:
            self.actions[hook].extend(self.action_priorities[hook][p])
    
    def _rebuild_filter_list(self, hook: str) -> None:
        """重新构建过滤器钩子的有序列表"""
        priorities = sorted(self.filter_priorities[hook].keys())
        self.filters[hook] = []
        for p in priorities:
            self.filters[hook].extend(self.filter_priorities[hook][p])
    
    # ==================== 装饰器 ====================
    
    def action(self, hook: str, priority: int = 10):
        """动作钩子装饰器"""
        def decorator(func):
            self.add_action(hook, func, priority)
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)
            return wrapper
        return decorator
    
    def filter(self, hook: str, priority: int = 10):
        """过滤器钩子装饰器"""
        def decorator(func):
            self.add_filter(hook, func, priority)
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)
            return wrapper
        return decorator


# 全局钩子管理器实例
hooks = HookManager()
