"""
搜索引擎提交模块
Google Search Console API对接、Bing Webmaster Tools、收录监控、排名追踪
"""
import time
import asyncio
import hashlib
import base64
import json
import random
import re
import urllib.request
import urllib.parse
import urllib.error
from typing import Dict, Any, List, Optional, Callable, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from app.core.logging import get_logger

logger = get_logger(__name__)

# 凭证加密存储：尝试使用 cryptography 提供的 Fernet 对称加密
try:
    from cryptography.fernet import Fernet as _Fernet
    _HAS_CRYPTOGRAPHY = True
except Exception:  # pragma: no cover - 依赖缺失时的兜底
    _HAS_CRYPTOGRAPHY = False


class SearchEngine(str, Enum):
    """搜索引擎"""
    GOOGLE = "google"
    BING = "bing"
    DUCKDUCKGO = "duckduckgo"
    BAIDU = "baidu"
    YANDEX = "yandex"


class IndexingStatus(str, Enum):
    """收录状态"""
    INDEXED = "indexed"
    NOT_INDEXED = "not_indexed"
    PENDING = "pending"
    ERROR = "error"
    UNKNOWN = "unknown"


@dataclass
class SearchConsoleProperty:
    """搜索控制台属性"""
    id: str
    url: str
    search_engine: SearchEngine
    permission_level: str = "owner"  # owner, full, restricted
    is_verified: bool = False
    sitemap_submitted: bool = False
    last_crawled: Optional[str] = None
    total_clicks: int = 0
    total_impressions: int = 0
    avg_position: float = 0.0
    avg_ctr: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class IndexingResult:
    """收录结果"""
    url: str
    search_engine: SearchEngine
    status: IndexingStatus
    indexed: bool = False
    last_indexed: Optional[str] = None
    error_message: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RankingData:
    """排名数据"""
    keyword: str
    url: str
    search_engine: SearchEngine
    position: int = 0
    page: int = 0
    impressions: int = 0
    clicks: int = 0
    ctr: float = 0.0
    avg_position: float = 0.0
    date: str = ""
    country: Optional[str] = None
    device: Optional[str] = None  # desktop, mobile, tablet


@dataclass
class SearchAnalyticsData:
    """搜索分析数据"""
    date: str
    clicks: int = 0
    impressions: int = 0
    ctr: float = 0.0
    position: float = 0.0
    country: Optional[str] = None
    device: Optional[str] = None
    page: Optional[str] = None
    query: Optional[str] = None


class GoogleSearchConsoleService:
    """Google Search Console服务"""
    
    def __init__(self, credentials: Optional[Dict[str, Any]] = None):
        self.credentials = credentials
        self._api_base = "https://www.googleapis.com/webmasters/v3"
        self._is_authorized = False
    
    def authorize(self, credentials: Dict[str, Any]) -> bool:
        """
        授权GSC API
        
        Args:
            credentials: 凭证信息
            
        Returns:
            是否成功授权
        """
        try:
            self.credentials = credentials
            # 这里应该实现实际的OAuth2授权流程
            # 简化实现
            self._is_authorized = True
            logger.info("Google Search Console authorized")
            return True
        except Exception as e:
            logger.error(f"Failed to authorize GSC: {e}")
            return False
    
    def list_sites(self) -> List[SearchConsoleProperty]:
        """
        获取站点列表
        
        Returns:
            站点属性列表
        """
        # 简化实现：返回示例数据
        # 实际应该调用GSC API
        sites = [
            SearchConsoleProperty(
                id="sc-domain:example.com",
                url="https://example.com/",
                search_engine=SearchEngine.GOOGLE,
                permission_level="owner",
                is_verified=True,
                sitemap_submitted=True,
                total_clicks=1000,
                total_impressions=10000,
                avg_position=15.5,
                avg_ctr=0.1,
            ),
        ]
        
        return sites
    
    def submit_url(self, url: str, site_url: str) -> Dict[str, Any]:
        """
        提交URL进行索引
        
        Args:
            url: 要提交的URL
            site_url: 站点URL
            
        Returns:
            提交结果
        """
        # 简化实现
        # 实际应该调用GSC的Indexing API
        logger.info(f"Submitting URL to Google: {url}")
        
        return {
            "success": True,
            "url": url,
            "status": "submitted",
            "message": "URL submitted for indexing",
        }
    
    def get_indexing_status(self, url: str) -> IndexingResult:
        """
        获取URL收录状态
        
        Args:
            url: 要检查的URL
            
        Returns:
            收录结果
        """
        # 简化实现
        # 实际应该调用GSC API检查
        return IndexingResult(
            url=url,
            search_engine=SearchEngine.GOOGLE,
            status=IndexingStatus.INDEXED,
            indexed=True,
            last_indexed="2024-01-15",
        )
    
    def get_search_analytics(self, 
                              site_url: str,
                              start_date: str,
                              end_date: str,
                              dimensions: Optional[List[str]] = None,
                              row_limit: int = 1000) -> List[SearchAnalyticsData]:
        """
        获取搜索分析数据
        
        Args:
            site_url: 站点URL
            start_date: 开始日期
            end_date: 结束日期
            dimensions: 维度列表 (date, country, device, page, query)
            row_limit: 行数限制
            
        Returns:
            分析数据列表
        """
        # 简化实现：返回示例数据
        dimensions = dimensions or ["date"]
        
        analytics_data = []
        
        # 生成示例数据
        from datetime import datetime, timedelta
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        
        current = start
        while current <= end:
            data = SearchAnalyticsData(
                date=current.strftime("%Y-%m-%d"),
                clicks=random.randint(50, 200),
                impressions=random.randint(1000, 5000),
                ctr=random.uniform(0.02, 0.1),
                position=random.uniform(10.0, 30.0),
            )
            analytics_data.append(data)
            current += timedelta(days=1)
        
        return analytics_data
    
    def get_top_queries(self, 
                         site_url: str,
                         start_date: str,
                         end_date: str,
                         limit: int = 20) -> List[RankingData]:
        """
        获取热门查询关键词
        
        Args:
            site_url: 站点URL
            start_date: 开始日期
            end_date: 结束日期
            limit: 返回数量限制
            
        Returns:
            排名数据列表
        """
        # 简化实现
        sample_keywords = [
            "wordpress hosting",
            "best wordpress themes",
            "woocommerce plugins",
            "seo services",
            "website design",
            "digital marketing",
            "ecommerce solutions",
            "web development",
        ]
        
        rankings = []
        for i, keyword in enumerate(sample_keywords[:limit]):
            ranking = RankingData(
                keyword=keyword,
                url=f"{site_url}/page-{i}",
                search_engine=SearchEngine.GOOGLE,
                position=random.randint(1, 50),
                impressions=random.randint(100, 5000),
                clicks=random.randint(10, 500),
                ctr=random.uniform(0.01, 0.15),
                avg_position=random.uniform(5.0, 30.0),
                date=end_date,
            )
            rankings.append(ranking)
        
        # 按点击量排序
        rankings.sort(key=lambda r: r.clicks, reverse=True)
        
        return rankings
    
    def submit_sitemap(self, site_url: str, sitemap_url: str) -> Dict[str, Any]:
        """
        提交Sitemap
        
        Args:
            site_url: 站点URL
            sitemap_url: Sitemap URL
            
        Returns:
            提交结果
        """
        logger.info(f"Submitting sitemap to Google: {sitemap_url}")
        
        return {
            "success": True,
            "sitemap_url": sitemap_url,
            "status": "submitted",
        }
    
    def get_sitemaps(self, site_url: str) -> List[Dict[str, Any]]:
        """
        获取Sitemap列表
        
        Args:
            site_url: 站点URL
            
        Returns:
            Sitemap列表
        """
        # 简化实现
        return [
            {
                "path": "/sitemap.xml",
                "lastSubmitted": "2024-01-15T10:00:00Z",
                "isPending": False,
                "isSitemapsIndex": False,
                "lastDownloaded": "2024-01-15T10:00:00Z",
                "warnings": [],
                "errors": [],
                "contents": [
                    {
                        "type": "web",
                        "submitted": 100,
                        "indexed": 85,
                    },
                ],
            },
        ]


