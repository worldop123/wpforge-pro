"""
Command Sender - 指令下发

提供向站点发送指令的能力，支持单个、分组、批量操作
"""

import asyncio
from typing import Optional, Dict, Any, List, Callable
from datetime import datetime

from loguru import logger

from .relay_client import RelayClient
from .site_manager import SiteManager


class CommandSender:
    """指令发送器"""

    def __init__(self, relay_client: RelayClient, site_manager: SiteManager):
        """
        初始化指令发送器

        Args:
            relay_client: 中转客户端实例
            site_manager: 站点管理器实例
        """
        self.relay_client = relay_client
        self.site_manager = site_manager

        # 批量任务
        self._batch_tasks: Dict[str, Dict[str, Any]] = {}

        logger.info("Command sender initialized")

    async def send_command(
        self,
        site_id: str,
        command: str,
        params: Optional[Dict[str, Any]] = None,
        timeout: int = 30,
    ) -> Optional[Dict[str, Any]]:
        """
        向单个站点发送指令

        Args:
            site_id: 站点ID
            command: 指令名称
            params: 指令参数
            timeout: 超时时间(秒)

        Returns:
            响应数据
        """
        # 检查站点是否在线
        if not await self.site_manager.is_site_online(site_id):
            logger.warning(f"Site {site_id} is offline, command may not be delivered")
            # 仍然尝试发送，服务器可能会缓存离线消息

        logger.info(f"Sending command '{command}' to site {site_id}")

        response = await self.relay_client.send_command(
            target_id=site_id,
            command=command,
            params=params,
            timeout=timeout,
        )

        if response:
            logger.info(f"Command '{command}' completed for site {site_id}")
        else:
            logger.warning(f"Command '{command}' failed or timed out for site {site_id}")

        return response

    async def send_command_to_group(
        self,
        group_id: str,
        command: str,
        params: Optional[Dict[str, Any]] = None,
        timeout: int = 30,
    ) -> Dict[str, Any]:
        """
        向分组中的所有站点发送指令

        Args:
            group_id: 分组ID
            command: 指令名称
            params: 指令参数
            timeout: 超时时间(秒)

        Returns:
            各站点的响应结果
        """
        site_ids = await self.site_manager.get_group_sites(group_id)

        if not site_ids:
            logger.warning(f"No sites found in group {group_id}")
            return {"success": 0, "failed": 0, "results": {}}

        logger.info(
            f"Sending command '{command}' to {len(site_ids)} sites in group {group_id}"
        )

        return await self.send_batch_command(site_ids, command, params, timeout)

    async def send_batch_command(
        self,
        site_ids: List[str],
        command: str,
        params: Optional[Dict[str, Any]] = None,
        timeout: int = 30,
        progress_callback: Optional[Callable] = None,
    ) -> Dict[str, Any]:
        """
        批量向多个站点发送指令

        Args:
            site_ids: 站点ID列表
            command: 指令名称
            params: 指令参数
            timeout: 每个站点的超时时间(秒)
            progress_callback: 进度回调函数

        Returns:
            批量执行结果
        """
        results = {}
        success_count = 0
        failed_count = 0
        total = len(site_ids)

        async def send_to_site(site_id: str, index: int):
            nonlocal success_count, failed_count

            try:
                response = await self.send_command(
                    site_id=site_id,
                    command=command,
                    params=params,
                    timeout=timeout,
                )

                results[site_id] = {
                    "success": response is not None,
                    "response": response,
                }

                if response:
                    success_count += 1
                else:
                    failed_count += 1

            except Exception as e:
                results[site_id] = {
                    "success": False,
                    "error": str(e),
                }
                failed_count += 1

            # 进度回调
            if progress_callback:
                if asyncio.iscoroutinefunction(progress_callback):
                    await progress_callback(index + 1, total, site_id)
                else:
                    progress_callback(index + 1, total, site_id)

        # 并发执行，但限制并发数
        semaphore = asyncio.Semaphore(10)  # 最多10个并发

        async def bounded_send(site_id: str, index: int):
            async with semaphore:
                await send_to_site(site_id, index)

        tasks = [bounded_send(site_id, i) for i, site_id in enumerate(site_ids)]
        await asyncio.gather(*tasks)

        logger.info(
            f"Batch command '{command}' completed: {success_count}/{total} success"
        )

        return {
            "total": total,
            "success": success_count,
            "failed": failed_count,
            "results": results,
        }

    async def broadcast_command(
        self,
        command: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        广播指令到所有在线站点

        Args:
            command: 指令名称
            params: 指令参数

        Returns:
            是否发送成功
        """
        logger.info(f"Broadcasting command '{command}' to all sites")

        # 使用广播机制
        success = await self.relay_client.send_broadcast(
            event_type="command",
            event_data={
                "command": command,
                "params": params or {},
            },
        )

        return success

    # ===== 常用指令封装 =====

    async def get_site_info(self, site_id: str) -> Optional[Dict[str, Any]]:
        """
        获取站点信息

        Args:
            site_id: 站点ID

        Returns:
            站点信息
        """
        return await self.send_command(site_id, "get_site_info")

    async def create_post(
        self,
        site_id: str,
        title: str,
        content: str,
        post_type: str = "post",
        status: str = "draft",
        **kwargs,
    ) -> Optional[Dict[str, Any]]:
        """
        创建文章

        Args:
            site_id: 站点ID
            title: 文章标题
            content: 文章内容
            post_type: 文章类型
            status: 文章状态
            **kwargs: 其他参数

        Returns:
            创建结果
        """
        params = {
            "title": title,
            "content": content,
            "type": post_type,
            "status": status,
            **kwargs,
        }

        return await self.send_command(site_id, "create_post", params)

    async def create_product(
        self,
        site_id: str,
        name: str,
        regular_price: float,
        **kwargs,
    ) -> Optional[Dict[str, Any]]:
        """
        创建产品

        Args:
            site_id: 站点ID
            name: 产品名称
            regular_price: 常规价格
            **kwargs: 其他参数

        Returns:
            创建结果
        """
        params = {
            "name": name,
            "regular_price": regular_price,
            **kwargs,
        }

        return await self.send_command(site_id, "create_product", params)

    async def update_stock(
        self,
        site_id: str,
        product_id: int,
        quantity: int,
    ) -> Optional[Dict[str, Any]]:
        """
        更新库存

        Args:
            site_id: 站点ID
            product_id: 产品ID
            quantity: 库存数量

        Returns:
            更新结果
        """
        params = {
            "product_id": product_id,
            "quantity": quantity,
        }

        return await self.send_command(site_id, "update_stock", params)

    async def system_info(self, site_id: str) -> Optional[Dict[str, Any]]:
        """
        获取系统信息

        Args:
            site_id: 站点ID

        Returns:
            系统信息
        """
        return await self.send_command(site_id, "system_info")

    async def health_check(self, site_id: str) -> Optional[Dict[str, Any]]:
        """
        健康检查

        Args:
            site_id: 站点ID

        Returns:
            健康检查结果
        """
        return await self.send_command(site_id, "health_check")

    async def clear_cache(self, site_id: str) -> Optional[Dict[str, Any]]:
        """
        清除缓存

        Args:
            site_id: 站点ID

        Returns:
            清除结果
        """
        return await self.send_command(site_id, "clear_cache")

    async def batch_create_products(
        self,
        site_ids: List[str],
        products: List[Dict[str, Any]],
        progress_callback: Optional[Callable] = None,
    ) -> Dict[str, Any]:
        """
        批量创建产品

        Args:
            site_ids: 站点ID列表
            products: 产品列表
            progress_callback: 进度回调

        Returns:
            批量执行结果
        """
        # 这个方法会在每个站点创建所有产品
        # 实际使用时可能需要更复杂的逻辑
        results = {}

        for site_id in site_ids:
            site_results = []
            for product in products:
                result = await self.create_product(site_id, **product)
                site_results.append(result)
            results[site_id] = site_results

        return results
