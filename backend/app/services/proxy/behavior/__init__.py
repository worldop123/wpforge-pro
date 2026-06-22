"""
行为模拟模块
提供真人行为模拟功能，包括鼠标、点击、滚动、键盘等行为
"""
from app.services.proxy.behavior.mouse_behavior import MouseBehaviorSimulator
from app.services.proxy.behavior.click_behavior import ClickBehaviorSimulator
from app.services.proxy.behavior.scroll_behavior import ScrollBehaviorSimulator
from app.services.proxy.behavior.keyboard_behavior import KeyboardBehaviorSimulator
from app.services.proxy.behavior.browsing_behavior import BrowsingBehaviorSimulator
from app.services.proxy.behavior.interaction_behavior import InteractionBehaviorSimulator
from app.services.proxy.behavior.wordpress_behavior import WordPressBehaviorSimulator
from app.services.proxy.behavior.human_behavior import HumanBehaviorSimulator

__all__ = [
    "MouseBehaviorSimulator",
    "ClickBehaviorSimulator",
    "ScrollBehaviorSimulator",
    "KeyboardBehaviorSimulator",
    "BrowsingBehaviorSimulator",
    "InteractionBehaviorSimulator",
    "WordPressBehaviorSimulator",
    "HumanBehaviorSimulator",
]