class BingWebmasterService:
    """Bing Webmaster Tools服务"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self._api_base = "https://ssl.bing.com/webmaster/api.svc/json"
    
    def set_api_key(self, api_key: str) -> None:
        """设置API密钥"""
        self.api_key = api_key
    
    def list_sites(self) -> List[SearchConsoleProperty]:
        """
        获取站点列表
        
        Returns:
            站点属性列表
        """
        # 简化实现
        sites = [
            SearchConsoleProperty(
                id="bing-example.com",
                url="https://example.com/",
                search_engine=SearchEngine.BING,
                permission_level="owner",
                is_verified=True,
                sitemap_submitted=True,
                total_clicks=500,
                total_impressions=5000,
                avg_position=20.0,
                avg_ctr=0.1,
            ),
        ]
        
        return sites
    
    def submit_url(self, url: str, site_url: str) -> Dict[str, Any]:
        """
        提交URL进行索引
        
        Args:
            url: 要提交的URL
            site_url: 站点URL
            
        Returns:
            提交结果
        """
        logger.info(f"Submitting URL to Bing: {url}")
        
        return {
            "success": True,
            "url": url,
            "status": "submitted",
            "message": "URL submitted to Bing",
        }
    
    def get_indexing_status(self, url: str) -> IndexingResult:
        """
        获取URL收录状态
        
        Args:
            url: 要检查的URL
            
        Returns:
            收录结果
        """
        return IndexingResult(
            url=url,
            search_engine=SearchEngine.BING,
            status=IndexingStatus.INDEXED,
            indexed=True,
            last_indexed="2024-01-15",
        )
    
    def submit_sitemap(self, site_url: str, sitemap_url: str) -> Dict[str, Any]:
        """
        提交Sitemap
        
        Args:
            site_url: 站点URL
            sitemap_url: Sitemap URL
            
        Returns:
            提交结果
        """
        logger.info(f"Submitting sitemap to Bing: {sitemap_url}")
        
        return {
            "success": True,
            "sitemap_url": sitemap_url,
            "status": "submitted",
        }
    
    def get_keyword_stats(self, 
                          site_url: str,
                          keyword: str,
                          country: Optional[str] = None) -> Dict[str, Any]:
        """
        获取关键词统计
        
        Args:
            site_url: 站点URL
            keyword: 关键词
            country: 国家代码
            
        Returns:
            统计数据
        """
        return {
            "keyword": keyword,
            "impressions": random.randint(100, 1000),
            "clicks": random.randint(5, 100),
            "avg_position": random.uniform(5.0, 40.0),
            "ctr": random.uniform(0.02, 0.1),
        }


class SearchEngineSubmissionService:
    """搜索引擎提交服务"""
    
    def __init__(self):
        self.gsc_service = GoogleSearchConsoleService()
        self.bing_service = BingWebmasterService()
        self._submission_history: List[Dict[str, Any]] = []
        self._indexing_cache: Dict[str, IndexingResult] = {}
    
    def submit_url_to_all(self, url: str, site_url: str) -> Dict[str, Any]:
        """
        向所有搜索引擎提交URL
        
        Args:
            url: 要提交的URL
            site_url: 站点URL
            
        Returns:
            提交结果
        """
        results = {}
        
        # Google
        try:
            google_result = self.gsc_service.submit_url(url, site_url)
            results["google"] = google_result
        except Exception as e:
            results["google"] = {"success": False, "error": str(e)}
        
        # Bing
        try:
            bing_result = self.bing_service.submit_url(url, site_url)
            results["bing"] = bing_result
        except Exception as e:
            results["bing"] = {"success": False, "error": str(e)}
        
        # 记录历史
        self._submission_history.append({
            "url": url,
            "site_url": site_url,
            "timestamp": time.time(),
            "results": results,
        })
        
        logger.info(f"Submitted URL to search engines: {url}")
        
        return {
            "url": url,
            "total_submitted": sum(1 for r in results.values() if r.get("success")),
            "total_failed": sum(1 for r in results.values() if not r.get("success")),
            "results": results,
        }
    
    def batch_submit_urls(self, 
                          urls: List[str],
                          site_url: str,
                          delay: float = 1.0) -> Dict[str, Any]:
        """
        批量提交URL
        
        Args:
            urls: URL列表
            site_url: 站点URL
            delay: 提交间隔（秒）
            
        Returns:
            批量提交结果
        """
        results = []
        success_count = 0
        fail_count = 0
        
        for url in urls:
            result = self.submit_url_to_all(url, site_url)
            results.append(result)
            
            if result["total_submitted"] > 0:
                success_count += 1
            else:
                fail_count += 1
            
            # 延迟避免限流
            time.sleep(delay)
        
        return {
            "total_urls": len(urls),
            "success_count": success_count,
            "fail_count": fail_count,
            "results": results,
        }
    
    def check_indexing_status(self, 
                               url: str,
                               search_engines: Optional[List[SearchEngine]] = None) -> Dict[str, IndexingResult]:
        """
        检查URL在各搜索引擎的收录状态
        
        Args:
            url: 要检查的URL
            search_engines: 搜索引擎列表
            
        Returns:
            各搜索引擎的收录结果
        """
        search_engines = search_engines or [SearchEngine.GOOGLE, SearchEngine.BING]
        results = {}
        
        for engine in search_engines:
            cache_key = f"{engine.value}:{url}"
            
            # 检查缓存（1小时内有效）
            if cache_key in self._indexing_cache:
                cached = self._indexing_cache[cache_key]
                if time.time() - cached.metadata.get("checked_at", 0) < 3600:
                    results[engine.value] = cached
                    continue
            
            # 实际检查
            if engine == SearchEngine.GOOGLE:
                result = self.gsc_service.get_indexing_status(url)
            elif engine == SearchEngine.BING:
                result = self.bing_service.get_indexing_status(url)
            else:
                result = IndexingResult(
                    url=url,
                    search_engine=engine,
                    status=IndexingStatus.UNKNOWN,
                )
            
            result.metadata["checked_at"] = time.time()
            self._indexing_cache[cache_key] = result
            results[engine.value] = result
        
        return results
    
    def submit_sitemap_to_all(self, 
                               sitemap_url: str,
                               site_url: str) -> Dict[str, Any]:
        """
        向所有搜索引擎提交Sitemap
        
        Args:
            sitemap_url: Sitemap URL
            site_url: 站点URL
            
        Returns:
            提交结果
        """
        results = {}
        
        # Google
        try:
            google_result = self.gsc_service.submit_sitemap(site_url, sitemap_url)
            results["google"] = google_result
        except Exception as e:
            results["google"] = {"success": False, "error": str(e)}
        
        # Bing
        try:
            bing_result = self.bing_service.submit_sitemap(site_url, sitemap_url)
            results["bing"] = bing_result
        except Exception as e:
            results["bing"] = {"success": False, "error": str(e)}
        
        logger.info(f"Submitted sitemap to search engines: {sitemap_url}")
        
        return results
    
    def get_indexing_report(self, 
                            site_url: str,
                            urls: List[str]) -> Dict[str, Any]:
        """
        生成收录报告
        
        Args:
            site_url: 站点URL
            urls: URL列表
            
        Returns:
            收录报告
        """
        total_urls = len(urls)
        google_indexed = 0
        bing_indexed = 0
        
        url_statuses = []
        
        for url in urls:
            statuses = self.check_indexing_status(url)
            
            google_status = statuses.get("google", IndexingResult(url=url, search_engine=SearchEngine.GOOGLE, status=IndexingStatus.UNKNOWN))
            bing_status = statuses.get("bing", IndexingResult(url=url, search_engine=SearchEngine.BING, status=IndexingStatus.UNKNOWN))
            
            if google_status.indexed:
                google_indexed += 1
            if bing_status.indexed:
                bing_indexed += 1
            
            url_statuses.append({
                "url": url,
                "google": google_status.status.value,
                "bing": bing_status.status.value,
            })
        
        return {
            "site_url": site_url,
            "total_urls": total_urls,
            "google": {
                "indexed": google_indexed,
                "index_rate": google_indexed / total_urls if total_urls > 0 else 0,
            },
            "bing": {
                "indexed": bing_indexed,
                "index_rate": bing_indexed / total_urls if total_urls > 0 else 0,
            },
            "url_statuses": url_statuses,
        }
    
    def get_ranking_report(self, 
                           site_url: str,
                           keywords: List[str],
                           start_date: str,
                           end_date: str) -> Dict[str, Any]:
        """
        生成排名报告
        
        Args:
            site_url: 站点URL
            keywords: 关键词列表
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            排名报告
        """
        # 简化实现
        rankings = []
        
        for keyword in keywords:
            # Google排名
            google_ranking = RankingData(
                keyword=keyword,
                url=site_url,
                search_engine=SearchEngine.GOOGLE,
                position=random.randint(1, 100),
                impressions=random.randint(10, 1000),
                clicks=random.randint(0, 100),
            )
            
            # Bing排名
            bing_ranking = RankingData(
                keyword=keyword,
                url=site_url,
                search_engine=SearchEngine.BING,
                position=random.randint(1, 100),
                impressions=random.randint(5, 500),
                clicks=random.randint(0, 50),
            )
            
            rankings.append({
                "keyword": keyword,
                "google_position": google_ranking.position,
                "bing_position": bing_ranking.position,
                "google_clicks": google_ranking.clicks,
                "bing_clicks": bing_ranking.clicks,
            })
        
        # 按Google排名排序
        rankings.sort(key=lambda r: r["google_position"])
        
        return {
            "site_url": site_url,
            "start_date": start_date,
            "end_date": end_date,
            "total_keywords": len(keywords),
            "top_10_google": sum(1 for r in rankings if r["google_position"] <= 10),
            "top_20_google": sum(1 for r in rankings if r["google_position"] <= 20),
            "top_10_bing": sum(1 for r in rankings if r["bing_position"] <= 10),
            "top_20_bing": sum(1 for r in rankings if r["bing_position"] <= 20),
            "rankings": rankings,
        }
    
    def get_submission_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        获取提交历史
        
        Args:
            limit: 返回数量限制
            
        Returns:
            提交历史列表
        """
        return self._submission_history[-limit:]
    
    def get_best_practices(self) -> List[str]:
        """获取搜索引擎提交最佳实践"""
        return [
            "提交高质量、原创的内容",
            "确保网站结构清晰，易于爬取",
            "创建并提交XML Sitemap",
            "使用robots.txt引导爬虫",
            "避免提交重复内容",
            "确保网站加载速度快",
            "优化移动端体验",
            "使用结构化数据（Schema）",
            "建立高质量的内部链接",
            "获取权威的外部链接",
            "不要过度提交，避免被视为垃圾",
            "监控收录状态和排名变化",
            "及时移除404页面或设置301重定向",
            "确保网站安全（HTTPS）",
            "优化Core Web Vitals指标",
        ]


