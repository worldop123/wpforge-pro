"""
鼠标行为模拟器
提供鼠标移动轨迹的模拟功能
"""
import math
import random
from typing import List, Tuple, Optional

from app.core.logging import get_logger
from app.services.proxy.behavior.human_behavior import HumanBehaviorSimulator

logger = get_logger(__name__)


class MouseBehaviorSimulator:
    """鼠标行为模拟器"""
    
    def __init__(self, base_simulator: Optional[HumanBehaviorSimulator] = None):
        self._base = base_simulator or HumanBehaviorSimulator()
        self._current_x: float = 0.0
        self._current_y: float = 0.0
    
    def set_position(self, x: float, y: float):
        """设置当前鼠标位置"""
        self._current_x = x
        self._current_y = y
        self._base._mouse_x = x
        self._base._mouse_y = y
    
    def get_position(self) -> Tuple[float, float]:
        """获取当前鼠标位置"""
        return (self._current_x, self._current_y)
    
    def move_to(self, target_x: float, target_y: float, 
                speed: float = 1000.0) -> List[Tuple[float, float]]:
        """
        移动鼠标到目标位置
        
        Args:
            target_x: 目标X坐标
            target_y: 目标Y坐标
            speed: 移动速度（像素/秒）
            
        Returns:
            路径点列表
        """
        # 计算距离
        dx = target_x - self._current_x
        dy = target_y - self._current_y
        distance = math.sqrt(dx * dx + dy * dy)
        
        # 计算步数（基于速度）
        duration = distance / speed
        steps = max(10, int(duration * 60))  # 60fps
        
        # 生成路径
        path = self._base.generate_mouse_path(
            self._current_x, self._current_y,
            target_x, target_y,
            steps=steps
        )
        
        self._current_x = target_x
        self._current_y = target_y
        
        return path
    
    def random_move(self, bounds: Tuple[int, int, int, int],
                     duration: float = 5.0) -> List[Tuple[float, float]]:
        """
        在边界内随机移动
        
        Args:
            bounds: 边界 (x1, y1, x2, y2)
            duration: 持续时间（秒）
            
        Returns:
            路径点列表
        """
        x1, y1, x2, y2 = bounds
        
        # 随机选择目标点
        target_x = random.uniform(x1, x2)
        target_y = random.uniform(y1, y2)
        
        return self.move_to(target_x, target_y)
    
    def generate_bezier_path(self, start: Tuple[float, float],
                              end: Tuple[float, float],
                              control_points: List[Tuple[float, float]],
                              steps: int = 30) -> List[Tuple[float, float]]:
        """
        生成贝塞尔曲线路径
        
        Args:
            start: 起点
            end: 终点
            control_points: 控制点列表
            steps: 步数
            
        Returns:
            路径点列表
        """
        points = []
        n = len(control_points) + 1  # 贝塞尔曲线阶数
        
        for i in range(steps + 1):
            t = i / steps
            
            # 计算贝塞尔曲线上的点
            x, y = self._bezier_point(start, end, control_points, t)
            
            # 添加微小抖动
            jitter_x = (random.random() - 0.5) * 2
            jitter_y = (random.random() - 0.5) * 2
            
            points.append((x + jitter_x, y + jitter_y))
        
        return points
    
    def _bezier_point(self, start: Tuple[float, float],
                       end: Tuple[float, float],
                       control_points: List[Tuple[float, float]],
                       t: float) -> Tuple[float, float]:
        """计算贝塞尔曲线上的点"""
        # 简化实现：使用de Casteljau算法
        points = [start] + control_points + [end]
        
        while len(points) > 1:
            new_points = []
            for i in range(len(points) - 1):
                x = points[i][0] * (1 - t) + points[i + 1][0] * t
                y = points[i][1] * (1 - t) + points[i + 1][1] * t
                new_points.append((x, y))
            points = new_points
        
        return points[0]
    
    def add_jitter(self, path: List[Tuple[float, float]],
                   jitter_amount: float = 1.0) -> List[Tuple[float, float]]:
        """
        给路径添加抖动
        
        Args:
            path: 原始路径
            jitter_amount: 抖动量
            
        Returns:
            抖动后的路径
        """
        result = []
        for x, y in path:
            jitter_x = (random.random() - 0.5) * jitter_amount * 2
            jitter_y = (random.random() - 0.5) * jitter_amount * 2
            result.append((x + jitter_x, y + jitter_y))
        return result
    
    def add_overshoot(self, path: List[Tuple[float, float]],
                       overshoot_amount: float = 5.0) -> List[Tuple[float, float]]:
        """
        给路径添加过冲效果
        
        Args:
            path: 原始路径
            overshoot_amount: 过冲量
            
        Returns:
            添加过冲后的路径
        """
        if len(path) < 2:
            return path
        
        # 计算方向
        dx = path[-1][0] - path[-2][0]
        dy = path[-1][1] - path[-2][1]
        distance = math.sqrt(dx * dx + dy * dy)
        
        if distance == 0:
            return path
        
        # 归一化方向
        dx /= distance
        dy /= distance
        
        # 添加过冲点
        overshoot_x = path[-1][0] + dx * overshoot_amount
        overshoot_y = path[-1][1] + dy * overshoot_amount
        
        result = path[:-1] + [(overshoot_x, overshoot_y)] + [path[-1]]
        return result
