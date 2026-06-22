"""
Relay Client - 中转服务器WebSocket客户端

负责与中转服务器建立WebSocket连接，处理消息收发
"""

import asyncio
import json
import uuid
from typing import Optional, Dict, Any, Callable, List
from datetime import datetime, timedelta

import socketio
from loguru import logger


class RelayClient:
    """中转服务器WebSocket客户端"""

    def __init__(
        self,
        server_url: str,
        api_key: str,
        client_type: str = "admin",
        auto_reconnect: bool = True,
        max_reconnect_attempts: int = 5,
        heartbeat_interval: int = 30,
    ):
        """
        初始化中转客户端

        Args:
            server_url: 中转服务器地址
            api_key: API密钥
            client_type: 客户端类型 (admin/plugin/admin_panel)
            auto_reconnect: 是否自动重连
            max_reconnect_attempts: 最大重连次数
            heartbeat_interval: 心跳间隔(秒)
        """
        self.server_url = server_url
        self.api_key = api_key
        self.client_type = client_type
        self.auto_reconnect = auto_reconnect
        self.max_reconnect_attempts = max_reconnect_attempts
        self.heartbeat_interval = heartbeat_interval

        # Socket.IO客户端
        self.sio: Optional[socketio.AsyncClient] = None
        self._connected = False
        self._reconnect_attempts = 0

        # 事件回调
        self._event_handlers: Dict[str, List[Callable]] = {}
        self._response_handlers: Dict[str, asyncio.Future] = {}

        # 心跳任务
        self._heartbeat_task: Optional[asyncio.Task] = None

        # 消息队列
        self._message_queue: asyncio.Queue = asyncio.Queue()

        logger.info(f"Relay client initialized: {client_type} -> {server_url}")

    async def connect(self) -> bool:
        """
        连接到中转服务器

        Returns:
            是否连接成功
        """
        try:
            self.sio = socketio.AsyncClient(
                reconnection=self.auto_reconnect,
                reconnection_attempts=self.max_reconnect_attempts,
                reconnection_delay=1,
                reconnection_delay_max=30,
            )

            # 注册事件处理
            self._register_event_handlers()

            # 连接选项
            connect_options = {
                "auth": {
                    "clientType": self.client_type,
                    "credentials": {
                        "apiKey": self.api_key,
                    },
                },
                "transports": ["websocket", "polling"],
            }

            # 建立连接
            await self.sio.connect(self.server_url, **connect_options)

            # 等待连接确认
            await asyncio.sleep(1)

            if self._connected:
                logger.info(f"Connected to relay server: {self.server_url}")
                self._reconnect_attempts = 0

                # 启动心跳
                self._start_heartbeat()

                # 启动消息处理
                asyncio.create_task(self._process_message_queue())

                return True
            else:
                logger.error("Failed to connect to relay server")
                return False

        except Exception as e:
            logger.error(f"Connection error: {e}")
            return False

    async def disconnect(self):
        """断开连接"""
        if self._heartbeat_task:
            self._heartbeat_task.cancel()
            self._heartbeat_task = None

        if self.sio and self._connected:
            await self.sio.disconnect()
            self._connected = False
            logger.info("Disconnected from relay server")

    def _register_event_handlers(self):
        """注册Socket.IO事件处理器"""

        @self.sio.event
        async def connect():
            self._connected = True
            logger.info("Socket.IO connected")

        @self.sio.event
        async def disconnect():
            self._connected = False
            logger.warning("Socket.IO disconnected")

        @self.sio.event
        async def connect_error(data):
            logger.error(f"Socket.IO connection error: {data}")

        @self.sio.on("event")
        async def on_event(data):
            await self._handle_event(data)

        @self.sio.on("command")
        async def on_command(data):
            await self._handle_command(data)

        @self.sio.on("response")
        async def on_response(data):
            await self._handle_response(data)

        @self.sio.on("broadcast")
        async def on_broadcast(data):
            await self._handle_broadcast(data)

        @self.sio.on("heartbeat")
        async def on_heartbeat(data):
            await self._handle_heartbeat(data)

        @self.sio.on("client_connected")
        async def on_client_connected(data):
            logger.debug(f"Client connected: {data}")
            await self._trigger_event("client_connected", data)

        @self.sio.on("client_disconnected")
        async def on_client_disconnected(data):
            logger.debug(f"Client disconnected: {data}")
            await self._trigger_event("client_disconnected", data)

    async def _handle_event(self, data: Dict[str, Any]):
        """处理事件消息"""
        event_type = data.get("event", "unknown")
        logger.debug(f"Received event: {event_type}")

        # 触发事件回调
        await self._trigger_event(event_type, data)

        # 也触发通用事件回调
        await self._trigger_event("*", data)

    async def _handle_command(self, data: Dict[str, Any]):
        """处理指令消息"""
        command_id = data.get("messageId", "")
        command = data.get("command", "")
        logger.debug(f"Received command: {command}")

        # 触发命令回调
        await self._trigger_event("command", data)

    async def _handle_response(self, data: Dict[str, Any]):
        """处理响应消息"""
        response_to = data.get("responseTo", "")
        logger.debug(f"Received response for: {response_to}")

        # 检查是否有等待的future
        if response_to in self._response_handlers:
            future = self._response_handlers.pop(response_to)
            if not future.done():
                future.set_result(data)

    async def _handle_broadcast(self, data: Dict[str, Any]):
        """处理广播消息"""
        logger.debug("Received broadcast")
        await self._trigger_event("broadcast", data)

    async def _handle_heartbeat(self, data: Dict[str, Any]):
        """处理心跳消息"""
        logger.debug("Received heartbeat")

    async def _trigger_event(self, event_type: str, data: Dict[str, Any]):
        """触发事件回调"""
        if event_type in self._event_handlers:
            for handler in self._event_handlers[event_type]:
                try:
                    if asyncio.iscoroutinefunction(handler):
                        await handler(data)
                    else:
                        handler(data)
                except Exception as e:
                    logger.error(f"Error in event handler for {event_type}: {e}")

    def on(self, event: str, handler: Callable):
        """
        注册事件监听器

        Args:
            event: 事件名称
            handler: 事件处理函数
        """
        if event not in self._event_handlers:
            self._event_handlers[event] = []
        self._event_handlers[event].append(handler)

    def off(self, event: str, handler: Optional[Callable] = None):
        """
        移除事件监听器

        Args:
            event: 事件名称
            handler: 事件处理函数，如果为None则移除所有
        """
        if event in self._event_handlers:
            if handler is None:
                del self._event_handlers[event]
            else:
                self._event_handlers[event] = [
                    h for h in self._event_handlers[event] if h != handler
                ]

    async def send_event(self, event_type: str, event_data: Dict[str, Any]) -> bool:
        """
        发送事件

        Args:
            event_type: 事件类型
            event_data: 事件数据

        Returns:
            是否发送成功
        """
        if not self._connected or not self.sio:
            logger.warning("Not connected, queuing event")
            await self._message_queue.put(("event", event_type, event_data))
            return False

        try:
            message = {
                "type": "event",
                "event": event_type,
                "data": event_data,
                "timestamp": datetime.utcnow().isoformat(),
            }

            await self.sio.emit("event", message)
            logger.debug(f"Sent event: {event_type}")
            return True

        except Exception as e:
            logger.error(f"Failed to send event: {e}")
            return False

    async def send_command(
        self,
        target_id: str,
        command: str,
        params: Optional[Dict[str, Any]] = None,
        timeout: int = 30,
    ) -> Optional[Dict[str, Any]]:
        """
        发送指令并等待响应

        Args:
            target_id: 目标站点ID
            command: 指令名称
            params: 指令参数
            timeout: 超时时间(秒)

        Returns:
            响应数据
        """
        if not self._connected or not self.sio:
            logger.error("Not connected, cannot send command")
            return None

        message_id = str(uuid.uuid4())

        # 创建future等待响应
        loop = asyncio.get_event_loop()
        future = loop.create_future()
        self._response_handlers[message_id] = future

        try:
            message = {
                "type": "command",
                "messageId": message_id,
                "targetId": target_id,
                "command": command,
                "params": params or {},
                "timestamp": datetime.utcnow().isoformat(),
            }

            await self.sio.emit("command", message)
            logger.debug(f"Sent command: {command} to {target_id}")

            # 等待响应
            response = await asyncio.wait_for(future, timeout=timeout)
            return response

        except asyncio.TimeoutError:
            logger.warning(f"Command timeout: {command}")
            if message_id in self._response_handlers:
                del self._response_handlers[message_id]
            return None
        except Exception as e:
            logger.error(f"Failed to send command: {e}")
            if message_id in self._response_handlers:
                del self._response_handlers[message_id]
            return None

    async def send_broadcast(self, event_type: str, event_data: Dict[str, Any]) -> bool:
        """
        发送广播

        Args:
            event_type: 事件类型
            event_data: 事件数据

        Returns:
            是否发送成功
        """
        if not self._connected or not self.sio:
            logger.error("Not connected, cannot send broadcast")
            return False

        try:
            message = {
                "type": "broadcast",
                "event": event_type,
                "data": event_data,
                "timestamp": datetime.utcnow().isoformat(),
            }

            await self.sio.emit("broadcast", message)
            logger.debug(f"Sent broadcast: {event_type}")
            return True

        except Exception as e:
            logger.error(f"Failed to send broadcast: {e}")
            return False

    def _start_heartbeat(self):
        """启动心跳"""
        self._heartbeat_task = asyncio.create_task(self._heartbeat_loop())

    async def _heartbeat_loop(self):
        """心跳循环"""
        while self._connected:
            try:
                await asyncio.sleep(self.heartbeat_interval)

                if self._connected and self.sio:
                    heartbeat_data = {
                        "type": "heartbeat",
                        "timestamp": datetime.utcnow().isoformat(),
                    }
                    await self.sio.emit("heartbeat", heartbeat_data)
                    logger.debug("Sent heartbeat")

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Heartbeat error: {e}")

    async def _process_message_queue(self):
        """处理消息队列"""
        while True:
            try:
                msg_type, *args = await self._message_queue.get()

                if not self._connected:
                    # 还没连接，等一下再试
                    await asyncio.sleep(1)
                    await self._message_queue.put((msg_type, *args))
                    continue

                if msg_type == "event":
                    event_type, event_data = args
                    await self.send_event(event_type, event_data)

                self._message_queue.task_done()

            except Exception as e:
                logger.error(f"Message queue processing error: {e}")
                await asyncio.sleep(1)

    @property
    def connected(self) -> bool:
        """是否已连接"""
        return self._connected

    @property
    def reconnect_attempts(self) -> int:
        """重连次数"""
        return self._reconnect_attempts
