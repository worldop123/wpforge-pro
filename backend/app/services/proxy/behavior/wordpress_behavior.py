"""
WordPress后台操作行为模拟器
提供WordPress后台操作的专项行为模拟
"""
import random
from typing import List, Dict, Any, Optional

from app.core.logging import get_logger
from app.services.proxy.behavior.human_behavior import HumanBehaviorSimulator

logger = get_logger(__name__)


class WordPressBehaviorSimulator:
    """WordPress后台操作行为模拟器"""
    
    def __init__(self, base_simulator: Optional[HumanBehaviorSimulator] = None):
        self._base = base_simulator or HumanBehaviorSimulator()
    
    def simulate_login(self, username: str, password: str) -> List[Dict[str, Any]]:
        """
        模拟WordPress登录行为
        
        Args:
            username: 用户名
            password: 密码
            
        Returns:
            登录事件列表
        """
        events = []
        
        # 登录页加载完成后等待
        events.append({
            "type": "page_load",
            "page": "wp-login.php",
            "duration": random.uniform(1.0, 2.0),
        })
        
        # 随机停顿（观察页面）
        events.append({
            "type": "pause",
            "duration": random.uniform(1.0, 3.0),
            "description": "观察登录页面",
        })
        
        # 点击用户名输入框
        events.append({
            "type": "click",
            "target": "#user_login",
            "description": "点击用户名输入框",
        })
        
        # 输入用户名
        username_events = self._base.human_like_type(username, base_speed=180)
        for event in username_events:
            event["target"] = "#user_login"
        events.extend(username_events)
        
        # 停顿
        events.append({
            "type": "pause",
            "duration": random.uniform(0.3, 1.0),
        })
        
        # 点击密码输入框
        events.append({
            "type": "click",
            "target": "#user_pass",
            "description": "点击密码输入框",
        })
        
        # 输入密码（密码通常输入更快，因为是肌肉记忆）
        password_events = self._base.human_like_type(password, base_speed=120)
        for event in password_events:
            event["target"] = "#user_pass"
        events.extend(password_events)
        
        # 停顿（思考是否记住密码）
        events.append({
            "type": "pause",
            "duration": random.uniform(0.5, 2.0),
        })
        
        # 随机选择是否勾选"记住我"
        if random.random() < 0.3:
            events.append({
                "type": "click",
                "target": "#rememberme",
                "description": "勾选记住我",
            })
            events.append({
                "type": "pause",
                "duration": random.uniform(0.3, 0.8),
            })
        
        # 点击登录按钮前的随机停顿
        events.append({
            "type": "pause",
            "duration": random.uniform(0.2, 1.0),
            "description": "点击登录前的停顿",
        })
        
        # 点击登录按钮
        events.append({
            "type": "click",
            "target": "#wp-submit",
            "description": "点击登录按钮",
        })
        
        # 等待登录重定向
        events.append({
            "type": "page_load",
            "page": "wp-admin/index.php",
            "duration": random.uniform(1.5, 3.5),
            "description": "等待登录重定向",
        })
        
        return events
    
    def simulate_dashboard_view(self) -> List[Dict[str, Any]]:
        """模拟查看仪表盘"""
        events = []
        
        # 页面加载
        events.append({
            "type": "page_load",
            "page": "wp-admin/index.php",
            "duration": random.uniform(1.0, 2.5),
        })
        
        # 查看仪表盘（滚动浏览）
        events.append({
            "type": "pause",
            "duration": random.uniform(2.0, 5.0),
            "description": "查看仪表盘概览",
        })
        
        # 随机滚动
        if random.random() < 0.5:
            events.append({
                "type": "scroll",
                "distance": random.randint(200, 500),
                "direction": "down",
            })
            events.append({
                "type": "pause",
                "duration": random.uniform(1.0, 3.0),
            })
        
        return events
    
    def simulate_menu_navigation(self, menu_item: str) -> List[Dict[str, Any]]:
        """
        模拟左侧菜单导航
        
        Args:
            menu_item: 菜单项名称
            
        Returns:
            导航事件列表
        """
        events = []
        
        # 移动鼠标到菜单项
        events.append({
            "type": "mousemove",
            "target": f"#menu-{menu_item}",
            "description": "移动鼠标到菜单项",
        })
        
        # 悬停（等待子菜单展开）
        events.append({
            "type": "hover",
            "target": f"#menu-{menu_item}",
            "duration": random.uniform(0.3, 0.8),
            "description": "悬停等待子菜单展开",
        })
        
        # 点击子菜单项
        events.append({
            "type": "click",
            "target": f"#menu-{menu_item} .wp-submenu li a",
            "description": "点击子菜单项",
        })
        
        # 等待页面加载
        events.append({
            "type": "page_load",
            "duration": random.uniform(1.0, 2.5),
        })
        
        return events
    
    def simulate_post_editor(self, title: str, content: str) -> List[Dict[str, Any]]:
        """
        模拟文章编辑
        
        Args:
            title: 文章标题
            content: 文章内容
            
        Returns:
            编辑事件列表
        """
        events = []
        
        # 页面加载
        events.append({
            "type": "page_load",
            "page": "wp-admin/post.php",
            "duration": random.uniform(1.5, 3.0),
        })
        
        # 等待编辑器初始化
        events.append({
            "type": "pause",
            "duration": random.uniform(1.0, 2.0),
            "description": "等待编辑器初始化",
        })
        
        # 点击标题输入框
        events.append({
            "type": "click",
            "target": "#title",
            "description": "点击标题输入框",
        })
        
        # 输入标题
        title_events = self._base.human_like_type(title, base_speed=150)
        for event in title_events:
            event["target"] = "#title"
        events.extend(title_events)
        
        # 停顿（思考内容）
        events.append({
            "type": "pause",
            "duration": random.uniform(1.0, 3.0),
            "description": "思考文章内容",
        })
        
        # 点击内容编辑器
        events.append({
            "type": "click",
            "target": "#content",
            "description": "点击内容编辑器",
        })
        
        # 输入内容（分段输入，中间有停顿）
        paragraphs = content.split("\n\n")
        for i, para in enumerate(paragraphs):
            if not para.strip():
                continue
            
            # 输入段落
            para_events = self._base.human_like_type(para, base_speed=180)
            for event in para_events:
                event["target"] = "#content"
            events.extend(para_events)
            
            # 段落间停顿
            if i < len(paragraphs) - 1:
                events.append({
                    "type": "pause",
                    "duration": random.uniform(0.5, 2.0),
                    "description": "段落间思考",
                })
                
                # 输入换行
                events.append({
                    "type": "keydown",
                    "key": "Enter",
                    "target": "#content",
                })
                events.append({
                    "type": "keyup",
                    "key": "Enter",
                    "target": "#content",
                })
        
        return events
    
    def simulate_publish_post(self) -> List[Dict[str, Any]]:
        """模拟发布文章"""
        events = []
        
        # 发布前预览（可选）
        if random.random() < 0.4:
            events.append({
                "type": "click",
                "target": "#post-preview",
                "description": "点击预览按钮",
            })
            
            events.append({
                "type": "page_load",
                "duration": random.uniform(1.0, 2.0),
                "description": "等待预览页面加载",
            })
            
            # 浏览预览
            events.append({
                "type": "pause",
                "duration": random.uniform(3.0, 8.0),
                "description": "浏览预览页面",
            })
            
            # 返回编辑器
            events.append({
                "type": "page_back",
                "description": "返回编辑器",
            })
            events.append({
                "type": "page_load",
                "duration": random.uniform(0.5, 1.5),
            })
        
        # 点击发布按钮
        events.append({
            "type": "click",
            "target": "#publish",
            "description": "点击发布按钮",
        })
        
        # 等待发布完成
        events.append({
            "type": "pause",
            "duration": random.uniform(1.0, 3.0),
            "description": "等待发布完成",
        })
        
        # 查看成功提示
        events.append({
            "type": "pause",
            "duration": random.uniform(1.0, 2.0),
            "description": "查看发布成功提示",
        })
        
        return events
    
    def simulate_operation_pause(self, min_seconds: int = 3, 
                                  max_seconds: int = 15) -> float:
        """
        获取操作间隔（模拟思考时间）
        
        Args:
            min_seconds: 最小秒数
            max_seconds: 最大秒数
            
        Returns:
            暂停时间（秒）
        """
        return random.uniform(min_seconds, max_seconds)
    
    def simulate_random_page_visit(self, admin_pages: List[str]) -> List[Dict[str, Any]]:
        """
        模拟随机访问其他页面（模拟真实管理员的行为）
        
        Args:
            admin_pages: 可用的管理页面列表
            
        Returns:
            访问事件列表
        """
        events = []
        
        # 随机选择1-3个页面访问
        num_pages = random.randint(1, 3)
        selected_pages = random.sample(admin_pages, min(num_pages, len(admin_pages)))
        
        for page in selected_pages:
            # 导航到页面
            events.append({
                "type": "page_navigation",
                "page": page,
            })
            
            # 页面加载
            events.append({
                "type": "page_load",
                "duration": random.uniform(1.0, 2.5),
            })
            
            # 浏览页面
            events.append({
                "type": "pause",
                "duration": random.uniform(5.0, 20.0),
                "description": f"浏览{page}",
            })
            
            # 偶尔滚动
            if random.random() < 0.5:
                events.append({
                    "type": "scroll",
                    "distance": random.randint(200, 600),
                    "direction": "down",
                })
                events.append({
                    "type": "pause",
                    "duration": random.uniform(2.0, 5.0),
                })
        
        return events
    
    def simulate_refresh(self) -> List[Dict[str, Any]]:
        """模拟刷新页面"""
        events = []
        
        events.append({
            "type": "page_refresh",
            "description": "刷新页面",
        })
        
        events.append({
            "type": "page_load",
            "duration": random.uniform(1.0, 2.5),
        })
        
        return events
    
    def get_admin_operation_interval(self) -> float:
        """获取后台操作间隔（秒）"""
        return random.uniform(3.0, 15.0)
    
    def is_working_hours(self, hour: int, timezone: str = "Asia/Shanghai") -> bool:
        """
        判断是否是工作时间
        
        Args:
            hour: 当前小时（24小时制）
            timezone: 时区
            
        Returns:
            是否是工作时间
        """
        # 典型工作时间 9:00 - 18:00
        return 9 <= hour <= 18