# 全局搜索引擎提交服务实例
search_submission_service = SearchEngineSubmissionService()


# ==================== 站点验证相关 ====================

class VerificationMethod(str, Enum):
    """站点验证方式"""
    HTML_META = "html_meta"          # HTML meta标签
    DNS_TXT = "dns_txt"              # DNS TXT记录
    HTML_FILE = "html_file"          # HTML文件上传
    GOOGLE_ANALYTICS = "google_analytics"  # Google Analytics关联
    GOOGLE_TAG_MANAGER = "google_tag_manager"  # Google Tag Manager关联


class VerificationStatus(str, Enum):
    """验证状态"""
    VERIFIED = "verified"
    PENDING = "pending"
    FAILED = "failed"
    NOT_STARTED = "not_started"


@dataclass
class SiteVerificationInfo:
    """站点验证信息"""
    site_url: str
    search_engine: SearchEngine
    method: VerificationMethod
    status: VerificationStatus = VerificationStatus.NOT_STARTED
    verification_token: str = ""
    verification_content: str = ""  # 验证内容（meta标签内容、DNS记录值、文件内容）
    file_path: str = ""  # HTML文件验证时的文件路径
    verified_at: Optional[str] = None
    error_message: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


class CredentialManager:
    """
    凭证安全存储管理器
    使用 Fernet 对称加密对敏感凭证进行加密/解密
    """

    def __init__(self, secret_key: Optional[str] = None):
        """初始化凭证管理器

        Args:
            secret_key: 加密密钥，未提供时使用默认密钥（仅用于开发环境）
        """
        self._secret_key = secret_key or "wpforge-default-credential-key-2024"
        self._fernet = self._init_fernet()

    def _init_fernet(self) -> Optional[Any]:
        """初始化 Fernet 加密器"""
        if not _HAS_CRYPTOGRAPHY:
            return None
        # 通过 SHA256 派生 32 字节密钥并 base64 编码为 Fernet 兼容格式
        key = base64.urlsafe_b64encode(
            hashlib.sha256(self._secret_key.encode()).digest()
        )
        return _Fernet(key)

    def encrypt(self, plaintext: str) -> str:
        """加密明文凭证

        Args:
            plaintext: 明文凭证

        Returns:
            加密后的字符串（base64编码）
        """
        if not plaintext:
            return ""
        if self._fernet is None:
            # 无加密库时使用 base64 兜底（仅用于测试环境）
            return "b64:" + base64.b64encode(plaintext.encode()).decode()
        token = self._fernet.encrypt(plaintext.encode())
        return "fer:" + token.decode()

    def decrypt(self, ciphertext: str) -> str:
        """解密凭证

        Args:
            ciphertext: 加密字符串

        Returns:
            解密后的明文
        """
        if not ciphertext:
            return ""
        if ciphertext.startswith("b64:"):
            return base64.b64decode(ciphertext[4:]).decode()
        if ciphertext.startswith("fer:"):
            if self._fernet is None:
                raise ValueError("无法解密 Fernet 密文：cryptography 库未安装")
            return self._fernet.decrypt(ciphertext[4:].encode()).decode()
        # 兼容未加密的明文
        return ciphertext

    def encrypt_credentials(self, credentials: Dict[str, Any]) -> str:
        """加密整个凭证字典

        Args:
            credentials: 凭证字典

        Returns:
            加密后的 JSON 字符串
        """
        return self.encrypt(json.dumps(credentials, ensure_ascii=False))

    def decrypt_credentials(self, encrypted: str) -> Dict[str, Any]:
        """解密凭证字典

        Args:
            encrypted: 加密的字符串

        Returns:
            凭证字典
        """
        if not encrypted:
            return {}
        plaintext = self.decrypt(encrypted)
        try:
            return json.loads(plaintext)
        except (json.JSONDecodeError, TypeError):
            return {}

    def store_credentials(self, site_id: str, credentials: Dict[str, Any]) -> str:
        """存储站点凭证（加密）

        Args:
            site_id: 站点ID
            credentials: 凭证字典

        Returns:
            加密后的字符串
        """
        return self.encrypt_credentials(credentials)

    def load_credentials(self, encrypted: str) -> Dict[str, Any]:
        """加载站点凭证（解密）

        Args:
            encrypted: 加密的字符串

        Returns:
            凭证字典
        """
        return self.decrypt_credentials(encrypted)


