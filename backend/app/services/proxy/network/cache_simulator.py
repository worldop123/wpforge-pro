"""
缓存行为模拟器
提供浏览器缓存行为的模拟功能
"""
import time
import hashlib
from typing import Dict, Any, List, Optional
from urllib.parse import urlparse

from app.core.logging import get_logger

logger = get_logger(__name__)


class CacheEntry:
    """缓存条目"""
    
    def __init__(self, url: str, headers: Dict[str, str], 
                 response_time: float = 0.0):
        self.url = url
        self.headers = headers
        self.response_time = response_time
        self.created_at = time.time()
        self.last_accessed = time.time()
        self.access_count = 0
        
        # 解析缓存控制头
        self.max_age = self._parse_max_age()
        self.etag = headers.get("ETag", "")
        self.last_modified = headers.get("Last-Modified", "")
        self.cache_control = headers.get("Cache-Control", "")
    
    def _parse_max_age(self) -> Optional[int]:
        """解析max-age"""
        cache_control = self.headers.get("Cache-Control", "")
        if "max-age=" in cache_control:
            try:
                return int(cache_control.split("max-age=")[1].split(",")[0].strip())
            except:
                pass
        return None
    
    def is_expired(self) -> bool:
        """检查是否过期"""
        if self.max_age is not None:
            return time.time() - self.created_at > self.max_age
        return False  # 默认不过期
    
    def should_revalidate(self) -> bool:
        """检查是否需要重新验证"""
        if "no-cache" in self.cache_control:
            return True
        if self.is_expired() and (self.etag or self.last_modified):
            return True
        return False
    
    def touch(self):
        """更新访问时间"""
        self.last_accessed = time.time()
        self.access_count += 1


class CacheSimulator:
    """缓存模拟器"""
    
    def __init__(self):
        self._cache: Dict[str, CacheEntry] = {}
        self._max_entries: int = 1000
        self._max_size: int = 50 * 1024 * 1024  # 50MB
        self._current_size: int = 0
    
    def add_response(self, url: str, headers: Dict[str, str],
                     response_time: float = 0.0):
        """添加响应到缓存"""
        # 检查是否允许缓存
        cache_control = headers.get("Cache-Control", "")
        if "no-store" in cache_control:
            return
        
        # 检查缓存大小
        if len(self._cache) >= self._max_entries:
            self._evict_oldest()
        
        entry = CacheEntry(url, headers, response_time)
        self._cache[url] = entry
    
    def get_cached_response(self, url: str) -> Optional[Dict[str, Any]]:
        """
        获取缓存的响应
        
        Args:
            url: URL
            
        Returns:
            缓存的响应信息，如果没有缓存或已过期则返回None
        """
        if url not in self._cache:
            return None
        
        entry = self._cache[url]
        
        # 检查是否过期
        if entry.is_expired():
            # 检查是否可以重新验证
            if entry.should_revalidate():
                return {
                    "status": "revalidate",
                    "etag": entry.etag,
                    "last_modified": entry.last_modified,
                    "entry": entry,
                }
            else:
                # 完全过期，删除
                del self._cache[url]
                return None
        
        # 更新访问时间
        entry.touch()
        
        return {
            "status": "hit",
            "headers": entry.headers,
            "response_time": entry.response_time * 0.1,  # 缓存响应更快
            "entry": entry,
        }
    
    def get_conditional_headers(self, url: str) -> Dict[str, str]:
        """
        获取条件请求头（用于重新验证）
        
        Args:
            url: URL
            
        Returns:
            条件请求头
        """
        headers = {}
        
        if url not in self._cache:
            return headers
        
        entry = self._cache[url]
        
        if entry.etag:
            headers["If-None-Match"] = entry.etag
        
        if entry.last_modified:
            headers["If-Modified-Since"] = entry.last_modified
        
        return headers
    
    def handle_304_response(self, url: str, new_headers: Dict[str, str]):
        """
        处理304 Not Modified响应
        
        Args:
            url: URL
            new_headers: 新的响应头
        """
        if url in self._cache:
            entry = self._cache[url]
            # 更新一些头信息
            entry.headers.update({
                k: v for k, v in new_headers.items()
                if k.lower() not in ["content-length", "content-encoding"]
            })
            entry.touch()
    
    def invalidate(self, url: str):
        """使缓存失效"""
        if url in self._cache:
            del self._cache[url]
    
    def clear(self):
        """清除所有缓存"""
        self._cache.clear()
        self._current_size = 0
    
    def _evict_oldest(self):
        """淘汰最旧的缓存条目"""
        if not self._cache:
            return
        
        # 找到最久未使用的条目
        oldest_url = None
        oldest_time = float('inf')
        
        for url, entry in self._cache.items():
            if entry.last_accessed < oldest_time:
                oldest_time = entry.last_accessed
                oldest_url = url
        
        if oldest_url:
            del self._cache[oldest_url]
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        total_entries = len(self._cache)
        expired_count = sum(1 for e in self._cache.values() if e.is_expired())
        
        return {
            "total_entries": total_entries,
            "expired_entries": expired_count,
            "max_entries": self._max_entries,
            "hit_rate": 0.0,  # 需要额外统计
        }
    
    def simulate_hard_refresh(self, url: str) -> Dict[str, str]:
        """
        模拟强制刷新（Ctrl+F5）
        
        Args:
            url: URL
            
        Returns:
            强制刷新的请求头
        """
        # 强制刷新会添加Cache-Control: no-cache和Pragma: no-cache
        return {
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
        }
    
    def simulate_normal_refresh(self, url: str) -> Dict[str, str]:
        """
        模拟普通刷新（F5）
        
        Args:
            url: URL
            
        Returns:
            普通刷新的请求头
        """
        # 普通刷新会重新验证
        return self.get_conditional_headers(url)
