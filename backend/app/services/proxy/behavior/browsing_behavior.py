"""
浏览行为模拟器
提供浏览路径和页面停留等行为的模拟功能
"""
import random
from typing import List, Dict, Any, Optional

from app.core.logging import get_logger
from app.services.proxy.behavior.human_behavior import HumanBehaviorSimulator

logger = get_logger(__name__)


class BrowsingBehaviorSimulator:
    """浏览行为模拟器"""
    
    def __init__(self, base_simulator: Optional[HumanBehaviorSimulator] = None):
        self._base = base_simulator or HumanBehaviorSimulator()
    
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
        return self._base.generate_browsing_path(pages, min_pages, max_pages)
    
    def get_page_stay_time(self, page_type: str = "normal") -> float:
        """
        获取页面停留时间
        
        Args:
            page_type: 页面类型（home/product/article/category等）
            
        Returns:
            停留时间（秒）
        """
        time_ranges = {
            "home": (10, 60),
            "product": (30, 180),
            "article": (60, 300),
            "category": (20, 120),
            "checkout": (60, 300),
            "search": (15, 90),
            "normal": (30, 300),
        }
        
        min_time, max_time = time_ranges.get(page_type, (30, 300))
        return self._base.get_page_stay_time(min_time, max_time)
    
    def simulate_browsing_session(self, pages: List[str],
                                   min_pages: int = 3,
                                   max_pages: int = 8) -> List[Dict[str, Any]]:
        """
        模拟完整的浏览会话
        
        Args:
            pages: 可用页面列表
            min_pages: 最少浏览页数
            max_pages: 最多浏览页数
            
        Returns:
            浏览会话事件列表
        """
        events = []
        
        # 生成浏览路径
        path = self.generate_browsing_path(pages, min_pages, max_pages)
        
        for i, page in enumerate(path):
            # 页面加载等待
            load_time = random.uniform(1.0, 3.0)
            events.append({
                "type": "page_load",
                "page": page,
                "duration": load_time,
            })
            
            # 页面停留
            page_type = self._guess_page_type(page)
            stay_time = self.get_page_stay_time(page_type)
            events.append({
                "type": "page_stay",
                "page": page,
                "duration": stay_time,
            })
            
            # 页面内行为（滚动、点击等）
            page_events = self._generate_page_interactions(page, page_type)
            events.extend(page_events)
            
            # 页面间跳转间隔
            if i < len(path) - 1:
                transition_time = random.uniform(0.5, 2.0)
                events.append({
                    "type": "page_transition",
                    "from_page": page,
                    "to_page": path[i + 1],
                    "duration": transition_time,
                })
                
                # 偶尔返回上一页
                if random.random() < 0.2 and i > 0:
                    back_time = random.uniform(0.5, 1.5)
                    events.append({
                        "type": "page_back",
                        "from_page": path[i + 1],
                        "to_page": page,
                        "duration": back_time,
                    })
        
        return events
    
    def _guess_page_type(self, page_url: str) -> str:
        """根据URL猜测页面类型"""
        url_lower = page_url.lower()
        
        if any(keyword in url_lower for keyword in ["/product/", "/item/", "/p/"]):
            return "product"
        elif any(keyword in url_lower for keyword in ["/category/", "/c/", "/collection/"]):
            return "category"
        elif any(keyword in url_lower for keyword in ["/blog/", "/article/", "/news/"]):
            return "article"
        elif any(keyword in url_lower for keyword in ["/checkout", "/cart", "/basket"]):
            return "checkout"
        elif any(keyword in url_lower for keyword in ["/search", "?s=", "?q="]):
            return "search"
        elif any(keyword in url_lower for keyword in ["/home", "index.html", "/"]) and len(url_lower) < 10:
            return "home"
        else:
            return "normal"
    
    def _generate_page_interactions(self, page: str, page_type: str) -> List[Dict[str, Any]]:
        """生成页面内交互事件"""
        events = []
        
        # 滚动行为
        num_scrolls = random.randint(1, 5)
        for _ in range(num_scrolls):
            scroll_distance = random.randint(100, 500)
            events.append({
                "type": "scroll",
                "distance": scroll_distance,
                "direction": "down",
            })
            
            # 滚动后停顿
            pause_time = random.uniform(1.0, 5.0)
            events.append({
                "type": "pause",
                "duration": pause_time,
            })
        
        # 随机点击
        if random.random() < 0.5:
            num_clicks = random.randint(1, 3)
            for _ in range(num_clicks):
                events.append({
                    "type": "click",
                    "element": "random_element",
                })
                
                click_pause = random.uniform(0.5, 2.0)
                events.append({
                    "type": "pause",
                    "duration": click_pause,
                })
        
        return events
    
    def random_tab_switch(self, num_tabs: int = 3) -> List[Dict[str, Any]]:
        """生成随机标签页切换行为"""
        return self._base.random_tab_switch(num_tabs)
    
    def simulate_return_visitor(self, pages: List[str]) -> List[Dict[str, Any]]:
        """模拟回访用户的浏览行为"""
        # 回访用户通常浏览页数更少，但停留时间更长
        events = self.simulate_browsing_session(
            pages,
            min_pages=2,
            max_pages=5
        )
        
        # 增加停留时间
        for event in events:
            if event["type"] == "page_stay":
                event["duration"] *= 1.5
        
        return events
    
    def simulate_new_visitor(self, pages: List[str]) -> List[Dict[str, Any]]:
        """模拟新用户的浏览行为"""
        # 新用户通常浏览更多页面，但停留时间更短
        events = self.simulate_browsing_session(
            pages,
            min_pages=4,
            max_pages=10
        )
        
        # 减少停留时间
        for event in events:
            if event["type"] == "page_stay":
                event["duration"] *= 0.8
        
        return events