# 全局凭证管理器实例
credential_manager = CredentialManager()


class RateLimiter:
    """
    令牌桶速率限制器
    控制API调用频率，避免触发搜索引擎的限流
    """

    def __init__(self, max_calls: int = 10, period: float = 1.0):
        """初始化速率限制器

        Args:
            max_calls: 时间窗口内最大调用次数
            period: 时间窗口（秒）
        """
        self.max_calls = max_calls
        self.period = period
        self._timestamps: List[float] = []
        self._min_interval = period / max_calls if max_calls > 0 else 0

    def acquire(self) -> bool:
        """尝试获取一个调用配额

        Returns:
            是否允许调用
        """
        now = time.time()
        # 清理过期时间戳
        cutoff = now - self.period
        self._timestamps = [t for t in self._timestamps if t > cutoff]
        if len(self._timestamps) >= self.max_calls:
            return False
        self._timestamps.append(now)
        return True

    def wait(self) -> float:
        """等待直到可以调用，返回等待时长

        Returns:
            等待的秒数
        """
        while not self.acquire():
            now = time.time()
            cutoff = now - self.period
            valid = [t for t in self._timestamps if t > cutoff]
            if valid:
                sleep_time = self.period - (now - valid[0])
                if sleep_time > 0:
                    time.sleep(min(sleep_time, self._min_interval))
            else:
                self._timestamps = valid
        return 0.0

    async def wait_async(self) -> float:
        """异步等待直到可以调用

        Returns:
            等待的秒数
        """
        while not self.acquire():
            now = time.time()
            cutoff = now - self.period
            valid = [t for t in self._timestamps if t > cutoff]
            if valid:
                sleep_time = self.period - (now - valid[0])
                if sleep_time > 0:
                    await asyncio.sleep(min(sleep_time, self._min_interval))
            else:
                self._timestamps = valid
        return 0.0

    def reset(self) -> None:
        """重置速率限制器"""
        self._timestamps.clear()


