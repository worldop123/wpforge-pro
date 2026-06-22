"""
人类行为模拟器
整合所有行为模拟功能，提供统一的接口
"""
import random
import time
import math
from typing import Dict, Any, List, Optional, Tuple

from app.core.logging import get_logger

logger = get_logger(__name__)


class HumanBehaviorSimulator:
    """人类行为模拟器"""
    
    def __init__(self):
        self._random_seed: Optional[str] = None
        self._behavior_intensity: float = 0.7  # 行为强度 0.0 - 1.0
        
        # 鼠标状态
        self._mouse_x: float = 0.0
        self._mouse_y: float = 0.0
        
        # 滚动状态
        self._scroll_y: float = 0.0
        self._scroll_x: float = 0.0
    
    def set_seed(self, seed: str):
        """设置随机种子"""
        self._random_seed = seed
        random.seed(hashlib.md5(seed.encode()).hexdigest())
    
    def set_intensity(self, intensity: float):
        """设置行为强度"""
        self._behavior_intensity = max(0.0, min(1.0, intensity))
    
    def random_delay(self, min_ms: int = 100, max_ms: int = 1000) -> float:
        """
        生成随机延迟
        
        Args:
            min_ms: 最小延迟（毫秒）
            max_ms: 最大延迟（毫秒）
            
        Returns:
            延迟时间（秒）
        """
        delay = random.uniform(min_ms, max_ms) / 1000.0
        # 应用行为强度
        delay = delay * (0.5 + self._behavior_intensity * 0.5)
        return delay
    
    def human_like_scroll(self, target_y: float, steps: int = 20) -> List[float]:
        """
        生成人类滚动路径
        
        Args:
            target_y: 目标滚动位置
            steps: 步数
            
        Returns:
            滚动位置列表
        """
        positions = []
        start_y = self._scroll_y
        distance = target_y - start_y
        
        for i in range(steps + 1):
            progress = i / steps
            
            # 使用S曲线模拟加速和减速
            if progress < 0.2:
                # 加速阶段
                t = progress / 0.2
                eased = t * t
            elif progress > 0.8:
                # 减速阶段
                t = (progress - 0.8) / 0.2
                eased = 1 - (1 - t) * (1 - t)
            else:
                # 匀速阶段
                eased = 0.04 + (progress - 0.2) * 0.96 / 0.6
            
            # 添加微小抖动
            jitter = (random.random() - 0.5) * abs(distance) * 0.01 * self._behavior_intensity
            
            current_y = start_y + distance * eased + jitter
            positions.append(current_y)
        
        self._scroll_y = target_y
        return positions
    
    def human_like_type(self, text: str, base_speed: float = 150) -> List[Dict[str, Any]]:
        """
        生成人类打字模式
        
        Args:
            text: 要输入的文本
            base_speed: 基础速度（毫秒/字符）
            
        Returns:
            打字事件列表
        """
        events = []
        current_time = 0.0
        
        for i, char in enumerate(text):
            # 计算按键间隔（正态分布）
            speed_variation = random.gauss(0, base_speed * 0.3)
            char_delay = max(50, base_speed + speed_variation) / 1000.0
            
            # 偶尔打错字然后删除（5-10%概率）
            if random.random() < 0.07 * self._behavior_intensity and i > 0:
                # 打错字
                wrong_char = chr(random.randint(97, 122))  # 随机小写字母
                events.append({
                    "type": "keydown",
                    "key": wrong_char,
                    "time": current_time,
                })
                current_time += char_delay * 0.5
                
                events.append({
                    "type": "keypress",
                    "key": wrong_char,
                    "time": current_time,
                })
                current_time += char_delay * 0.3
                
                events.append({
                    "type": "keyup",
                    "key": wrong_char,
                    "time": current_time,
                })
                current_time += char_delay * 0.5
                
                # 按退格键
                events.append({
                    "type": "keydown",
                    "key": "Backspace",
                    "time": current_time,
                })
                current_time += char_delay * 0.5
                
                events.append({
                    "type": "keypress",
                    "key": "Backspace",
                    "time": current_time,
                })
                current_time += char_delay * 0.3
                
                events.append({
                    "type": "keyup",
                    "key": "Backspace",
                    "time": current_time,
                })
                current_time += char_delay * 0.5
            
            # 正常输入字符
            events.append({
                "type": "keydown",
                "key": char,
                "time": current_time,
            })
            current_time += char_delay * 0.3
            
            events.append({
                "type": "keypress",
                "key": char,
                "time": current_time,
            })
            current_time += char_delay * 0.2
            
            events.append({
                "type": "keyup",
                "key": char,
                "time": current_time,
            })
            current_time += char_delay * 0.5
            
            # 长文本中间有较长停顿（思考时间）
            if i > 0 and i % 20 == 0 and random.random() < 0.3 * self._behavior_intensity:
                pause_time = random.uniform(0.5, 2.0)
                events.append({
                    "type": "pause",
                    "time": current_time,
                    "duration": pause_time,
                })
                current_time += pause_time
        
        return events
    
    def human_like_click(self, target_x: float, target_y: float) -> List[Dict[str, Any]]:
        """
        生成人类点击行为
        
        Args:
            target_x: 目标X坐标
            target_y: 目标Y坐标
            
        Returns:
            点击事件列表
        """
        events = []
        
        # 点击前悬停（200-800ms随机）
        hover_time = random.uniform(200, 800) / 1000.0 * self._behavior_intensity
        events.append({
            "type": "hover",
            "x": target_x,
            "y": target_y,
            "duration": hover_time,
        })
        
        # 点击位置不是像素级精确（有±3px偏移）
        offset_x = (random.random() - 0.5) * 6
        offset_y = (random.random() - 0.5) * 6
        click_x = target_x + offset_x
        click_y = target_y + offset_y
        
        # mousedown
        events.append({
            "type": "mousedown",
            "x": click_x,
            "y": click_y,
            "button": 0,
        })
        
        # 点击时的微小鼠标移动（人手点击会微动）
        move_x = click_x + (random.random() - 0.5) * 2
        move_y = click_y + (random.random() - 0.5) * 2
        
        events.append({
            "type": "mousemove",
            "x": move_x,
            "y": move_y,
        })
        
        # mouseup
        events.append({
            "type": "mouseup",
            "x": move_x,
            "y": move_y,
            "button": 0,
        })
        
        # click
        events.append({
            "type": "click",
            "x": move_x,
            "y": move_y,
            "button": 0,
        })
        
        # 点击后等待（100-500ms随机）
        post_click_time = random.uniform(100, 500) / 1000.0
        events.append({
            "type": "post_click_pause",
            "duration": post_click_time,
        })
        
        self._mouse_x = target_x
        self._mouse_y = target_y
        
        return events
    
    def generate_mouse_path(self, start_x: float, start_y: float, 
                             end_x: float, end_y: float,
                             steps: int = 30) -> List[Tuple[float, float]]:
        """
        生成贝塞尔曲线鼠标路径
        
        Args:
            start_x: 起点X坐标
            start_y: 起点Y坐标
            end_x: 终点X坐标
            end_y: 终点Y坐标
            steps: 步数
            
        Returns:
            路径点列表
        """
        points = []
        
        # 生成两个控制点（贝塞尔曲线）
        dx = end_x - start_x
        dy = end_y - start_y
        distance = math.sqrt(dx * dx + dy * dy)
        
        # 控制点1
        cp1_x = start_x + dx * 0.3 + (random.random() - 0.5) * distance * 0.2
        cp1_y = start_y + dy * 0.3 + (random.random() - 0.5) * distance * 0.2
        
        # 控制点2
        cp2_x = start_x + dx * 0.7 + (random.random() - 0.5) * distance * 0.2
        cp2_y = start_y + dy * 0.7 + (random.random() - 0.5) * distance * 0.2
        
        for i in range(steps + 1):
            t = i / steps
            
            # 三阶贝塞尔曲线
            x = (1-t)**3 * start_x + 3*(1-t)**2 * t * cp1_x + 3*(1-t)*t**2 * cp2_x + t**3 * end_x
            y = (1-t)**3 * start_y + 3*(1-t)**2 * t * cp1_y + 3*(1-t)*t**2 * cp2_y + t**3 * end_y
            
            # 添加随机微小抖动（人手自然抖动）
            jitter_x = (random.random() - 0.5) * 2 * self._behavior_intensity
            jitter_y = (random.random() - 0.5) * 2 * self._behavior_intensity
            
            points.append((x + jitter_x, y + jitter_y))
        
        # 过冲现象（移动过头再回来）
        if random.random() < 0.3 * self._behavior_intensity:
            overshoot_x = end_x + (random.random() - 0.5) * 10
            overshoot_y = end_y + (random.random() - 0.5) * 10
            points.append((overshoot_x, overshoot_y))
            points.append((end_x, end_y))
        
        self._mouse_x = end_x
        self._mouse_y = end_y
        
        return points
    
    def simulate_reading(self, duration: float = 30.0) -> List[Dict[str, Any]]:
        """
        模拟阅读行为
        
        Args:
            duration: 阅读时长（秒）
            
        Returns:
            行为事件列表
        """
        events = []
        current_time = 0.0
        
        # 随机滚动几次
        num_scrolls = random.randint(3, 8)
        scroll_interval = duration / num_scrolls
        
        for i in range(num_scrolls):
            # 停顿（阅读）
            pause_time = scroll_interval * random.uniform(0.6, 0.9)
            events.append({
                "type": "reading_pause",
                "time": current_time,
                "duration": pause_time,
            })
            current_time += pause_time
            
            # 滚动
            scroll_distance = random.randint(100, 500)
            scroll_events = self.human_like_scroll(
                self._scroll_y + scroll_distance,
                steps=random.randint(10, 20)
            )
            
            for pos in scroll_events:
                events.append({
                    "type": "scroll",
                    "time": current_time,
                    "y": pos,
                })
                current_time += 0.05  # 每步50ms
            
            # 偶尔回滚（往上滚一点再往下）
            if random.random() < 0.2 * self._behavior_intensity:
                rollback_distance = random.randint(50, 150)
                rollback_events = self.human_like_scroll(
                    self._scroll_y - rollback_distance,
                    steps=random.randint(5, 10)
                )
                
                for pos in rollback_events:
                    events.append({
                        "type": "scroll_rollback",
                        "time": current_time,
                        "y": pos,
                    })
                    current_time += 0.05
                
                # 再滚回来
                scroll_back_events = self.human_like_scroll(
                    self._scroll_y + scroll_distance,
                    steps=random.randint(5, 10)
                )
                
                for pos in scroll_back_events:
                    events.append({
                        "type": "scroll",
                        "time": current_time,
                        "y": pos,
                    })
                    current_time += 0.05
        
        return events
    
    def random_mouse_movements(self, bounds: Tuple[int, int, int, int], 
                                duration: float = 10.0) -> List[Dict[str, Any]]:
        """
        生成随机鼠标移动
        
        Args:
            bounds: 边界 (x1, y1, x2, y2)
            duration: 持续时间（秒）
            
        Returns:
            鼠标移动事件列表
        """
        events = []
        current_time = 0.0
        x1, y1, x2, y2 = bounds
        
        num_movements = random.randint(5, 15)
        move_interval = duration / num_movements
        
        for i in range(num_movements):
            # 随机目标点
            target_x = random.uniform(x1, x2)
            target_y = random.uniform(y1, y2)
            
            # 生成路径
            path = self.generate_mouse_path(
                self._mouse_x, self._mouse_y,
                target_x, target_y,
                steps=random.randint(10, 30)
            )
            
            # 添加路径点
            step_time = move_interval * 0.6 / len(path)
            for px, py in path:
                events.append({
                    "type": "mousemove",
                    "time": current_time,
                    "x": px,
                    "y": py,
                })
                current_time += step_time
            
            # 停顿
            pause_time = move_interval * 0.4
            events.append({
                "type": "mouse_pause",
                "time": current_time,
                "duration": pause_time,
                "x": target_x,
                "y": target_y,
            })
            current_time += pause_time
        
        return events
    
    def get_page_stay_time(self, min_seconds: int = 30, max_seconds: int = 300) -> float:
        """
        获取页面停留时间
        
        Args:
            min_seconds: 最小秒数
            max_seconds: 最大秒数
            
        Returns:
            停留时间（秒）
        """
        # 使用对数正态分布，更符合真实用户行为
        mu = math.log((min_seconds + max_seconds) / 2)
        sigma = 0.5
        stay_time = random.lognormvariate(mu, sigma)
        
        return max(min_seconds, min(max_seconds, stay_time))
    
    def generate_browsing_path(self, pages: List[str], 
                                min_pages: int = 3,
                                max_pages: int = 10) -> List[str]:
        """
        生成浏览路径
        
        Args:
            pages: 可用页面列表
            min_pages: 最少浏览页数
            max_pages: 最多浏览页数
            
        Returns:
            浏览页面列表
        """
        if not pages:
            return []
        
        num_pages = random.randint(min_pages, min(max_pages, len(pages)))
        selected_pages = random.sample(pages, min(num_pages, len(pages)))
        
        # 偶尔返回上一页
        if random.random() < 0.3 * self._behavior_intensity and len(selected_pages) > 1:
            insert_pos = random.randint(1, len(selected_pages) - 1)
            selected_pages.insert(insert_pos, selected_pages[insert_pos - 1])
        
        return selected_pages
    
    def random_tab_switch(self, num_tabs: int = 3) -> List[Dict[str, Any]]:
        """
        生成随机标签页切换行为
        
        Args:
            num_tabs: 标签页数量
            
        Returns:
            切换事件列表
        """
        events = []
        num_switches = random.randint(1, 5)
        
        for i in range(num_switches):
            events.append({
                "type": "tab_switch",
                "from_tab": random.randint(0, num_tabs - 1),
                "to_tab": random.randint(0, num_tabs - 1),
                "duration": random.uniform(1, 10),
            })
        
        return events
    
    def get_click_delay(self) -> float:
        """获取点击延迟（秒）"""
        return random.uniform(0.2, 0.8) * self._behavior_intensity
    
    def get_random_pause(self, min_seconds: float = 0.5, max_seconds: float = 5.0) -> float:
        """获取随机暂停时间（秒）"""
        return random.uniform(min_seconds, max_seconds) * self._behavior_intensity
    
    def get_human_behavior_config(self) -> Dict[str, Any]:
        """获取真人行为配置"""
        return {
            "intensity": self._behavior_intensity,
            "typing_speed": {
                "min": 100,
                "max": 400,
                "unit": "ms_per_char",
            },
            "mouse_speed": {
                "min": 500,
                "max": 2000,
                "unit": "pixels_per_second",
            },
            "scroll_speed": {
                "min": 500,
                "max": 3000,
                "unit": "pixels_per_second",
            },
            "click_accuracy": 3.0,  # ±3像素
            "page_stay_time": {
                "min": 30,
                "max": 300,
                "unit": "seconds",
            },
            "error_rate": 0.07,  # 打字错误率
        }


# 全局实例
human_behavior_simulator = HumanBehaviorSimulator()
