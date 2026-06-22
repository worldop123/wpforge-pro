"""
滚动行为模拟器
提供滚动行为的模拟功能
"""
import random
import math
from typing import List, Dict, Any, Optional

from app.core.logging import get_logger
from app.services.proxy.behavior.human_behavior import HumanBehaviorSimulator

logger = get_logger(__name__)


class ScrollBehaviorSimulator:
    """滚动行为模拟器"""
    
    def __init__(self, base_simulator: Optional[HumanBehaviorSimulator] = None):
        self._base = base_simulator or HumanBehaviorSimulator()
        self._scroll_y: float = 0.0
        self._scroll_x: float = 0.0
    
    def set_position(self, y: float, x: float = 0.0):
        """设置当前滚动位置"""
        self._scroll_y = y
        self._scroll_x = x
        self._base._scroll_y = y
        self._base._scroll_x = x
    
    def get_position(self) -> tuple:
        """获取当前滚动位置"""
        return (self._scroll_y, self._scroll_x)
    
    def scroll_to(self, target_y: float, target_x: float = 0.0,
                  speed: float = 1000.0) -> List[Dict[str, Any]]:
        """
        滚动到目标位置
        
        Args:
            target_y: 目标Y位置
            target_x: 目标X位置
            speed: 滚动速度（像素/秒）
            
        Returns:
            滚动事件列表
        """
        events = []
        
        # 计算距离
        dy = target_y - self._scroll_y
        dx = target_x - self._scroll_x
        distance = math.sqrt(dy * dy + dx * dx)
        
        # 计算步数
        duration = distance / speed
        steps = max(10, int(duration * 60))  # 60fps
        
        # 生成滚动路径
        scroll_events = self._base.human_like_scroll(target_y, steps=steps)
        
        for pos in scroll_events:
            events.append({
                "type": "scroll",
                "y": pos,
                "x": self._scroll_x,  # 简化：X方向暂不处理
            })
        
        self._scroll_y = target_y
        self._scroll_x = target_x
        
        return events
    
    def scroll_down(self, distance: float = 500.0) -> List[Dict[str, Any]]:
        """
        向下滚动指定距离
        
        Args:
            distance: 滚动距离（像素）
            
        Returns:
            滚动事件列表
        """
        return self.scroll_to(self._scroll_y + distance)
    
    def scroll_up(self, distance: float = 500.0) -> List[Dict[str, Any]]:
        """
        向上滚动指定距离
        
        Args:
            distance: 滚动距离（像素）
            
        Returns:
            滚动事件列表
        """
        return self.scroll_to(max(0, self._scroll_y - distance))
    
    def scroll_to_element(self, element_y: float, element_height: float = 100.0,
                          viewport_height: float = 800.0) -> List[Dict[str, Any]]:
        """
        滚动到元素位置（使元素可见）
        
        Args:
            element_y: 元素Y位置
            element_height: 元素高度
            viewport_height: 视口高度
            
        Returns:
            滚动事件列表
        """
        # 计算目标位置（使元素居中）
        target_y = element_y - viewport_height / 2 + element_height / 2
        target_y = max(0, target_y)
        
        return self.scroll_to(target_y)
    
    def random_scroll(self, max_distance: float = 1000.0,
                      direction: str = "down") -> List[Dict[str, Any]]:
        """
        随机滚动
        
        Args:
            max_distance: 最大滚动距离
            direction: 方向（down/up/random）
            
        Returns:
            滚动事件列表
        """
        distance = random.uniform(max_distance * 0.3, max_distance)
        
        if direction == "random":
            direction = random.choice(["down", "up"])
        
        if direction == "down":
            return self.scroll_down(distance)
        else:
            return self.scroll_up(distance)
    
    def scroll_with_pauses(self, target_y: float,
                           num_pauses: int = 3) -> List[Dict[str, Any]]:
        """
        带停顿的滚动（模拟阅读）
        
        Args:
            target_y: 目标位置
            num_pauses: 停顿次数
            
        Returns:
            滚动事件列表
        """
        events = []
        start_y = self._scroll_y
        distance = target_y - start_y
        
        # 分段滚动
        segment_distance = distance / (num_pauses + 1)
        
        for i in range(num_pauses + 1):
            segment_target = start_y + segment_distance * (i + 1)
            segment_events = self.scroll_to(segment_target)
            events.extend(segment_events)
            
            if i < num_pauses:
                # 添加停顿
                pause_duration = random.uniform(0.5, 3.0)
                events.append({
                    "type": "scroll_pause",
                    "duration": pause_duration,
                    "y": segment_target,
                })
        
        return events
    
    def simulate_reading_scroll(self, page_height: float,
                                 viewport_height: float = 800.0,
                                 reading_speed: float = 200.0) -> List[Dict[str, Any]]:
        """
        模拟阅读式滚动
        
        Args:
            page_height: 页面总高度
            viewport_height: 视口高度
            reading_speed: 阅读速度（像素/秒）
            
        Returns:
            滚动事件列表
        """
        events = []
        current_y = 0.0
        
        while current_y < page_height - viewport_height:
            # 滚动一段距离
            scroll_distance = random.uniform(viewport_height * 0.3, viewport_height * 0.7)
            target_y = min(current_y + scroll_distance, page_height - viewport_height)
            
            scroll_events = self.scroll_to(target_y, speed=reading_speed)
            events.extend(scroll_events)
            
            # 阅读停顿
            reading_time = random.uniform(2.0, 10.0)
            events.append({
                "type": "reading_pause",
                "duration": reading_time,
                "y": target_y,
            })
            
            current_y = target_y
            
            # 偶尔回滚（重新看上面的内容）
            if random.random() < 0.2:
                rollback_distance = random.uniform(50, 200)
                rollback_target = max(0, current_y - rollback_distance)
                rollback_events = self.scroll_to(rollback_target, speed=reading_speed * 1.5)
                events.extend(rollback_events)
                
                # 短暂停顿
                events.append({
                    "type": "reread_pause",
                    "duration": random.uniform(1.0, 3.0),
                    "y": rollback_target,
                })
                
                # 再滚回来
                scroll_back_events = self.scroll_to(current_y, speed=reading_speed)
                events.extend(scroll_back_events)
        
        return events
    
    def get_scroll_speed(self) -> float:
        """获取典型滚动速度（像素/秒）"""
        return random.uniform(500, 3000)
