"""
键盘行为模拟器
提供键盘输入行为的模拟功能
"""
import random
from typing import List, Dict, Any, Optional

from app.core.logging import get_logger
from app.services.proxy.behavior.human_behavior import HumanBehaviorSimulator

logger = get_logger(__name__)


class KeyboardBehaviorSimulator:
    """键盘行为模拟器"""
    
    def __init__(self, base_simulator: Optional[HumanBehaviorSimulator] = None):
        self._base = base_simulator or HumanBehaviorSimulator()
    
    def type_text(self, text: str, base_speed: float = 150.0) -> List[Dict[str, Any]]:
        """
        生成打字事件序列
        
        Args:
            text: 要输入的文本
            base_speed: 基础速度（毫秒/字符）
            
        Returns:
            事件列表
        """
        return self._base.human_like_type(text, base_speed)
    
    def type_with_errors(self, text: str, error_rate: float = 0.07,
                         base_speed: float = 150.0) -> List[Dict[str, Any]]:
        """
        带错误的打字（模拟打错字然后删除）
        
        Args:
            text: 要输入的文本
            error_rate: 错误率
            base_speed: 基础速度（毫秒/字符）
            
        Returns:
            事件列表
        """
        # 保存当前错误率
        original_intensity = self._base._behavior_intensity
        self._base._behavior_intensity = error_rate / 0.07  # 调整强度
        
        events = self.type_text(text, base_speed)
        
        # 恢复
        self._base._behavior_intensity = original_intensity
        
        return events
    
    def press_key(self, key: str) -> List[Dict[str, Any]]:
        """
        生成单个按键事件
        
        Args:
            key: 按键
            
        Returns:
            事件列表
        """
        events = []
        
        events.append({
            "type": "keydown",
            "key": key,
        })
        
        events.append({
            "type": "keypress",
            "key": key,
        })
        
        events.append({
            "type": "keyup",
            "key": key,
        })
        
        return events
    
    def press_key_combination(self, keys: List[str]) -> List[Dict[str, Any]]:
        """
        生成组合键事件（如Ctrl+C）
        
        Args:
            keys: 按键列表（按按下顺序）
            
        Returns:
            事件列表
        """
        events = []
        
        # 按下所有键
        for key in keys:
            events.append({
                "type": "keydown",
                "key": key,
            })
        
        # 释放所有键（反向顺序）
        for key in reversed(keys):
            events.append({
                "type": "keyup",
                "key": key,
            })
        
        return events
    
    def copy(self) -> List[Dict[str, Any]]:
        """生成复制操作（Ctrl+C）"""
        return self.press_key_combination(["Control", "c"])
    
    def paste(self) -> List[Dict[str, Any]]:
        """生成粘贴操作（Ctrl+V）"""
        return self.press_key_combination(["Control", "v"])
    
    def cut(self) -> List[Dict[str, Any]]:
        """生成剪切操作（Ctrl+X）"""
        return self.press_key_combination(["Control", "x"])
    
    def select_all(self) -> List[Dict[str, Any]]:
        """生成全选操作（Ctrl+A）"""
        return self.press_key_combination(["Control", "a"])
    
    def undo(self) -> List[Dict[str, Any]]:
        """生成撤销操作（Ctrl+Z）"""
        return self.press_key_combination(["Control", "z"])
    
    def redo(self) -> List[Dict[str, Any]]:
        """生成重做操作（Ctrl+Y）"""
        return self.press_key_combination(["Control", "y"])
    
    def enter(self) -> List[Dict[str, Any]]:
        """生成回车键"""
        return self.press_key("Enter")
    
    def backspace(self, count: int = 1) -> List[Dict[str, Any]]:
        """
        生成退格键
        
        Args:
            count: 次数
            
        Returns:
            事件列表
        """
        events = []
        for _ in range(count):
            events.extend(self.press_key("Backspace"))
        return events
    
    def tab(self) -> List[Dict[str, Any]]:
        """生成Tab键"""
        return self.press_key("Tab")
    
    def escape(self) -> List[Dict[str, Any]]:
        """生成Esc键"""
        return self.press_key("Escape")
    
    def arrow_keys(self, direction: str = "down", count: int = 1) -> List[Dict[str, Any]]:
        """
        生成方向键
        
        Args:
            direction: 方向（up/down/left/right）
            count: 次数
            
        Returns:
            事件列表
        """
        key_map = {
            "up": "ArrowUp",
            "down": "ArrowDown",
            "left": "ArrowLeft",
            "right": "ArrowRight",
        }
        
        key = key_map.get(direction, "ArrowDown")
        events = []
        for _ in range(count):
            events.extend(self.press_key(key))
        return events
    
    def get_typing_speed(self) -> float:
        """获取典型打字速度（毫秒/字符）"""
        return random.uniform(100, 400)
    
    def get_error_rate(self) -> float:
        """获取典型错误率"""
        return random.uniform(0.05, 0.1)