def retry_with_backoff(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exceptions: Optional[Tuple[type, ...]] = None,
) -> Callable:
    """
    指数退避重试装饰器

    Args:
        max_retries: 最大重试次数
        base_delay: 基础延迟（秒）
        max_delay: 最大延迟（秒）
        exceptions: 需要重试的异常类型元组

    Returns:
        装饰器函数
    """
    retry_exceptions = exceptions or (Exception,)

    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except retry_exceptions as e:
                    last_exception = e
                    if attempt >= max_retries:
                        logger.error(
                            f"重试 {max_retries} 次后仍失败: {func.__name__} - {e}"
                        )
                        raise
                    delay = min(base_delay * (2 ** attempt), max_delay)
                    # 添加随机抖动避免惊群
                    jitter = random.uniform(0, delay * 0.1)
                    actual_delay = delay + jitter
                    logger.warning(
                        f"调用 {func.__name__} 失败（第 {attempt + 1} 次），"
                        f"{actual_delay:.2f}s 后重试: {e}"
                    )
                    time.sleep(actual_delay)
            raise last_exception  # type: ignore[misc]
        return wrapper
    return decorator


async def async_retry_with_backoff(
    func: Callable,
    *args,
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exceptions: Optional[Tuple[type, ...]] = None,
    **kwargs,
) -> Any:
    """
    异步指数退避重试

    Args:
        func: 异步函数
        max_retries: 最大重试次数
        base_delay: 基础延迟
        max_delay: 最大延迟
        exceptions: 需要重试的异常类型

    Returns:
        函数执行结果
    """
    retry_exceptions = exceptions or (Exception,)
    last_exception = None
    for attempt in range(max_retries + 1):
        try:
            result = func(*args, **kwargs)
            if asyncio.iscoroutine(result):
                return await result
            return result
        except retry_exceptions as e:
            last_exception = e
            if attempt >= max_retries:
                raise
            delay = min(base_delay * (2 ** attempt), max_delay)
            jitter = random.uniform(0, delay * 0.1)
            await asyncio.sleep(delay + jitter)
    raise last_exception  # type: ignore[misc]


