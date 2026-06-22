"""
Message Center - 消息中心

提供消息历史查询、筛选、重发等功能
"""

import asyncio
import uuid
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from collections import defaultdict

from loguru import logger

from .relay_client import RelayClient


class MessageCenter:
    """消息中心"""

    def __init__(self, relay_client: RelayClient):
        """
        初始化消息中心

        Args:
            relay_client: 中转客户端实例
        """
        self.relay_client = relay_client

        # 消息历史
        self._message_history: List[Dict[str, Any]] = []
        self._max_history = 5000

        # 消息统计
        self._message_stats: Dict[str, int] = defaultdict(int)

        # 待确认的消息
        self._pending_messages: Dict[str, Dict[str, Any]] = {}

        logger.info("Message center initialized")

    def record_message(
        self,
        message_type: str,
        direction: str,
        message: Dict[str, Any],
    ):
        """
        记录消息

        Args:
            message_type: 消息类型 (command/event/response/broadcast)
            direction: 方向 (sent/received)
            message: 消息内容
        """
        message_id = message.get("messageId", str(uuid.uuid4()))

        record = {
            "message_id": message_id,
            "message_type": message_type,
            "direction": direction,
            "message": message,
            "timestamp": datetime.utcnow().isoformat(),
            "status": "sent" if direction == "sent" else "received",
        }

        # 添加到历史
        self._message_history.append(record)
        if len(self._message_history) > self._max_history:
            self._message_history.pop(0)

        # 更新统计
        self._message_stats[message_type] += 1
        self._message_stats[f"{direction}_{message_type}"] += 1

        logger.debug(
            f"Message recorded: {direction} {message_type} ({message_id})"
        )

    def get_message_history(
        self,
        message_type: Optional[str] = None,
        direction: Optional[str] = None,
        source_id: Optional[str] = None,
        target_id: Optional[str] = None,
        limit: int = 100,
        since: Optional[datetime] = None,
        until: Optional[datetime] = None,
    ) -> List[Dict[str, Any]]:
        """
        获取消息历史

        Args:
            message_type: 按消息类型筛选
            direction: 按方向筛选
            source_id: 按来源筛选
            target_id: 按目标筛选
            limit: 返回数量限制
            since: 从指定时间开始
            until: 到指定时间结束

        Returns:
            消息列表
        """
        messages = self._message_history.copy()

        # 反向排序，最新的在前
        messages.reverse()

        # 筛选
        if message_type:
            messages = [m for m in messages if m.get("message_type") == message_type]

        if direction:
            messages = [m for m in messages if m.get("direction") == direction]

        if source_id:
            messages = [
                m
                for m in messages
                if m.get("message", {}).get("sourceId") == source_id
            ]

        if target_id:
            messages = [
                m
                for m in messages
                if m.get("message", {}).get("targetId") == target_id
            ]

        if since:
            since_str = since.isoformat()
            messages = [m for m in messages if m.get("timestamp", "") >= since_str]

        if until:
            until_str = until.isoformat()
            messages = [m for m in messages if m.get("timestamp", "") <= until_str]

        # 限制数量
        if limit:
            messages = messages[:limit]

        return messages

    def get_message_stats(self) -> Dict[str, int]:
        """
        获取消息统计

        Returns:
            消息统计数据
        """
        stats = dict(self._message_stats)
        stats["total"] = len(self._message_history)
        return stats

    def get_message_count(
        self,
        message_type: Optional[str] = None,
        direction: Optional[str] = None,
    ) -> int:
        """
        获取消息数量

        Args:
            message_type: 消息类型
            direction: 方向

        Returns:
            消息数量
        """
        if message_type and direction:
            return self._message_stats.get(f"{direction}_{message_type}", 0)
        elif message_type:
            return self._message_stats.get(message_type, 0)
        elif direction:
            return sum(
                v
                for k, v in self._message_stats.items()
                if k.startswith(f"{direction}_")
            )
        return len(self._message_history)

    async def resend_message(self, message_id: str) -> bool:
        """
        重发消息

        Args:
            message_id: 消息ID

        Returns:
            是否重发成功
        """
        # 查找原始消息
        original_message = None
        for msg in self._message_history:
            if msg.get("message_id") == message_id:
                original_message = msg
                break

        if not original_message:
            logger.warning(f"Message not found: {message_id}")
            return False

        # 只能重发发送的消息
        if original_message.get("direction") != "sent":
            logger.warning(f"Cannot resend received message: {message_id}")
            return False

        message = original_message.get("message", {})
        message_type = original_message.get("message_type")

        try:
            if message_type == "event":
                await self.relay_client.send_event(
                    event_type=message.get("event", ""),
                    event_data=message.get("data", {}),
                )
            elif message_type == "command":
                # 命令需要重新生成ID
                await self.relay_client.send_command(
                    target_id=message.get("targetId", ""),
                    command=message.get("command", ""),
                    params=message.get("params", {}),
                )
            elif message_type == "broadcast":
                await self.relay_client.send_broadcast(
                    event_type=message.get("event", ""),
                    event_data=message.get("data", {}),
                )
            else:
                logger.warning(f"Unsupported message type for resend: {message_type}")
                return False

            # 记录重发的消息
            self.record_message(message_type, "sent", message)

            logger.info(f"Message resent: {message_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to resend message: {e}")
            return False

    def clear_history(self):
        """清除消息历史"""
        self._message_history.clear()
        self._message_stats.clear()
        logger.info("Message history cleared")

    def get_pending_messages(self) -> List[Dict[str, Any]]:
        """
        获取待处理消息

        Returns:
            待处理消息列表
        """
        return list(self._pending_messages.values())

    def add_pending_message(self, message: Dict[str, Any]):
        """
        添加待处理消息

        Args:
            message: 消息内容
        """
        message_id = message.get("messageId", str(uuid.uuid4()))
        self._pending_messages[message_id] = {
            "message": message,
            "added_at": datetime.utcnow().isoformat(),
        }

    def remove_pending_message(self, message_id: str):
        """
        移除待处理消息

        Args:
            message_id: 消息ID
        """
        if message_id in self._pending_messages:
            del self._pending_messages[message_id]

    def get_message_by_id(self, message_id: str) -> Optional[Dict[str, Any]]:
        """
        根据ID获取消息

        Args:
            message_id: 消息ID

        Returns:
            消息内容
        """
        for msg in self._message_history:
            if msg.get("message_id") == message_id:
                return msg
        return None

    def search_messages(self, keyword: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        搜索消息

        Args:
            keyword: 搜索关键词
            limit: 返回数量限制

        Returns:
            匹配的消息列表
        """
        keyword_lower = keyword.lower()
        results = []

        for msg in reversed(self._message_history):
            # 在消息内容中搜索
            message_str = str(msg.get("message", "")).lower()
            if keyword_lower in message_str:
                results.append(msg)
                if len(results) >= limit:
                    break

        return results

    def get_message_summary(self, days: int = 7) -> Dict[str, Any]:
        """
        获取消息汇总

        Args:
            days: 统计天数

        Returns:
            消息汇总数据
        """
        since = datetime.utcnow() - timedelta(days=days)
        since_str = since.isoformat()

        # 筛选时间范围内的消息
        recent_messages = [
            m for m in self._message_history if m.get("timestamp", "") >= since_str
        ]

        # 按天统计
        daily_stats = defaultdict(lambda: {"sent": 0, "received": 0, "total": 0})

        for msg in recent_messages:
            timestamp = msg.get("timestamp", "")
            if timestamp:
                day = timestamp[:10]  # YYYY-MM-DD
                direction = msg.get("direction", "unknown")
                daily_stats[day][direction] += 1
                daily_stats[day]["total"] += 1

        # 按类型统计
        type_stats = defaultdict(int)
        for msg in recent_messages:
            msg_type = msg.get("message_type", "unknown")
            type_stats[msg_type] += 1

        return {
            "period_days": days,
            "total_messages": len(recent_messages),
            "daily_stats": dict(daily_stats),
            "type_stats": dict(type_stats),
        }

    @property
    def message_history(self) -> List[Dict[str, Any]]:
        """消息历史"""
        return self._message_history.copy()

    @property
    def total_messages(self) -> int:
        """消息总数"""
        return len(self._message_history)
