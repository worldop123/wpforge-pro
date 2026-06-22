"""
Event Listener - 事件接收

接收来自站点的事件，提供分类过滤、告警通知、日志记录等功能
"""

import asyncio
from typing import Optional, Dict, Any, List, Callable
from datetime import datetime, timedelta
from collections import defaultdict

from loguru import logger

from .relay_client import RelayClient


class EventListener:
    """事件监听器"""

    def __init__(self, relay_client: RelayClient):
        """
        初始化事件监听器

        Args:
            relay_client: 中转客户端实例
        """
        self.relay_client = relay_client

        # 事件历史
        self._event_history: List[Dict[str, Any]] = []
        self._max_history = 1000

        # 事件统计
        self._event_stats: Dict[str, int] = defaultdict(int)

        # 告警规则
        self._alert_rules: List[Dict[str, Any]] = []

        # 事件回调
        self._event_handlers: Dict[str, List[Callable]] = defaultdict(list)

        # 注册事件监听
        self._register_event_handlers()

        logger.info("Event listener initialized")

    def _register_event_handlers(self):
        """注册事件处理器"""
        # 监听所有事件
        self.relay_client.on("*", self._on_event)

    async def _on_event(self, data: Dict[str, Any]):
        """处理接收到的事件"""
        event_type = data.get("event", "unknown")
        source_id = data.get("sourceId", "unknown")

        # 记录事件
        event_record = {
            "event": event_type,
            "source": source_id,
            "data": data.get("data", {}),
            "timestamp": data.get("timestamp", datetime.utcnow().isoformat()),
            "received_at": datetime.utcnow().isoformat(),
        }

        # 添加到历史
        self._event_history.append(event_record)
        if len(self._event_history) > self._max_history:
            self._event_history.pop(0)

        # 更新统计
        self._event_stats[event_type] += 1

        # 检查告警规则
        await self._check_alerts(event_record)

        # 触发事件回调
        await self._trigger_event_handlers(event_type, event_record)

        logger.debug(f"Event received: {event_type} from {source_id}")

    async def _check_alerts(self, event: Dict[str, Any]):
        """检查告警规则"""
        event_type = event.get("event", "")

        for rule in self._alert_rules:
            # 检查事件类型匹配
            if rule.get("event_type") and rule["event_type"] != event_type:
                continue

            # 检查条件
            if not self._check_alert_condition(rule, event):
                continue

            # 触发告警
            await self._trigger_alert(rule, event)

    def _check_alert_condition(self, rule: Dict[str, Any], event: Dict[str, Any]) -> bool:
        """检查告警条件"""
        condition = rule.get("condition", {})
        event_data = event.get("data", {})

        # 简单的条件匹配
        for key, value in condition.items():
            if key not in event_data:
                return False
            if str(event_data[key]) != str(value):
                return False

        return True

    async def _trigger_alert(self, rule: Dict[str, Any], event: Dict[str, Any]):
        """触发告警"""
        alert_name = rule.get("name", "Unknown Alert")
        logger.warning(f"Alert triggered: {alert_name}")

        # 调用告警回调
        callback = rule.get("callback")
        if callback:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(rule, event)
                else:
                    callback(rule, event)
            except Exception as e:
                logger.error(f"Error in alert callback: {e}")

    async def _trigger_event_handlers(self, event_type: str, event: Dict[str, Any]):
        """触发事件回调"""
        # 特定事件类型的回调
        if event_type in self._event_handlers:
            for handler in self._event_handlers[event_type]:
                try:
                    if asyncio.iscoroutinefunction(handler):
                        await handler(event)
                    else:
                        handler(event)
                except Exception as e:
                    logger.error(f"Error in event handler for {event_type}: {e}")

        # 通用事件回调
        if "*" in self._event_handlers:
            for handler in self._event_handlers["*"]:
                try:
                    if asyncio.iscoroutinefunction(handler):
                        await handler(event)
                    else:
                        handler(event)
                except Exception as e:
                    logger.error(f"Error in wildcard event handler: {e}")

    def on_event(self, event_type: str, handler: Callable):
        """
        注册事件监听器

        Args:
            event_type: 事件类型，使用"*"监听所有事件
            handler: 事件处理函数
        """
        self._event_handlers[event_type].append(handler)

    def off_event(self, event_type: str, handler: Optional[Callable] = None):
        """
        移除事件监听器

        Args:
            event_type: 事件类型
            handler: 事件处理函数，如果为None则移除所有
        """
        if event_type in self._event_handlers:
            if handler is None:
                del self._event_handlers[event_type]
            else:
                self._event_handlers[event_type] = [
                    h for h in self._event_handlers[event_type] if h != handler
                ]

    def add_alert_rule(
        self,
        name: str,
        event_type: str,
        condition: Optional[Dict[str, Any]] = None,
        callback: Optional[Callable] = None,
        level: str = "warning",
    ):
        """
        添加告警规则

        Args:
            name: 告警名称
            event_type: 事件类型
            condition: 条件
            callback: 告警回调
            level: 告警级别
        """
        rule = {
            "name": name,
            "event_type": event_type,
            "condition": condition or {},
            "callback": callback,
            "level": level,
            "created_at": datetime.utcnow().isoformat(),
        }

        self._alert_rules.append(rule)
        logger.info(f"Alert rule added: {name}")

    def remove_alert_rule(self, name: str):
        """
        移除告警规则

        Args:
            name: 告警名称
        """
        self._alert_rules = [r for r in self._alert_rules if r.get("name") != name]
        logger.info(f"Alert rule removed: {name}")

    def get_event_history(
        self,
        event_type: Optional[str] = None,
        source_id: Optional[str] = None,
        limit: int = 100,
        since: Optional[datetime] = None,
    ) -> List[Dict[str, Any]]:
        """
        获取事件历史

        Args:
            event_type: 按事件类型筛选
            source_id: 按来源筛选
            limit: 返回数量限制
            since: 从指定时间开始

        Returns:
            事件列表
        """
        events = self._event_history.copy()

        # 反向排序，最新的在前
        events.reverse()

        # 筛选
        if event_type:
            events = [e for e in events if e.get("event") == event_type]

        if source_id:
            events = [e for e in events if e.get("source") == source_id]

        if since:
            since_str = since.isoformat()
            events = [e for e in events if e.get("received_at", "") >= since_str]

        # 限制数量
        if limit:
            events = events[:limit]

        return events

    def get_event_stats(self) -> Dict[str, int]:
        """
        获取事件统计

        Returns:
            各类型事件数量统计
        """
        return dict(self._event_stats)

    def get_event_count(self, event_type: Optional[str] = None) -> int:
        """
        获取事件数量

        Args:
            event_type: 事件类型，为None则返回总数

        Returns:
            事件数量
        """
        if event_type:
            return self._event_stats.get(event_type, 0)
        return sum(self._event_stats.values())

    def clear_history(self):
        """清除事件历史"""
        self._event_history.clear()
        self._event_stats.clear()
        logger.info("Event history cleared")

    @property
    def alert_rules(self) -> List[Dict[str, Any]]:
        """所有告警规则"""
        return self._alert_rules.copy()

    @property
    def event_history(self) -> List[Dict[str, Any]]:
        """事件历史"""
        return self._event_history.copy()
