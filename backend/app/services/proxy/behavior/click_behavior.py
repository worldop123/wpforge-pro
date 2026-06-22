"""
点击行为模拟器
提供点击行为的模拟功能
"""
import random
from typing import List, Dict, Any, Optional, Tuple

from app.core.logging import get_logger
from app.services.proxy.behavior.human_behavior import HumanBehaviorSimulator

logger = get_logger(__name__)


class ClickBehaviorSimulator:
    """点击行为模拟器"""
    
    def __init__(self, base_simulator: Optional[HumanBehaviorSimulator] = None):
        self._base = base_simulator or HumanBehaviorSimulator()
    
    def click(self, x: float, y: float, button: int = 0) -> List[Dict[str, Any]]:
        """
        生成点击事件序列
        
        Args:
            x: X坐标
            y: Y坐标
            button: 鼠标按钮（0=左键，1=中键，2=右键）
            
        Returns:
            事件列表
        """
        return self._base.human_like_click(x, y)
    
    def double_click(self, x: float, y: float) -> List[Dict[str, Any]]:
        """
        生成双击事件序列
        
        Args:
            x: X坐标
            y: Y坐标
            
        Returns:
            事件列表
        """
        events = []
        
        # 第一次点击
        first_click = self.click(x, y)
        events.extend(first_click)
        
        # 双击间隔（300-500ms）
        double_click_delay = random.uniform(300, 500) / 1000.0
        events.append({
            "type": "double_click_pause",
            "duration": double_click_delay,
        })
        
        # 第二次点击
        second_click = self.click(x, y)
        events.extend(second_click)
        
        return events
    
    def right_click(self, x: float, y: float) -> List[Dict[str, Any]]:
        """
        生成右键点击事件序列
        
        Args:
            x: X坐标
            y: Y坐标
            
        Returns:
            事件列表
        """
        events = []
        
        # 悬停
        hover_time = random.uniform(200, 800) / 1000.0
        events.append({
            "type": "hover",
            "x": x,
            "y": y,
            "duration": hover_time,
        })
        
        # 点击位置偏移
        offset_x = (random.random() - 0.5) * 6
        offset_y = (random.random() - 0.5) * 6
        click_x = x + offset_x
        click_y = y + offset_y
        
        # mousedown
        events.append({
            "type": "mousedown",
            "x": click_x,
            "y": click_y,
            "button": 2,
        })
        
        # mouseup
        events.append({
            "type": "mouseup",
            "x": click_x,
            "y": click_y,
            "button": 2,
        })
        
        # contextmenu
        events.append({
            "type": "contextmenu",
            "x": click_x,
            "y": click_y,
        })
        
        # 点击后等待
        post_click_time = random.uniform(200, 600) / 1000.0
        events.append({
            "type": "post_click_pause",
            "duration": post_click_time,
        })
        
        return events
    
    def click_and_drag(self, start_x: float, start_y: float,
                       end_x: float, end_y: float) -> List[Dict[str, Any]]:
        """
        生成点击拖拽事件序列
        
        Args:
            start_x: 起点X坐标
            start_y: 起点Y坐标
            end_x: 终点X坐标
            end_y: 终点Y坐标
            
        Returns:
            事件列表
        """
        events = []
        
        # 起点悬停
        hover_time = random.uniform(200, 500) / 1000.0
        events.append({
            "type": "hover",
            "x": start_x,
            "y": start_y,
            "duration": hover_time,
        })
        
        # mousedown
        events.append({
            "type": "mousedown",
            "x": start_x,
            "y": start_y,
            "button": 0,
        })
        
        # 拖拽移动
        drag_steps = random.randint(10, 30)
        for i in range(drag_steps + 1):
            t = i / drag_steps
            # 使用缓动函数
            if t < 0.2:
                eased = (t / 0.2) ** 2
            elif t > 0.8:
                eased = 1 - ((1 - (t - 0.8) / 0.2) ** 2)
            else:
                eased = 0.04 + (t - 0.2) * 0.96 / 0.6
            
            x = start_x + (end_x - start_x) * eased
            y = start_y + (end_y - start_y) * eased
            
            # 添加抖动
            jitter_x = (random.random() - 0.5) * 2
            jitter_y = (random.random() - 0.5) * 2
            
            events.append({
                "type": "mousemove",
                "x": x + jitter_x,
                "y": y + jitter_y,
            })
        
        # mouseup
        events.append({
            "type": "mouseup",
            "x": end_x,
            "y": end_y,
            "button": 0,
        })
        
        return events
    
    def get_random_click_delay(self) -> float:
        """获取随机点击延迟（秒）"""
        return self._base.get_click_delay()
    
    def get_click_accuracy(self) -> float:
        """获取点击精度（像素）"""
        return 3.0  # ±3像素
