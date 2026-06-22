"""
页面交互行为模拟器
提供表单填写、下拉选择、复选框等交互行为的模拟
"""
import random
from typing import List, Dict, Any, Optional

from app.core.logging import get_logger
from app.services.proxy.behavior.human_behavior import HumanBehaviorSimulator

logger = get_logger(__name__)


class InteractionBehaviorSimulator:
    """页面交互行为模拟器"""
    
    def __init__(self, base_simulator: Optional[HumanBehaviorSimulator] = None):
        self._base = base_simulator or HumanBehaviorSimulator()
    
    def fill_form(self, fields: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        模拟表单填写
        
        Args:
            fields: 字段列表，每个字段包含name, value, type等
            
        Returns:
            交互事件列表
        """
        events = []
        
        for i, field in enumerate(fields):
            field_type = field.get("type", "text")
            field_name = field.get("name", f"field_{i}")
            field_value = field.get("value", "")
            
            # 点击字段（聚焦）
            events.append({
                "type": "click",
                "target": f"input[name='{field_name}']",
                "action": "focus",
            })
            
            # 输入内容
            if field_type == "text" or field_type == "email" or field_type == "password":
                type_events = self._base.human_like_type(str(field_value))
                for event in type_events:
                    event["target"] = f"input[name='{field_name}']"
                events.extend(type_events)
            elif field_type == "select":
                # 下拉选择
                select_events = self._simulate_select(field_value)
                for event in select_events:
                    event["target"] = f"select[name='{field_name}']"
                events.extend(select_events)
            elif field_type == "checkbox":
                # 复选框
                if field_value:
                    events.append({
                        "type": "click",
                        "target": f"input[name='{field_name}']",
                        "action": "check",
                    })
            elif field_type == "radio":
                # 单选框
                events.append({
                    "type": "click",
                    "target": f"input[name='{field_name}'][value='{field_value}']",
                    "action": "select",
                })
            
            # 字段间停顿
            if i < len(fields) - 1:
                pause_time = random.uniform(0.3, 1.5)
                events.append({
                    "type": "pause",
                    "duration": pause_time,
                })
        
        return events
    
    def _simulate_select(self, value: str) -> List[Dict[str, Any]]:
        """模拟下拉选择"""
        events = []
        
        # 点击展开下拉
        events.append({
            "type": "click",
            "action": "open_select",
        })
        
        # 短暂停顿
        events.append({
            "type": "pause",
            "duration": random.uniform(0.2, 0.5),
        })
        
        # 模拟滚动选项
        if random.random() < 0.3:
            events.append({
                "type": "scroll",
                "target": "select_options",
                "direction": "down",
            })
            events.append({
                "type": "pause",
                "duration": random.uniform(0.1, 0.3),
            })
        
        # 点击选项
        events.append({
            "type": "click",
            "action": "select_option",
            "value": value,
        })
        
        return events
    
    def simulate_checkbox(self, checked: bool = True) -> List[Dict[str, Any]]:
        """模拟复选框操作"""
        events = []
        
        # 悬停
        events.append({
            "type": "hover",
            "duration": random.uniform(0.2, 0.5),
        })
        
        # 点击
        events.append({
            "type": "click",
            "action": "check" if checked else "uncheck",
        })
        
        return events
    
    def simulate_radio(self) -> List[Dict[str, Any]]:
        """模拟单选框操作"""
        events = []
        
        # 悬停
        events.append({
            "type": "hover",
            "duration": random.uniform(0.2, 0.5),
        })
        
        # 点击
        events.append({
            "type": "click",
            "action": "select",
        })
        
        return events
    
    def simulate_slider(self, value: float, min_value: float = 0, 
                        max_value: float = 100) -> List[Dict[str, Any]]:
        """模拟滑块拖动"""
        events = []
        
        # 计算位置
        position = (value - min_value) / (max_value - min_value)
        
        # 点击滑块
        events.append({
            "type": "mousedown",
            "target": "slider_thumb",
        })
        
        # 拖动
        steps = random.randint(5, 15)
        for i in range(steps + 1):
            t = i / steps
            # 缓动效果
            if t < 0.3:
                eased = (t / 0.3) ** 2
            elif t > 0.7:
                eased = 1 - ((1 - (t - 0.7) / 0.3) ** 2)
            else:
                eased = 0.09 + (t - 0.3) * 0.91 / 0.4
            
            current_pos = position * eased
            
            events.append({
                "type": "mousemove",
                "target": "slider_track",
                "position": current_pos,
            })
        
        # 释放
        events.append({
            "type": "mouseup",
            "target": "slider_thumb",
        })
        
        return events
    
    def simulate_file_upload(self) -> List[Dict[str, Any]]:
        """模拟文件上传操作"""
        events = []
        
        # 点击上传按钮
        events.append({
            "type": "click",
            "target": "upload_button",
        })
        
        # 等待文件选择对话框（模拟）
        events.append({
            "type": "pause",
            "duration": random.uniform(1.0, 3.0),
        })
        
        # 文件选择完成
        events.append({
            "type": "file_selected",
            "filename": "example_file.jpg",
        })
        
        # 上传进度
        upload_duration = random.uniform(2.0, 5.0)
        events.append({
            "type": "upload_start",
            "duration": upload_duration,
        })
        
        # 上传完成
        events.append({
            "type": "upload_complete",
        })
        
        return events
    
    def simulate_modal_close(self) -> List[Dict[str, Any]]:
        """模拟弹窗关闭"""
        events = []
        
        # 短暂阅读
        events.append({
            "type": "pause",
            "duration": random.uniform(1.0, 3.0),
        })
        
        # 点击关闭按钮
        events.append({
            "type": "click",
            "target": "modal_close_button",
        })
        
        # 等待弹窗消失
        events.append({
            "type": "pause",
            "duration": random.uniform(0.3, 0.8),
        })
        
        return events
    
    def simulate_hover(self, duration: Optional[float] = None) -> List[Dict[str, Any]]:
        """模拟悬停"""
        if duration is None:
            duration = random.uniform(0.2, 1.0)
        
        return [{
            "type": "hover",
            "duration": duration,
        }]
    
    def get_random_pause(self, min_seconds: float = 0.5, 
                         max_seconds: float = 5.0) -> float:
        """获取随机暂停时间"""
        return self._base.get_random_pause(min_seconds, max_seconds)