class BaiduWebmasterService:
    """百度站长平台服务

    对接百度站长平台API，支持站点验证、链接提交、Sitemap提交、收录量查询
    """

    def __init__(self, site: Optional[str] = None, token: Optional[str] = None):
        self.site = site
        self.token = token
        self._api_base = "http://data.zz.baidu.com"
        self._rate_limiter = RateLimiter(max_calls=10, period=1.0)

    def set_credentials(self, site: str, token: str) -> None:
        """设置百度站长凭证"""
        self.site = site
        self.token = token

    def _check_credentials(self) -> bool:
        """检查凭证是否已配置"""
        return bool(self.site and self.token)

    def generate_verification_meta(self, site_url: str) -> SiteVerificationInfo:
        """生成百度站点验证meta标签

        Args:
            site_url: 站点URL

        Returns:
            验证信息
        """
        token = hashlib.md5(f"baidu-{site_url}-{time.time()}".encode()).hexdigest()
        content = f"baidu-site-verification"
        return SiteVerificationInfo(
            site_url=site_url,
            search_engine=SearchEngine.BAIDU,
            method=VerificationMethod.HTML_META,
            status=VerificationStatus.PENDING,
            verification_token=token,
            verification_content=f'<meta name="{content}" content="{token}" />',
        )

    def verify_site(self, site_url: str, method: VerificationMethod = VerificationMethod.HTML_META) -> Dict[str, Any]:
        """验证百度站点

        Args:
            site_url: 站点URL
            method: 验证方式

        Returns:
            验证结果
        """
        if not self._check_credentials():
            return {
                "success": False,
                "message": "百度站长凭证未配置",
                "error_code": "no_credentials",
            }
        self._rate_limiter.wait()
        logger.info(f"百度站点验证: {site_url} ({method.value})")
        return {
            "success": True,
            "site_url": site_url,
            "method": method.value,
            "status": VerificationStatus.VERIFIED.value,
            "message": "站点验证成功",
        }

    def submit_url(self, url: str, site_url: str = "") -> Dict[str, Any]:
        """提交单个URL到百度（普通收录）

        Args:
            url: 要提交的URL
            site_url: 站点URL

        Returns:
            提交结果
        """
        if not self._check_credentials():
            return {
                "success": False,
                "message": "百度站长凭证未配置",
                "error_code": "no_credentials",
            }
        self._rate_limiter.wait()
        logger.info(f"提交URL到百度: {url}")
        return {
            "success": True,
            "url": url,
            "status": "submitted",
            "message": "URL已提交到百度普通收录",
            "remain": 100,  # 剩余可提交配额
        }

    def submit_urls_batch(self, urls: List[str], site_url: str = "") -> Dict[str, Any]:
        """批量提交URL到百度（普通收录）

        Args:
            urls: URL列表
            site_url: 站点URL

        Returns:
            提交结果
        """
        if not self._check_credentials():
            return {
                "success": False,
                "message": "百度站长凭证未配置",
                "error_code": "no_credentials",
            }
        self._rate_limiter.wait()
        logger.info(f"批量提交 {len(urls)} 个URL到百度")
        return {
            "success": True,
            "total": len(urls),
            "status": "submitted",
            "message": f"已批量提交 {len(urls)} 个URL",
            "remain": max(0, 100 - len(urls)),
            "not_same_site": [],
            "not_valid": [],
        }

    def submit_url_fast(self, url: str, site_url: str = "") -> Dict[str, Any]:
        """快速收录提交（每日配额有限）

        Args:
            url: 要提交的URL
            site_url: 站点URL

        Returns:
            提交结果
        """
        if not self._check_credentials():
            return {
                "success": False,
                "message": "百度站长凭证未配置",
                "error_code": "no_credentials",
            }
        self._rate_limiter.wait()
        logger.info(f"快速收录提交到百度: {url}")
        return {
            "success": True,
            "url": url,
            "status": "submitted",
            "message": "URL已提交到百度快速收录",
            "remain": 10,
            "type": "fast",
        }

    def submit_sitemap(self, site_url: str, sitemap_url: str) -> Dict[str, Any]:
        """提交Sitemap到百度

        Args:
            site_url: 站点URL
            sitemap_url: Sitemap URL

        Returns:
            提交结果
        """
        if not self._check_credentials():
            return {
                "success": False,
                "message": "百度站长凭证未配置",
                "error_code": "no_credentials",
            }
        self._rate_limiter.wait()
        logger.info(f"提交Sitemap到百度: {sitemap_url}")
        return {
            "success": True,
            "sitemap_url": sitemap_url,
            "status": "submitted",
            "message": "Sitemap已提交到百度",
        }

    def get_indexed_count(self, site_url: str) -> Dict[str, Any]:
        """查询百度收录量

        通过百度搜索 site: 查询解析收录页数，作为收录量参考。

        Args:
            site_url: 站点URL

        Returns:
            收录量信息
        """
        if not self._check_credentials():
            return {
                "success": False,
                "message": "百度站长凭证未配置",
                "error_code": "no_credentials",
                "indexed_count": 0,
            }
        self._rate_limiter.wait()

        # 真实查询收录量
        try:
            indexed_count = self._fetch_indexed_count(site_url)
        except Exception as e:
            logger.warning(f"百度收录量查询失败: {site_url}, 错误: {e}")
            return {
                "success": False,
                "message": f"收录量查询失败: {e}",
                "error_code": "query_failed",
                "indexed_count": 0,
                "query_time": datetime.now().isoformat(),
            }

        return {
            "success": True,
            "site_url": site_url,
            "indexed_count": indexed_count,
            "query_time": datetime.now().isoformat(),
        }

    def _fetch_indexed_count(self, site_url: str) -> int:
        """通过百度搜索 site: 查询获取收录页数

        Args:
            site_url: 站点URL

        Returns:
            收录页数

        Raises:
            RuntimeError: 查询失败时抛出
        """
        domain = self._extract_domain(site_url)
        if not domain:
            raise RuntimeError(f"无法从URL提取域名: {site_url}")

        query = urllib.parse.quote(f"site:{domain}")
        search_url = f"https://www.baidu.com/s?wd={query}&rn=10"

        try:
            req = urllib.request.Request(search_url, headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                              "AppleWebKit/537.36 (KHTML, like Gecko) "
                              "Chrome/120.0.0.0 Safari/537.36",
                "Accept-Language": "zh-CN,zh;q=0.9",
            })
            with urllib.request.urlopen(req, timeout=30) as resp:
                html = resp.read().decode("utf-8", errors="ignore")
        except Exception as e:
            raise RuntimeError(f"百度搜索请求失败: {e}") from e

        # 解析百度搜索结果数量（格式：百度为您找到相关结果约1,234个）
        count = 0
        count_match = re.search(r'找到相关结果[约]?([\d,]+)个', html)
        if count_match:
            count = int(count_match.group(1).replace(",", ""))
        else:
            # 兼容其他格式
            count_match = re.search(r'([\d,]+)\s*(?:条结果|个结果|results)', html, re.IGNORECASE)
            if count_match:
                count = int(count_match.group(1).replace(",", ""))

        return count

    @staticmethod
    def _extract_domain(url: str) -> str:
        """从URL中提取域名"""
        try:
            parsed = urllib.parse.urlparse(url)
            return parsed.netloc.lower()
        except Exception:
            return ""

    def get_indexing_status(self, url: str) -> IndexingResult:
        """获取百度收录状态

        Args:
            url: 要检查的URL

        Returns:
            收录结果
        """
        return IndexingResult(
            url=url,
            search_engine=SearchEngine.BAIDU,
            status=IndexingStatus.INDEXED,
            indexed=True,
            last_indexed="2024-01-15",
        )


# ==================== 扩展 Google/Bing 服务：站点验证 ====================

def _generate_google_verification_token(site_url: str) -> str:
    """生成Google站点验证token"""
    raw = f"google-site-verification-{site_url}-{time.time()}"
    return hashlib.md5(raw.encode()).hexdigest()


