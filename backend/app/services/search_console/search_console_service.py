"""
搜索引擎自动提交与索引服务
支持Google Search Console、Bing Webmaster Tools等
"""
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import json
import random
import time
from datetime import datetime, timedelta

import httpx

from app.core.logging import get_logger

logger = get_logger(__name__)


class SearchEngine(str, Enum):
    """搜索引擎枚举"""
    GOOGLE = "google"
    BING = "bing"
    DUCKDUCKGO = "duckduckgo"
    YANDEX = "yandex"
    BAIDU = "baidu"


class IndexingStatus(str, Enum):
    """索引状态枚举"""
    NOT_SUBMITTED = "not_submitted"
    SUBMITTED = "submitted"
    PROCESSING = "processing"
    INDEXED = "indexed"
    FAILED = "failed"
    DEINDEXED = "deindexed"


@dataclass
class SearchConsoleConfig:
    """搜索控制台配置"""
    # Google Search Console
    google_enabled: bool = False
    google_client_id: str = ""
    google_client_secret: str = ""
    google_refresh_token: str = ""
    google_site_url: str = ""

    # Bing Webmaster Tools
    bing_enabled: bool = False
    bing_api_key: str = ""
    bing_site_url: str = ""

    # Yandex
    yandex_enabled: bool = False
    yandex_api_key: str = ""
    yandex_user_id: str = ""

    # Baidu
    baidu_enabled: bool = False
    baidu_token: str = ""
    baidu_site: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "google_enabled": self.google_enabled,
            "google_client_id": self.google_client_id,
            "google_client_secret": self.google_client_secret,
            "google_refresh_token": self.google_refresh_token,
            "google_site_url": self.google_site_url,
            "bing_enabled": self.bing_enabled,
            "bing_api_key": self.bing_api_key,
            "bing_site_url": self.bing_site_url,
            "yandex_enabled": self.yandex_enabled,
            "yandex_api_key": self.yandex_api_key,
            "yandex_user_id": self.yandex_user_id,
            "baidu_enabled": self.baidu_enabled,
            "baidu_token": self.baidu_token,
            "baidu_site": self.baidu_site,
        }


@dataclass
class IndexingResult:
    """索引提交结果"""
    url: str
    search_engine: SearchEngine
    status: IndexingStatus
    message: str = ""
    submitted_at: Optional[float] = None
    indexed_at: Optional[float] = None
    error_code: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "url": self.url,
            "search_engine": self.search_engine.value,
            "status": self.status.value,
            "message": self.message,
            "submitted_at": self.submitted_at,
            "indexed_at": self.indexed_at,
            "error_code": self.error_code,
        }


@dataclass
class SearchAnalyticsData:
    """搜索分析数据"""
    date: str
    clicks: int = 0
    impressions: int = 0
    ctr: float = 0.0  # 点击率
    average_position: float = 0.0  # 平均排名
    keywords: List[Dict[str, Any]] = field(default_factory=list)
    pages: List[Dict[str, Any]] = field(default_factory=list)
    countries: List[Dict[str, Any]] = field(default_factory=list)
    devices: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "date": self.date,
            "clicks": self.clicks,
            "impressions": self.impressions,
            "ctr": self.ctr,
            "average_position": self.average_position,
            "keywords": self.keywords,
            "pages": self.pages,
            "countries": self.countries,
            "devices": self.devices,
        }


@dataclass
class RankingData:
    """排名数据"""
    keyword: str
    url: str
    position: int
    previous_position: Optional[int] = None
    change: int = 0
    search_engine: SearchEngine = SearchEngine.GOOGLE
    country: str = ""
    device: str = "desktop"
    last_checked: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "keyword": self.keyword,
            "url": self.url,
            "position": self.position,
            "previous_position": self.previous_position,
            "change": self.change,
            "search_engine": self.search_engine.value,
            "country": self.country,
            "device": self.device,
            "last_checked": self.last_checked,
        }


