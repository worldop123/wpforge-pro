"""
Site Manager - 站点连接管理

管理所有连接的站点，提供站点列表、状态查询、分组管理等功能
"""

import asyncio
from typing import Optional, Dict, Any, List
from datetime import datetime

from loguru import logger

from .relay_client import RelayClient


class SiteManager:
    """站点连接管理器"""

    def __init__(self, relay_client: RelayClient):
        """
        初始化站点管理器

        Args:
            relay_client: 中转客户端实例
        """
        self.relay_client = relay_client
        self._sites: Dict[str, Dict[str, Any]] = {}
        self._groups: Dict[str, List[str]] = {}

        # 注册事件监听
        self._register_event_handlers()

        logger.info("Site manager initialized")

    def _register_event_handlers(self):
        """注册事件处理器"""
        self.relay_client.on("client_connected", self._on_client_connected)
        self.relay_client.on("client_disconnected", self._on_client_disconnected)

    async def _on_client_connected(self, data: Dict[str, Any]):
        """客户端连接事件"""
        client_id = data.get("clientId", "")
        client_type = data.get("type", "")

        if client_type == "plugin":
            site_id = data.get("siteId", client_id)
            self._sites[site_id] = {
                "site_id": site_id,
                "client_id": client_id,
                "status": "online",
                "connected_at": datetime.utcnow().isoformat(),
                "last_seen": datetime.utcnow().isoformat(),
                "metadata": data.get("metadata", {}),
            }
            logger.info(f"Site connected: {site_id}")

    async def _on_client_disconnected(self, data: Dict[str, Any]):
        """客户端断开事件"""
        client_id = data.get("clientId", "")
        client_type = data.get("type", "")

        if client_type == "plugin":
            # 查找对应的站点
            for site_id, site_info in self._sites.items():
                if site_info.get("client_id") == client_id:
                    site_info["status"] = "offline"
                    site_info["last_seen"] = datetime.utcnow().isoformat()
                    logger.info(f"Site disconnected: {site_id}")
                    break

    async def get_sites(
        self,
        status: Optional[str] = None,
        group_id: Optional[str] = None,
        search: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> Dict[str, Any]:
        """
        获取站点列表

        Args:
            status: 按状态筛选 (online/offline/disabled)
            group_id: 按分组筛选
            search: 搜索关键词
            page: 页码
            page_size: 每页数量

        Returns:
            站点列表和分页信息
        """
        # 这里简化处理，实际应该通过REST API从服务器获取
        # 因为站点数据存储在服务器端
        sites = list(self._sites.values())

        # 状态筛选
        if status:
            sites = [s for s in sites if s.get("status") == status]

        # 搜索筛选
        if search:
            search_lower = search.lower()
            sites = [
                s
                for s in sites
                if search_lower in s.get("site_id", "").lower()
                or search_lower in s.get("metadata", {}).get("site_name", "").lower()
            ]

        # 分页
        total = len(sites)
        start = (page - 1) * page_size
        end = start + page_size
        paginated_sites = sites[start:end]

        return {
            "sites": paginated_sites,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size,
        }

    async def get_site(self, site_id: str) -> Optional[Dict[str, Any]]:
        """
        获取站点详情

        Args:
            site_id: 站点ID

        Returns:
            站点信息
        """
        return self._sites.get(site_id)

    async def is_site_online(self, site_id: str) -> bool:
        """
        检查站点是否在线

        Args:
            site_id: 站点ID

        Returns:
            是否在线
        """
        site = self._sites.get(site_id)
        return site is not None and site.get("status") == "online"

    async def get_online_sites(self) -> List[str]:
        """
        获取所有在线站点ID列表

        Returns:
            在线站点ID列表
        """
        return [
            site_id
            for site_id, site_info in self._sites.items()
            if site_info.get("status") == "online"
        ]

    async def get_offline_sites(self) -> List[str]:
        """
        获取所有离线站点ID列表

        Returns:
            离线站点ID列表
        """
        return [
            site_id
            for site_id, site_info in self._sites.items()
            if site_info.get("status") == "offline"
        ]

    async def get_site_count(self) -> Dict[str, int]:
        """
        获取站点统计

        Returns:
            各状态站点数量
        """
        counts = {
            "total": len(self._sites),
            "online": 0,
            "offline": 0,
            "disabled": 0,
        }

        for site_info in self._sites.values():
            status = site_info.get("status", "offline")
            if status in counts:
                counts[status] += 1

        return counts

    async def add_to_group(self, site_id: str, group_id: str):
        """
        将站点添加到分组

        Args:
            site_id: 站点ID
            group_id: 分组ID
        """
        if group_id not in self._groups:
            self._groups[group_id] = []

        if site_id not in self._groups[group_id]:
            self._groups[group_id].append(site_id)

        logger.debug(f"Site {site_id} added to group {group_id}")

    async def remove_from_group(self, site_id: str, group_id: str):
        """
        从分组移除站点

        Args:
            site_id: 站点ID
            group_id: 分组ID
        """
        if group_id in self._groups and site_id in self._groups[group_id]:
            self._groups[group_id].remove(site_id)

        logger.debug(f"Site {site_id} removed from group {group_id}")

    async def get_group_sites(self, group_id: str) -> List[str]:
        """
        获取分组中的站点

        Args:
            group_id: 分组ID

        Returns:
            站点ID列表
        """
        return self._groups.get(group_id, [])

    async def get_groups(self) -> List[str]:
        """
        获取所有分组

        Returns:
            分组ID列表
        """
        return list(self._groups.keys())

    async def update_site_metadata(self, site_id: str, metadata: Dict[str, Any]):
        """
        更新站点元数据

        Args:
            site_id: 站点ID
            metadata: 元数据
        """
        if site_id in self._sites:
            if "metadata" not in self._sites[site_id]:
                self._sites[site_id]["metadata"] = {}
            self._sites[site_id]["metadata"].update(metadata)

    async def refresh_sites(self):
        """刷新站点列表（从服务器获取最新数据）"""
        # 这里应该通过REST API从服务器获取最新站点列表
        # 暂时保留本地缓存
        logger.debug("Refreshing sites list")

    @property
    def sites(self) -> Dict[str, Dict[str, Any]]:
        """所有站点"""
        return self._sites.copy()