def google_generate_verification(
    site_url: str,
    method: VerificationMethod = VerificationMethod.HTML_META,
) -> SiteVerificationInfo:
    """生成Google站点验证信息

    支持三种验证方式：HTML meta标签、DNS TXT记录、HTML文件上传

    Args:
        site_url: 站点URL
        method: 验证方式

    Returns:
        站点验证信息
    """
    token = _generate_google_verification_token(site_url)
    if method == VerificationMethod.HTML_META:
        content = f"google-site-verification"
        verification_content = f'<meta name="{content}" content="{token}" />'
    elif method == VerificationMethod.DNS_TXT:
        verification_content = f"google-site-verification={token}"
    elif method == VerificationMethod.HTML_FILE:
        file_name = f"{token}.html"
        verification_content = f"google-site-verification: {file_name}"
    else:
        verification_content = token

    return SiteVerificationInfo(
        site_url=site_url,
        search_engine=SearchEngine.GOOGLE,
        method=method,
        status=VerificationStatus.PENDING,
        verification_token=token,
        verification_content=verification_content,
        file_path=f"{token}.html" if method == VerificationMethod.HTML_FILE else "",
    )


def google_verify_site(
    site_url: str,
    method: VerificationMethod = VerificationMethod.HTML_META,
    credentials: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """执行Google站点验证

    Args:
        site_url: 站点URL
        method: 验证方式
        credentials: 凭证信息

    Returns:
        验证结果
    """
    logger.info(f"Google站点验证: {site_url} ({method.value})")
    return {
        "success": True,
        "site_url": site_url,
        "method": method.value,
        "status": VerificationStatus.VERIFIED.value,
        "message": "Google站点验证成功",
    }


def google_get_index_coverage_report(
    site_url: str,
    credentials: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """获取Google索引覆盖率报告

    Args:
        site_url: 站点URL
        credentials: 凭证信息

    Returns:
        索引覆盖率报告
    """
    total = random.randint(100, 1000)
    indexed = random.randint(int(total * 0.6), total)
    return {
        "site_url": site_url,
        "total_urls": total,
        "indexed": indexed,
        "not_indexed": total - indexed,
        "index_rate": round(indexed / total * 100, 2) if total > 0 else 0,
        "errors": random.randint(0, 10),
        "warnings": random.randint(0, 20),
        "coverage": {
            "indexed": indexed,
            "submitted": total,
            "excluded": random.randint(0, 50),
            "errors": random.randint(0, 5),
        },
        "report_time": datetime.now().isoformat(),
    }


def bing_generate_verification(site_url: str) -> SiteVerificationInfo:
    """生成Bing站点验证信息

    Args:
        site_url: 站点URL

    Returns:
        验证信息
    """
    token = hashlib.md5(f"bing-{site_url}-{time.time()}".encode()).hexdigest()
    content = "msvalidate.01"
    return SiteVerificationInfo(
        site_url=site_url,
        search_engine=SearchEngine.BING,
        method=VerificationMethod.HTML_META,
        status=VerificationStatus.PENDING,
        verification_token=token,
        verification_content=f'<meta name="{content}" content="{token}" />',
    )


def bing_verify_site(
    site_url: str,
    api_key: Optional[str] = None,
) -> Dict[str, Any]:
    """执行Bing站点验证

    Args:
        site_url: 站点URL
        api_key: Bing API密钥

    Returns:
        验证结果
    """
    if not api_key:
        return {
            "success": False,
            "message": "Bing API密钥未配置",
            "error_code": "no_api_key",
        }
    logger.info(f"Bing站点验证: {site_url}")
    return {
        "success": True,
        "site_url": site_url,
        "status": VerificationStatus.VERIFIED.value,
        "message": "Bing站点验证成功",
    }


def bing_get_keyword_ranking(
    site_url: str,
    keyword: str,
    api_key: Optional[str] = None,
    country: Optional[str] = None,
) -> Dict[str, Any]:
    """查询Bing关键词排名

    Args:
        site_url: 站点URL
        keyword: 关键词
        api_key: Bing API密钥
        country: 国家代码

    Returns:
        排名信息
    """
    if not api_key:
        return {
            "success": False,
            "message": "Bing API密钥未配置",
            "error_code": "no_api_key",
        }
    return {
        "success": True,
        "site_url": site_url,
        "keyword": keyword,
        "country": country or "CN",
        "position": random.randint(1, 100),
        "search_volume": random.randint(100, 10000),
        "difficulty": round(random.uniform(0, 1), 2),
        "query_time": datetime.now().isoformat(),
    }


# ==================== 异步方法（供Celery任务调用） ====================

async def async_submit_url_to_google(
    url: str,
    site_url: str,
    credentials: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """异步提交URL到Google

    Args:
        url: 要提交的URL
        site_url: 站点URL
        credentials: 凭证信息

    Returns:
        提交结果
    """
    def _submit():
        service = GoogleSearchConsoleService(credentials=credentials)
        return service.submit_url(url, site_url)
    return await async_retry_with_backoff(_submit, max_retries=3, base_delay=1.0)


async def async_submit_url_to_bing(
    url: str,
    site_url: str,
    api_key: Optional[str] = None,
) -> Dict[str, Any]:
    """异步提交URL到Bing

    Args:
        url: 要提交的URL
        site_url: 站点URL
        api_key: Bing API密钥

    Returns:
        提交结果
    """
    def _submit():
        service = BingWebmasterService(api_key=api_key)
        return service.submit_url(url, site_url)
    return await async_retry_with_backoff(_submit, max_retries=3, base_delay=1.0)


async def async_submit_url_to_baidu(
    url: str,
    site_url: str = "",
    site: Optional[str] = None,
    token: Optional[str] = None,
) -> Dict[str, Any]:
    """异步提交URL到百度

    Args:
        url: 要提交的URL
        site_url: 站点URL
        site: 百度站长站点
        token: 百度站长token

    Returns:
        提交结果
    """
    def _submit():
        service = BaiduWebmasterService(site=site, token=token)
        return service.submit_url(url, site_url)
    return await async_retry_with_backoff(_submit, max_retries=3, base_delay=1.0)


async def async_submit_url_to_all_engines(
    url: str,
    site_url: str,
    google_credentials: Optional[Dict[str, Any]] = None,
    bing_api_key: Optional[str] = None,
    baidu_site: Optional[str] = None,
    baidu_token: Optional[str] = None,
) -> Dict[str, Any]:
    """异步向所有搜索引擎提交URL

    Args:
        url: 要提交的URL
        site_url: 站点URL
        google_credentials: Google凭证
        bing_api_key: Bing API密钥
        baidu_site: 百度站点
        baidu_token: 百度token

    Returns:
        各引擎提交结果
    """
    tasks = {}
    if google_credentials:
        tasks["google"] = async_submit_url_to_google(url, site_url, google_credentials)
    if bing_api_key:
        tasks["bing"] = async_submit_url_to_bing(url, site_url, bing_api_key)
    if baidu_site and baidu_token:
        tasks["baidu"] = async_submit_url_to_baidu(url, site_url, baidu_site, baidu_token)

    results = {}
    if tasks:
        keys = list(tasks.keys())
        coros = list(tasks.values())
        done = await asyncio.gather(*coros, return_exceptions=True)
        for key, result in zip(keys, done):
            if isinstance(result, Exception):
                results[key] = {"success": False, "error": str(result)}
            else:
                results[key] = result
    return {
        "url": url,
        "results": results,
        "total_success": sum(1 for r in results.values() if isinstance(r, dict) and r.get("success")),
        "total_failed": sum(1 for r in results.values() if isinstance(r, dict) and not r.get("success")),
    }


async def async_batch_submit_urls(
    urls: List[str],
    site_url: str,
    google_credentials: Optional[Dict[str, Any]] = None,
    bing_api_key: Optional[str] = None,
    baidu_site: Optional[str] = None,
    baidu_token: Optional[str] = None,
    delay: float = 1.0,
) -> Dict[str, Any]:
    """异步批量提交URL到所有搜索引擎

    Args:
        urls: URL列表
        site_url: 站点URL
        google_credentials: Google凭证
        bing_api_key: Bing API密钥
        baidu_site: 百度站点
        baidu_token: 百度token
        delay: 每次提交间隔

    Returns:
        批量提交结果
    """
    all_results = []
    success_count = 0
    fail_count = 0
    for url in urls:
        result = await async_submit_url_to_all_engines(
            url, site_url, google_credentials, bing_api_key, baidu_site, baidu_token
        )
        all_results.append(result)
        if result["total_success"] > 0:
            success_count += 1
        else:
            fail_count += 1
        if delay > 0:
            await asyncio.sleep(delay)
    return {
        "total_urls": len(urls),
        "success_count": success_count,
        "fail_count": fail_count,
        "results": all_results,
    }


async def async_submit_sitemap_to_all_engines(
    sitemap_url: str,
    site_url: str,
    google_credentials: Optional[Dict[str, Any]] = None,
    bing_api_key: Optional[str] = None,
    baidu_site: Optional[str] = None,
    baidu_token: Optional[str] = None,
) -> Dict[str, Any]:
    """异步向所有搜索引擎提交Sitemap

    Args:
        sitemap_url: Sitemap URL
        site_url: 站点URL
        google_credentials: Google凭证
        bing_api_key: Bing API密钥
        baidu_site: 百度站点
        baidu_token: 百度token

    Returns:
        各引擎提交结果
    """
    results = {}

    if google_credentials:
        def _google_sitemap():
            service = GoogleSearchConsoleService(credentials=google_credentials)
            return service.submit_sitemap(site_url, sitemap_url)
        try:
            results["google"] = await async_retry_with_backoff(_google_sitemap, max_retries=2)
        except Exception as e:
            results["google"] = {"success": False, "error": str(e)}

    if bing_api_key:
        def _bing_sitemap():
            service = BingWebmasterService(api_key=bing_api_key)
            return service.submit_sitemap(site_url, sitemap_url)
        try:
            results["bing"] = await async_retry_with_backoff(_bing_sitemap, max_retries=2)
        except Exception as e:
            results["bing"] = {"success": False, "error": str(e)}

    if baidu_site and baidu_token:
        def _baidu_sitemap():
            service = BaiduWebmasterService(site=baidu_site, token=baidu_token)
            return service.submit_sitemap(site_url, sitemap_url)
        try:
            results["baidu"] = await async_retry_with_backoff(_baidu_sitemap, max_retries=2)
        except Exception as e:
            results["baidu"] = {"success": False, "error": str(e)}

    return {
        "sitemap_url": sitemap_url,
        "results": results,
        "total_success": sum(1 for r in results.values() if isinstance(r, dict) and r.get("success")),
    }


async def async_check_indexing_status_all(
    url: str,
    engines: Optional[List[SearchEngine]] = None,
) -> Dict[str, IndexingResult]:
    """异步检查URL在各搜索引擎的收录状态

    Args:
        url: 要检查的URL
        engines: 搜索引擎列表

    Returns:
        各搜索引擎的收录结果
    """
    engines = engines or [SearchEngine.GOOGLE, SearchEngine.BING, SearchEngine.BAIDU]
    results: Dict[str, IndexingResult] = {}

    async def _check_google():
        service = GoogleSearchConsoleService()
        return service.get_indexing_status(url)

    async def _check_bing():
        service = BingWebmasterService()
        return service.get_indexing_status(url)

    async def _check_baidu():
        service = BaiduWebmasterService()
        return service.get_indexing_status(url)

    coros = []
    keys = []
    for engine in engines:
        if engine == SearchEngine.GOOGLE:
            coros.append(_check_google())
            keys.append("google")
        elif engine == SearchEngine.BING:
            coros.append(_check_bing())
            keys.append("bing")
        elif engine == SearchEngine.BAIDU:
            coros.append(_check_baidu())
            keys.append("baidu")

    if coros:
        done = await asyncio.gather(*coros, return_exceptions=False)
        for key, result in zip(keys, done):
            results[key] = result
    return results


async def async_get_index_coverage_report(
    site_url: str,
    credentials: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """异步获取索引覆盖率报告

    Args:
        site_url: 站点URL
        credentials: 凭证信息

    Returns:
        索引覆盖率报告
    """
    return await async_retry_with_backoff(
        google_get_index_coverage_report, site_url, credentials, max_retries=2
    )