class SearchConsoleService:
    """
    搜索引擎控制台服务
    支持多搜索引擎的索引提交、数据获取、排名追踪
    """

    def __init__(self, config: Optional[SearchConsoleConfig] = None):
        self.config = config or SearchConsoleConfig()
        self._submission_history: Dict[str, List[IndexingResult]] = {}
        self._analytics_cache: Dict[str, SearchAnalyticsData] = {}
        self._rankings: List[RankingData] = []
        # Google OAuth2 access token 缓存：(access_token, expires_at)
        self._google_token_cache: Optional[tuple] = None

    # ==================== OAuth2 / API 调用辅助 ====================

    def _get_google_access_token(self) -> str:
        """通过 refresh_token 获取 Google OAuth2 access_token

        使用 Google OAuth2 token 端点刷新访问令牌。
        凭证从 SearchConsoleConfig 读取，缺失时抛出明确异常。

        Returns:
            访问令牌字符串

        Raises:
            RuntimeError: 凭证未配置或刷新失败
        """
        cfg = self.config
        if not (cfg.google_client_id and cfg.google_client_secret and cfg.google_refresh_token):
            raise RuntimeError("Google OAuth2 凭证未配置（需要 client_id、client_secret、refresh_token）")

        # 命中缓存且未过期（提前 60 秒失效以留出余量）
        if self._google_token_cache:
            token, expires_at = self._google_token_cache
            if token and expires_at and time.time() < expires_at - 60:
                return token

        token_url = "https://oauth2.googleapis.com/token"
        payload = {
            "client_id": cfg.google_client_id,
            "client_secret": cfg.google_client_secret,
            "refresh_token": cfg.google_refresh_token,
            "grant_type": "refresh_token",
        }
        try:
            with httpx.Client(timeout=30.0) as client:
                resp = client.post(token_url, data=payload)
                resp.raise_for_status()
                data = resp.json()
        except httpx.HTTPError as e:
            raise RuntimeError(f"刷新 Google access_token 失败: {e}") from e

        access_token = data.get("access_token")
        expires_in = data.get("expires_in", 3600)
        if not access_token:
            raise RuntimeError(f"Google token 响应缺少 access_token: {data}")

        self._google_token_cache = (access_token, time.time() + int(expires_in))
        return access_token

    def _google_indexing_api_publish(self, url: str, access_token: str) -> Dict[str, Any]:
        """调用 Google Indexing API 提交 URL 通知

        Args:
            url: 要提交的 URL
            access_token: OAuth2 访问令牌

        Returns:
            API 响应字典

        Raises:
            RuntimeError: API 调用失败
        """
        api_url = "https://indexing.googleapis.com/v3/urlNotifications:publish"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }
        body = {"url": url, "type": "URL_UPDATED"}
        try:
            with httpx.Client(timeout=30.0) as client:
                resp = client.post(api_url, headers=headers, json=body)
                # 200/201 表示成功；4xx 抛出携带响应内容的异常
                if resp.status_code >= 400:
                    raise RuntimeError(
                        f"Google Indexing API 返回 {resp.status_code}: {resp.text}"
                    )
                resp.raise_for_status()
                return resp.json() if resp.text else {}
        except httpx.HTTPError as e:
            raise RuntimeError(f"调用 Google Indexing API 失败: {e}") from e

    def _google_search_analytics_query(
        self, start_date: str, end_date: str, access_token: str
    ) -> Dict[str, Any]:
        """调用 Google Search Console API 查询搜索分析数据

        Args:
            start_date: 开始日期 YYYY-MM-DD
            end_date: 结束日期 YYYY-MM-DD
            access_token: OAuth2 访问令牌

        Returns:
            API 响应字典（含 rows）

        Raises:
            RuntimeError: API 调用失败
        """
        site_url = self.config.google_site_url
        if not site_url:
            raise RuntimeError("Google site_url 未配置，无法查询搜索分析")

        encoded_site = httpx.URL(site_url).path or site_url
        api_url = f"https://www.googleapis.com/webmasters/v3/sites/{encoded_site}/searchAnalytics/query"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }
        body = {
            "startDate": start_date,
            "endDate": end_date,
            "dimensions": ["query"],
            "rowLimit": 1000,
        }
        try:
            with httpx.Client(timeout=30.0) as client:
                resp = client.post(api_url, headers=headers, json=body)
                if resp.status_code >= 400:
                    raise RuntimeError(
                        f"Google Search Console API 返回 {resp.status_code}: {resp.text}"
                    )
                resp.raise_for_status()
                return resp.json() if resp.text else {}
        except httpx.HTTPError as e:
            raise RuntimeError(f"调用 Google Search Console API 失败: {e}") from e

    def _bing_submit_url_api(self, url: str) -> Dict[str, Any]:
        """调用 Bing Webmaster API 提交 URL

        使用 Bing Indexing API（https://ssl.bing.com/webmaster/api.svc/2.0/SubmitUrl）

        Args:
            url: 要提交的 URL

        Returns:
            API 响应字典

        Raises:
            RuntimeError: 凭证缺失或 API 调用失败
        """
        cfg = self.config
        if not cfg.bing_api_key:
            raise RuntimeError("Bing API key 未配置")
        if not cfg.bing_site_url:
            raise RuntimeError("Bing site_url 未配置")

        api_url = "https://ssl.bing.com/webmaster/api.svc/2.0/SubmitUrl"
        params = {"apikey": cfg.bing_api_key}
        body = {"siteUrl": cfg.bing_site_url, "url": url}
        try:
            with httpx.Client(timeout=30.0) as client:
                resp = client.post(api_url, params=params, json=body)
                if resp.status_code >= 400:
                    raise RuntimeError(
                        f"Bing Indexing API 返回 {resp.status_code}: {resp.text}"
                    )
                resp.raise_for_status()
                return resp.json() if resp.text else {}
        except httpx.HTTPError as e:
            raise RuntimeError(f"调用 Bing Indexing API 失败: {e}") from e

    def _google_submit_sitemap_api(self, sitemap_url: str, access_token: str) -> Dict[str, Any]:
        """调用 Google Search Console API 提交 Sitemap

        PUT /webmasters/v3/sites/{site}/sitemaps/{feedpath}

        Args:
            sitemap_url: Sitemap URL
            access_token: OAuth2 访问令牌

        Returns:
            API 响应字典

        Raises:
            RuntimeError: 配置缺失或 API 调用失败
        """
        site_url = self.config.google_site_url
        if not site_url:
            raise RuntimeError("Google site_url 未配置，无法提交 Sitemap")

        encoded_site = httpx.URL(site_url).path or site_url
        api_url = (
            f"https://www.googleapis.com/webmasters/v3/sites/{encoded_site}"
            f"/sitemaps/{httpx.URL(sitemap_url).path or sitemap_url}"
        )
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }
        body = {"path": sitemap_url}
        try:
            with httpx.Client(timeout=30.0) as client:
                resp = client.put(api_url, headers=headers, json=body)
                if resp.status_code >= 400:
                    raise RuntimeError(
                        f"Google Sitemap API 返回 {resp.status_code}: {resp.text}"
                    )
                resp.raise_for_status()
                return resp.json() if resp.text else {}
        except httpx.HTTPError as e:
            raise RuntimeError(f"调用 Google Sitemap API 失败: {e}") from e

    def _bing_submit_sitemap_api(self, sitemap_url: str) -> Dict[str, Any]:
        """调用 Bing Webmaster API 提交 Sitemap

        Args:
            sitemap_url: Sitemap URL

        Returns:
            API 响应字典

        Raises:
            RuntimeError: 凭证缺失或 API 调用失败
        """
        cfg = self.config
        if not cfg.bing_api_key:
            raise RuntimeError("Bing API key 未配置")
        if not cfg.bing_site_url:
            raise RuntimeError("Bing site_url 未配置")

        api_url = "https://ssl.bing.com/webmaster/api.svc/2.0/SubmitSitemap"
        params = {"apikey": cfg.bing_api_key}
        body = {"siteUrl": cfg.bing_site_url, "sitemapUrl": sitemap_url}
        try:
            with httpx.Client(timeout=30.0) as client:
                resp = client.post(api_url, params=params, json=body)
                if resp.status_code >= 400:
                    raise RuntimeError(
                        f"Bing Sitemap API 返回 {resp.status_code}: {resp.text}"
                    )
                resp.raise_for_status()
                return resp.json() if resp.text else {}
        except httpx.HTTPError as e:
            raise RuntimeError(f"调用 Bing Sitemap API 失败: {e}") from e

    # ==================== Google Search Console ====================

    async def submit_url_to_google(self, url: str) -> IndexingResult:
        """
        提交URL到Google索引

        Args:
            url: 要提交的URL

        Returns:
            提交结果
        """
        result = IndexingResult(
            url=url,
            search_engine=SearchEngine.GOOGLE,
            status=IndexingStatus.SUBMITTED,
            submitted_at=time.time(),
        )

        if not self.config.google_enabled:
            result.status = IndexingStatus.FAILED
            result.message = "Google Search Console is not enabled"
            result.error_code = "not_enabled"
            return result

        try:
            # 调用真实 Google Indexing API：先获取 OAuth2 access_token，再提交 URL 通知
            access_token = self._get_google_access_token()
            self._google_indexing_api_publish(url, access_token)
            result.status = IndexingStatus.SUBMITTED
            result.message = "URL submitted to Google successfully"
        except Exception as e:
            result.status = IndexingStatus.FAILED
            result.message = str(e)
            result.error_code = "api_error"

        # 记录历史
        self._record_submission(result)
        return result

    async def submit_urls_to_google(self, urls: List[str]) -> List[IndexingResult]:
        """
        批量提交URL到Google索引

        Args:
            urls: URL列表

        Returns:
            提交结果列表
        """
        results = []
        for url in urls:
            result = await self.submit_url_to_google(url)
            results.append(result)
        return results

    async def get_google_indexing_status(self, url: str) -> IndexingResult:
        """
        获取Google索引状态

        Args:
            url: 要检查的URL

        Returns:
            索引状态
        """
        result = IndexingResult(
            url=url,
            search_engine=SearchEngine.GOOGLE,
            status=IndexingStatus.NOT_SUBMITTED,
        )

        if not self.config.google_enabled:
            result.message = "Google Search Console is not enabled"
            return result

        # 检查提交历史
        history = self._submission_history.get(url, [])
        if history:
            latest = history[-1]
            result = latest

        return result

    async def get_google_analytics(self, start_date: str, end_date: str) -> SearchAnalyticsData:
        """
        获取Google搜索分析数据

        Args:
            start_date: 开始日期 YYYY-MM-DD
            end_date: 结束日期 YYYY-MM-DD

        Returns:
            分析数据
        """
        cache_key = f"google_{start_date}_{end_date}"
        if cache_key in self._analytics_cache:
            return self._analytics_cache[cache_key]

        analytics = SearchAnalyticsData(date=f"{start_date} to {end_date}")

        if not self.config.google_enabled:
            return analytics

        try:
            # 调用真实 Google Search Console API 查询搜索分析数据
            access_token = self._get_google_access_token()
            raw = self._google_search_analytics_query(start_date, end_date, access_token)

            rows = raw.get("rows", []) or []
            total_clicks = 0
            total_impressions = 0
            position_sum = 0.0
            keywords: List[Dict[str, Any]] = []

            for row in rows:
                clicks = int(row.get("clicks", 0))
                impressions = int(row.get("impressions", 0))
                ctr = float(row.get("ctr", 0.0)) * 100  # API 返回 0-1，转为百分比
                position = float(row.get("position", 0.0))
                total_clicks += clicks
                total_impressions += impressions
                position_sum += position

                keys = row.get("keys", []) or []
                keyword_text = keys[0] if keys else ""
                keywords.append({
                    "keyword": keyword_text,
                    "clicks": clicks,
                    "impressions": impressions,
                    "ctr": round(ctr, 2),
                    "position": round(position, 2),
                })

            analytics.clicks = total_clicks
            analytics.impressions = total_impressions
            analytics.ctr = round(total_clicks / total_impressions * 100, 2) if total_impressions else 0.0
            analytics.average_position = round(position_sum / len(rows), 2) if rows else 0.0
            analytics.keywords = keywords

            self._analytics_cache[cache_key] = analytics

        except Exception as e:
            logger.error(f"获取 Google 搜索分析数据失败: {e}")

        return analytics

    async def submit_sitemap_to_google(self, sitemap_url: str) -> bool:
        """
        提交Sitemap到Google

        Args:
            sitemap_url: Sitemap URL

        Returns:
            是否成功
        """
        if not self.config.google_enabled:
            return False

        try:
            # 调用真实 Google Search Console API 提交 Sitemap
            access_token = self._get_google_access_token()
            self._google_submit_sitemap_api(sitemap_url, access_token)
            return True
        except Exception as e:
            logger.error(f"提交 Sitemap 到 Google 失败: {e}")
            return False

    # ==================== Bing Webmaster Tools ====================

    async def submit_url_to_bing(self, url: str) -> IndexingResult:
        """
        提交URL到Bing索引

        Args:
            url: 要提交的URL

        Returns:
            提交结果
        """
        result = IndexingResult(
            url=url,
            search_engine=SearchEngine.BING,
            status=IndexingStatus.SUBMITTED,
            submitted_at=time.time(),
        )

        if not self.config.bing_enabled:
            result.status = IndexingStatus.FAILED
            result.message = "Bing Webmaster Tools is not enabled"
            result.error_code = "not_enabled"
            return result

        try:
            # 调用真实 Bing Indexing API 提交 URL
            self._bing_submit_url_api(url)
            result.status = IndexingStatus.SUBMITTED
            result.message = "URL submitted to Bing successfully"
        except Exception as e:
            result.status = IndexingStatus.FAILED
            result.message = str(e)
            result.error_code = "api_error"

        self._record_submission(result)
        return result

    async def submit_urls_to_bing(self, urls: List[str]) -> List[IndexingResult]:
        """
        批量提交URL到Bing索引

        Args:
            urls: URL列表

        Returns:
            提交结果列表
        """
        results = []
        for url in urls:
            result = await self.submit_url_to_bing(url)
            results.append(result)
        return results

    async def get_bing_indexing_status(self, url: str) -> IndexingResult:
        """
        获取Bing索引状态

        Args:
            url: 要检查的URL

        Returns:
            索引状态
        """
        result = IndexingResult(
            url=url,
            search_engine=SearchEngine.BING,
            status=IndexingStatus.NOT_SUBMITTED,
        )

        if not self.config.bing_enabled:
            result.message = "Bing Webmaster Tools is not enabled"
            return result

        history = self._submission_history.get(url, [])
        if history:
            bing_history = [h for h in history if h.search_engine == SearchEngine.BING]
            if bing_history:
                result = bing_history[-1]

        return result

    async def submit_sitemap_to_bing(self, sitemap_url: str) -> bool:
        """
        提交Sitemap到Bing

        Args:
            sitemap_url: Sitemap URL

        Returns:
            是否成功
        """
        if not self.config.bing_enabled:
            return False

        try:
            # 调用真实 Bing Webmaster API 提交 Sitemap
            self._bing_submit_sitemap_api(sitemap_url)
            return True
        except Exception as e:
            logger.error(f"提交 Sitemap 到 Bing 失败: {e}")
            return False

    # ==================== 通用方法 ====================

    async def submit_url(self, url: str, engines: Optional[List[SearchEngine]] = None) -> List[IndexingResult]:
        """
        提交URL到多个搜索引擎

        Args:
            url: 要提交的URL
            engines: 搜索引擎列表，None表示所有已启用的

        Returns:
            提交结果列表
        """
        if engines is None:
            engines = []
            if self.config.google_enabled:
                engines.append(SearchEngine.GOOGLE)
            if self.config.bing_enabled:
                engines.append(SearchEngine.BING)

        results = []
        for engine in engines:
            if engine == SearchEngine.GOOGLE:
                result = await self.submit_url_to_google(url)
            elif engine == SearchEngine.BING:
                result = await self.submit_url_to_bing(url)
            else:
                continue
            results.append(result)

        return results

    async def submit_urls(self, urls: List[str], engines: Optional[List[SearchEngine]] = None) -> List[IndexingResult]:
        """
        批量提交URL到多个搜索引擎

        Args:
            urls: URL列表
            engines: 搜索引擎列表

        Returns:
            提交结果列表
        """
        all_results = []
        for url in urls:
            results = await self.submit_url(url, engines)
            all_results.extend(results)
        return all_results

    async def submit_sitemap(self, sitemap_url: str, engines: Optional[List[SearchEngine]] = None) -> Dict[str, bool]:
        """
        提交Sitemap到多个搜索引擎

        Args:
            sitemap_url: Sitemap URL
            engines: 搜索引擎列表

        Returns:
            各引擎提交结果
        """
        if engines is None:
            engines = []
            if self.config.google_enabled:
                engines.append(SearchEngine.GOOGLE)
            if self.config.bing_enabled:
                engines.append(SearchEngine.BING)

        results = {}
        for engine in engines:
            if engine == SearchEngine.GOOGLE:
                results[engine.value] = await self.submit_sitemap_to_google(sitemap_url)
            elif engine == SearchEngine.BING:
                results[engine.value] = await self.submit_sitemap_to_bing(sitemap_url)

        return results

    # ==================== 排名追踪 ====================

    def _fetch_keyword_position_from_google(self, keyword: str) -> Optional[int]:
        """通过 Google Search Console API 获取关键词的真实平均排名

        查询过去 7 天内该关键词的搜索表现，返回平均排名（取整）。
        若无数据或凭证缺失，返回 None。

        Args:
            keyword: 关键词

        Returns:
            平均排名（整数），无数据时返回 None
        """
        try:
            access_token = self._get_google_access_token()
        except Exception as e:
            logger.debug(f"获取 Google access_token 失败，无法查询关键词排名: {e}")
            return None

        end_date = datetime.utcnow().date()
        start_date = end_date - timedelta(days=7)
        site_url = self.config.google_site_url
        if not site_url:
            logger.debug("Google site_url 未配置，无法查询关键词排名")
            return None

        encoded_site = httpx.URL(site_url).path or site_url
        api_url = f"https://www.googleapis.com/webmasters/v3/sites/{encoded_site}/searchAnalytics/query"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }
        body = {
            "startDate": start_date.strftime("%Y-%m-%d"),
            "endDate": end_date.strftime("%Y-%m-%d"),
            "dimensions": ["query"],
            "dimensionFilterGroups": [{
                "filters": [{
                    "dimension": "query",
                    "operator": "equals",
                    "expression": keyword,
                }]
            }],
            "rowLimit": 1,
        }
        try:
            with httpx.Client(timeout=30.0) as client:
                resp = client.post(api_url, headers=headers, json=body)
                if resp.status_code >= 400:
                    logger.debug(
                        f"Google Search Console 关键词排名查询返回 {resp.status_code}: {resp.text}"
                    )
                    return None
                resp.raise_for_status()
                data = resp.json() if resp.text else {}
        except httpx.HTTPError as e:
            logger.debug(f"调用 Google Search Console 关键词排名查询失败: {e}")
            return None

        rows = data.get("rows", []) or []
        if not rows:
            return None
        position = float(rows[0].get("position", 0.0))
        return int(round(position))

    def track_keyword_ranking(self, keyword: str, url: str,
                              search_engine: SearchEngine = SearchEngine.GOOGLE,
                              country: str = "", device: str = "desktop") -> RankingData:
        """
        追踪关键词排名

        Args:
            keyword: 关键词
            url: URL
            search_engine: 搜索引擎
            country: 国家
            device: 设备

        Returns:
            排名数据
        """
        # 查找现有的排名数据
        existing = None
        for ranking in self._rankings:
            if (ranking.keyword == keyword and
                ranking.url == url and
                ranking.search_engine == search_engine and
                ranking.country == country and
                ranking.device == device):
                existing = ranking
                break

        # 通过真实 API 获取关键词排名；无数据时记为 0（表示未进入索引或无曝光）
        fetched = None
        if search_engine == SearchEngine.GOOGLE:
            fetched = self._fetch_keyword_position_from_google(keyword)
        new_position = fetched if fetched is not None else 0

        if existing:
            previous_position = existing.position
            change = previous_position - new_position  # 排名上升为正
            existing.previous_position = previous_position
            existing.position = new_position
            existing.change = change
            existing.last_checked = time.time()
            return existing
        else:
            ranking = RankingData(
                keyword=keyword,
                url=url,
                position=new_position,
                search_engine=search_engine,
                country=country,
                device=device,
                last_checked=time.time(),
            )
            self._rankings.append(ranking)
            return ranking

    def get_rankings(self, search_engine: Optional[SearchEngine] = None) -> List[RankingData]:
        """
        获取所有排名数据

        Args:
            search_engine: 可选，按搜索引擎过滤

        Returns:
            排名数据列表
        """
        if search_engine:
            return [r for r in self._rankings if r.search_engine == search_engine]
        return self._rankings.copy()

    # ==================== 收录监控 ====================

    async def check_indexing_status(self, urls: List[str], 
                                     engines: Optional[List[SearchEngine]] = None) -> List[IndexingResult]:
        """
        批量检查索引状态

        Args:
            urls: URL列表
            engines: 搜索引擎列表

        Returns:
            索引状态列表
        """
        results = []
        for url in urls:
            if engines is None or SearchEngine.GOOGLE in engines:
                status = await self.get_google_indexing_status(url)
                results.append(status)
            if engines is None or SearchEngine.BING in engines:
                status = await self.get_bing_indexing_status(url)
                results.append(status)
        return results

    def get_indexing_stats(self) -> Dict[str, Any]:
        """
        获取索引统计

        Returns:
            统计信息
        """
        total_urls = len(self._submission_history)
        indexed_count = 0
        submitted_count = 0
        failed_count = 0

        for url, history in self._submission_history.items():
            if history:
                latest = history[-1]
                if latest.status == IndexingStatus.INDEXED:
                    indexed_count += 1
                elif latest.status == IndexingStatus.SUBMITTED or latest.status == IndexingStatus.PROCESSING:
                    submitted_count += 1
                elif latest.status == IndexingStatus.FAILED:
                    failed_count += 1

        return {
            "total_urls": total_urls,
            "indexed": indexed_count,
            "submitted": submitted_count,
            "failed": failed_count,
            "index_rate": round(indexed_count / total_urls * 100, 2) if total_urls > 0 else 0,
        }

    # ==================== 辅助方法 ====================

    def _record_submission(self, result: IndexingResult):
        """记录提交历史"""
        url = result.url
        if url not in self._submission_history:
            self._submission_history[url] = []
        self._submission_history[url].append(result)

    def get_submission_history(self, url: str) -> List[IndexingResult]:
        """获取提交历史"""
        return self._submission_history.get(url, []).copy()

    def get_all_submission_history(self) -> Dict[str, List[IndexingResult]]:
        """获取所有提交历史"""
        return {k: v.copy() for k, v in self._submission_history.items()}

    def set_config(self, config: SearchConsoleConfig):
        """设置配置"""
        self.config = config

    def get_config(self) -> SearchConsoleConfig:
        """获取配置"""
        return self.config


# 单例实例
_search_console_service = None


def get_search_console_service() -> SearchConsoleService:
    """获取搜索控制台服务单例"""
    global _search_console_service
    if _search_console_service is None:
        _search_console_service = SearchConsoleService()
    return _search_console_service
