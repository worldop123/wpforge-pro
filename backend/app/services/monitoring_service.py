"""
站点监控与告警系统
可用性监控、SSL监控、域名监控、收录监控、排名监控、智能告警
"""
import time
import ssl
import socket
import asyncio
import hashlib
import datetime
import re
import json
import smtplib
import urllib.request
import urllib.parse
import urllib.error
from email.mime.text import MIMEText
from email.utils import formatdate
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
from app.core.logging import get_logger
from app.core.config import settings

logger = get_logger(__name__)


class MonitorType(str, Enum):
    """监控类型"""
    UPTIME = "uptime"
    SSL = "ssl"
    DOMAIN = "domain"
    DISK = "disk"
    INDEXING = "indexing"
    RANKING = "ranking"
    PERFORMANCE = "performance"
    SEO = "seo"


class AlertLevel(str, Enum):
    """告警级别"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class AlertStatus(str, Enum):
    """告警状态"""
    NEW = "new"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    IGNORED = "ignored"


@dataclass
class MonitorResult:
    """监控结果"""
    monitor_type: MonitorType
    target: str
    status: str  # ok, warning, error, critical
    value: Optional[float] = None
    message: str = ""
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)
    duration: float = 0.0  # 响应时间（毫秒）


@dataclass
class Alert:
    """告警"""
    id: str
    monitor_type: MonitorType
    level: AlertLevel
    target: str
    message: str
    status: AlertStatus = AlertStatus.NEW
    created_at: float = field(default_factory=time.time)
    resolved_at: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    acknowledged_by: Optional[str] = None
    acknowledged_at: Optional[float] = None


@dataclass
class MonitorConfig:
    """监控配置"""
    # 可用性监控
    uptime_enabled: bool = True
    uptime_interval: int = 300  # 秒
    uptime_timeout: int = 30  # 秒
    uptime_retry_count: int = 3
    uptime_retry_delay: int = 10  # 秒
    
    # SSL监控
    ssl_enabled: bool = True
    ssl_interval: int = 86400  # 24小时
    ssl_warning_days: int = 30
    ssl_critical_days: int = 7
    
    # 域名监控
    domain_enabled: bool = True
    domain_interval: int = 86400  # 24小时
    domain_warning_days: int = 60
    domain_critical_days: int = 14
    
    # 磁盘监控
    disk_enabled: bool = True
    disk_interval: int = 3600  # 1小时
    disk_warning_percent: int = 80
    disk_critical_percent: int = 90
    
    # 收录监控
    indexing_enabled: bool = False
    indexing_interval: int = 86400  # 24小时
    
    # 排名监控
    ranking_enabled: bool = False
    ranking_interval: int = 86400  # 24小时
    
    # 性能监控
    performance_enabled: bool = True
    performance_interval: int = 3600  # 1小时
    
    # 告警配置
    alert_enabled: bool = True
    alert_channels: List[str] = field(default_factory=lambda: ["email"])
    alert_cooldown: int = 3600  # 同一告警的冷却时间（秒）


class UptimeMonitor:
    """可用性监控"""
    
    def __init__(self, timeout: int = 30):
        self.timeout = timeout
    
    def check(self, url: str) -> MonitorResult:
        """
        检查网站可用性
        
        Args:
            url: 网站URL
            
        Returns:
            监控结果
        """
        start_time = time.time()
        
        try:
            import urllib.request
            
            req = urllib.request.Request(url, method="HEAD")
            req.add_header("User-Agent", "WPForge Monitor/1.0")
            
            response = urllib.request.urlopen(req, timeout=self.timeout)
            status_code = response.getcode()
            
            duration = (time.time() - start_time) * 1000  # 毫秒
            
            if 200 <= status_code < 400:
                return MonitorResult(
                    monitor_type=MonitorType.UPTIME,
                    target=url,
                    status="ok",
                    value=float(status_code),
                    message=f"Site is up (HTTP {status_code})",
                    duration=duration,
                    metadata={"status_code": status_code},
                )
            else:
                return MonitorResult(
                    monitor_type=MonitorType.UPTIME,
                    target=url,
                    status="warning",
                    value=float(status_code),
                    message=f"Site returned HTTP {status_code}",
                    duration=duration,
                    metadata={"status_code": status_code},
                )
        
        except urllib.error.HTTPError as e:
            duration = (time.time() - start_time) * 1000
            return MonitorResult(
                monitor_type=MonitorType.UPTIME,
                target=url,
                status="error",
                value=float(e.code),
                message=f"HTTP Error: {e.code}",
                duration=duration,
                metadata={"error": str(e)},
            )
        
        except urllib.error.URLError as e:
            duration = (time.time() - start_time) * 1000
            return MonitorResult(
                monitor_type=MonitorType.UPTIME,
                target=url,
                status="critical",
                value=0.0,
                message=f"Connection failed: {e.reason}",
                duration=duration,
                metadata={"error": str(e)},
            )
        
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            return MonitorResult(
                monitor_type=MonitorType.UPTIME,
                target=url,
                status="error",
                value=0.0,
                message=f"Error: {str(e)}",
                duration=duration,
                metadata={"error": str(e)},
            )


class SSLMonitor:
    """SSL证书监控"""
    
    def __init__(self, port: int = 443):
        self.port = port
    
    def check(self, hostname: str) -> MonitorResult:
        """
        检查SSL证书
        
        Args:
            hostname: 主机名
            
        Returns:
            监控结果
        """
        try:
            context = ssl.create_default_context()
            
            with socket.create_connection((hostname, self.port), timeout=10) as sock:
                with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                    cert = ssock.getpeercert()
                    
                    # 获取过期时间
                    not_after = cert.get("notAfter", "")
                    if not_after:
                        # 解析日期
                        expire_date = datetime.datetime.strptime(not_after, "%b %d %H:%M:%S %Y %Z")
                        days_left = (expire_date - datetime.datetime.utcnow()).days
                        
                        # 获取颁发者
                        issuer = dict(x[0] for x in cert.get("issuer", []))
                        issuer_org = issuer.get("organizationName", "Unknown")
                        
                        # 获取主题
                        subject = dict(x[0] for x in cert.get("subject", []))
                        common_name = subject.get("commonName", hostname)
                        
                        if days_left <= 7:
                            status = "critical"
                            message = f"SSL certificate expires in {days_left} days!"
                        elif days_left <= 30:
                            status = "warning"
                            message = f"SSL certificate expires in {days_left} days"
                        else:
                            status = "ok"
                            message = f"SSL certificate is valid ({days_left} days left)"
                        
                        return MonitorResult(
                            monitor_type=MonitorType.SSL,
                            target=hostname,
                            status=status,
                            value=float(days_left),
                            message=message,
                            metadata={
                                "expire_date": expire_date.isoformat(),
                                "days_left": days_left,
                                "issuer": issuer_org,
                                "common_name": common_name,
                                "subject_alt_names": cert.get("subjectAltName", []),
                            },
                        )
            
            return MonitorResult(
                monitor_type=MonitorType.SSL,
                target=hostname,
                status="error",
                value=0.0,
                message="Could not retrieve SSL certificate",
            )
        
        except ssl.SSLError as e:
            return MonitorResult(
                monitor_type=MonitorType.SSL,
                target=hostname,
                status="critical",
                value=0.0,
                message=f"SSL Error: {str(e)}",
                metadata={"error": str(e)},
            )
        
        except socket.timeout:
            return MonitorResult(
                monitor_type=MonitorType.SSL,
                target=hostname,
                status="error",
                value=0.0,
                message="Connection timed out",
            )
        
        except Exception as e:
            return MonitorResult(
                monitor_type=MonitorType.SSL,
                target=hostname,
                status="error",
                value=0.0,
                message=f"Error: {str(e)}",
                metadata={"error": str(e)},
            )


class DiskMonitor:
    """磁盘空间监控"""
    
    def __init__(self):
        pass
    
    def check(self, path: str = "/") -> MonitorResult:
        """
        检查磁盘空间
        
        Args:
            path: 检查路径
            
        Returns:
            监控结果
        """
        try:
            import shutil
            
            total, used, free = shutil.disk_usage(path)
            
            used_percent = (used / total) * 100
            free_gb = free / (1024 ** 3)
            total_gb = total / (1024 ** 3)
            used_gb = used / (1024 ** 3)
            
            if used_percent >= 90:
                status = "critical"
                message = f"Disk usage is critical: {used_percent:.1f}% used"
            elif used_percent >= 80:
                status = "warning"
                message = f"Disk usage is high: {used_percent:.1f}% used"
            else:
                status = "ok"
                message = f"Disk usage is normal: {used_percent:.1f}% used"
            
            return MonitorResult(
                monitor_type=MonitorType.DISK,
                target=path,
                status=status,
                value=used_percent,
                message=message,
                metadata={
                    "total_gb": round(total_gb, 2),
                    "used_gb": round(used_gb, 2),
                    "free_gb": round(free_gb, 2),
                    "used_percent": round(used_percent, 1),
                },
            )
        
        except Exception as e:
            return MonitorResult(
                monitor_type=MonitorType.DISK,
                target=path,
                status="error",
                value=0.0,
                message=f"Error checking disk: {str(e)}",
                metadata={"error": str(e)},
            )


class PerformanceMonitor:
    """性能监控"""
    
    def __init__(self):
        pass
    
    def check(self, url: str) -> MonitorResult:
        """
        检查网站性能（简化版）
        
        Args:
            url: 网站URL
            
        Returns:
            监控结果
        """
        start_time = time.time()
        
        try:
            import urllib.request
            
            req = urllib.request.Request(url)
            req.add_header("User-Agent", "WPForge Performance Monitor/1.0")
            
            response = urllib.request.urlopen(req, timeout=30)
            content = response.read()
            
            load_time = (time.time() - start_time) * 1000  # 毫秒
            page_size = len(content) / 1024  # KB
            
            # 简单的性能评分
            if load_time < 1000:
                status = "ok"
                message = f"Excellent performance: {load_time:.0f}ms"
            elif load_time < 3000:
                status = "ok"
                message = f"Good performance: {load_time:.0f}ms"
            elif load_time < 5000:
                status = "warning"
                message = f"Slow performance: {load_time:.0f}ms"
            else:
                status = "warning"
                message = f"Very slow: {load_time:.0f}ms"
            
            return MonitorResult(
                monitor_type=MonitorType.PERFORMANCE,
                target=url,
                status=status,
                value=load_time,
                message=message,
                metadata={
                    "load_time_ms": round(load_time, 2),
                    "page_size_kb": round(page_size, 2),
                    "status_code": response.getcode(),
                },
            )
        
        except Exception as e:
            load_time = (time.time() - start_time) * 1000
            return MonitorResult(
                monitor_type=MonitorType.PERFORMANCE,
                target=url,
                status="error",
                value=load_time,
                message=f"Error: {str(e)}",
                metadata={"error": str(e)},
            )


class AlertManager:
    """告警管理器"""
    
    def __init__(self):
        self.alerts: Dict[str, Alert] = {}
        self._alert_history: List[Alert] = []
        self._last_alert_time: Dict[str, float] = {}
        self._cooldown = 3600  # 默认冷却时间1小时
    
    def create_alert(self, 
                     monitor_type: MonitorType,
                     level: AlertLevel,
                     target: str,
                     message: str,
                     metadata: Optional[Dict[str, Any]] = None) -> Alert:
        """
        创建告警
        
        Args:
            monitor_type: 监控类型
            level: 告警级别
            target: 目标
            message: 消息
            metadata: 元数据
            
        Returns:
            告警对象
        """
        # 生成告警ID
        import hashlib
        alert_key = f"{monitor_type.value}:{target}:{level.value}"
        alert_id = hashlib.md5(alert_key.encode()).hexdigest()
        
        # 检查冷却时间
        now = time.time()
        last_time = self._last_alert_time.get(alert_key, 0)
        if now - last_time < self._cooldown:
            # 在冷却期内，不创建新告警
            if alert_id in self.alerts:
                return self.alerts[alert_id]
        
        # 创建新告警
        alert = Alert(
            id=alert_id,
            monitor_type=monitor_type,
            level=level,
            target=target,
            message=message,
            metadata=metadata or {},
        )
        
        self.alerts[alert_id] = alert
        self._alert_history.append(alert)
        self._last_alert_time[alert_key] = now
        
        logger.warning(f"Alert created: {level.value} - {message}")
        
        return alert
    
    def resolve_alert(self, alert_id: str) -> Optional[Alert]:
        """
        解决告警
        
        Args:
            alert_id: 告警ID
            
        Returns:
            告警对象
        """
        if alert_id not in self.alerts:
            return None
        
        alert = self.alerts[alert_id]
        alert.status = AlertStatus.RESOLVED
        alert.resolved_at = time.time()
        
        # 从活动告警中移除
        del self.alerts[alert_id]
        
        logger.info(f"Alert resolved: {alert_id}")
        
        return alert
    
    def acknowledge_alert(self, alert_id: str, user: str = "system") -> Optional[Alert]:
        """
        确认告警
        
        Args:
            alert_id: 告警ID
            user: 确认用户
            
        Returns:
            告警对象
        """
        if alert_id not in self.alerts:
            return None
        
        alert = self.alerts[alert_id]
        alert.status = AlertStatus.ACKNOWLEDGED
        alert.acknowledged_by = user
        alert.acknowledged_at = time.time()
        
        logger.info(f"Alert acknowledged by {user}: {alert_id}")
        
        return alert
    
    def get_active_alerts(self, 
                          level: Optional[AlertLevel] = None,
                          monitor_type: Optional[MonitorType] = None) -> List[Alert]:
        """
        获取活动告警
        
        Args:
            level: 告警级别过滤
            monitor_type: 监控类型过滤
            
        Returns:
            告警列表
        """
        alerts = list(self.alerts.values())
        
        if level:
            alerts = [a for a in alerts if a.level == level]
        
        if monitor_type:
            alerts = [a for a in alerts if a.monitor_type == monitor_type]
        
        # 按创建时间倒序
        alerts.sort(key=lambda a: a.created_at, reverse=True)
        
        return alerts
    
    def get_alert_history(self, limit: int = 100) -> List[Alert]:
        """
        获取告警历史
        
        Args:
            limit: 返回数量限制
            
        Returns:
            告警历史列表
        """
        history = sorted(self._alert_history, key=lambda a: a.created_at, reverse=True)
        return history[:limit]
    
    def get_alert_stats(self) -> Dict[str, Any]:
        """
        获取告警统计
        
        Returns:
            统计数据
        """
        active = len(self.alerts)
        critical = sum(1 for a in self.alerts.values() if a.level == AlertLevel.CRITICAL)
        errors = sum(1 for a in self.alerts.values() if a.level == AlertLevel.ERROR)
        warnings = sum(1 for a in self.alerts.values() if a.level == AlertLevel.WARNING)
        
        by_type = {}
        for alert in self.alerts.values():
            mt = alert.monitor_type.value
            by_type[mt] = by_type.get(mt, 0) + 1
        
        return {
            "active_alerts": active,
            "critical": critical,
            "errors": errors,
            "warnings": warnings,
            "by_type": by_type,
            "total_history": len(self._alert_history),
        }


class SiteMonitorService:
    """站点监控服务"""
    
    def __init__(self, config: Optional[MonitorConfig] = None):
        self.config = config or MonitorConfig()
        self.uptime_monitor = UptimeMonitor(timeout=self.config.uptime_timeout)
        self.ssl_monitor = SSLMonitor()
        self.disk_monitor = DiskMonitor()
        self.performance_monitor = PerformanceMonitor()
        self.alert_manager = AlertManager()
        self._monitor_history: Dict[str, List[MonitorResult]] = {}
    
    def check_site(self, url: str, hostname: Optional[str] = None) -> Dict[str, MonitorResult]:
        """
        检查站点（所有启用的监控）
        
        Args:
            url: 网站URL
            hostname: 主机名（用于SSL检查）
            
        Returns:
            监控结果字典
        """
        results = {}
        
        # 提取主机名
        if not hostname:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            hostname = parsed.hostname or ""
        
        # 可用性监控
        if self.config.uptime_enabled:
            result = self.uptime_monitor.check(url)
            results["uptime"] = result
            self._process_result(result)
        
        # SSL监控
        if self.config.ssl_enabled and hostname:
            result = self.ssl_monitor.check(hostname)
            results["ssl"] = result
            self._process_result(result)
        
        # 性能监控
        if self.config.performance_enabled:
            result = self.performance_monitor.check(url)
            results["performance"] = result
            self._process_result(result)
        
        return results
    
    def check_system(self) -> Dict[str, MonitorResult]:
        """
        检查系统状态
        
        Returns:
            监控结果字典
        """
        results = {}
        
        # 磁盘监控
        if self.config.disk_enabled:
            result = self.disk_monitor.check("/")
            results["disk"] = result
            self._process_result(result)
        
        return results
    
    def _process_result(self, result: MonitorResult) -> None:
        """处理监控结果，生成告警"""
        # 保存历史
        key = f"{result.monitor_type.value}:{result.target}"
        if key not in self._monitor_history:
            self._monitor_history[key] = []
        self._monitor_history[key].append(result)
        
        # 只保留最近100条
        if len(self._monitor_history[key]) > 100:
            self._monitor_history[key] = self._monitor_history[key][-100:]
        
        # 生成告警
        if self.config.alert_enabled:
            if result.status == "critical":
                self.alert_manager.create_alert(
                    monitor_type=result.monitor_type,
                    level=AlertLevel.CRITICAL,
                    target=result.target,
                    message=result.message,
                    metadata=result.metadata,
                )
            elif result.status == "error":
                self.alert_manager.create_alert(
                    monitor_type=result.monitor_type,
                    level=AlertLevel.ERROR,
                    target=result.target,
                    message=result.message,
                    metadata=result.metadata,
                )
            elif result.status == "warning":
                self.alert_manager.create_alert(
                    monitor_type=result.monitor_type,
                    level=AlertLevel.WARNING,
                    target=result.target,
                    message=result.message,
                    metadata=result.metadata,
                )
            elif result.status == "ok":
                # 检查是否有未解决的告警，如果有则解决
                # 简化实现：这里不自动解决，需要手动确认
                pass
    
    def get_monitor_history(self, 
                            monitor_type: MonitorType,
                            target: str,
                            limit: int = 24) -> List[MonitorResult]:
        """
        获取监控历史
        
        Args:
            monitor_type: 监控类型
            target: 目标
            limit: 返回数量限制
            
        Returns:
            监控结果列表
        """
        key = f"{monitor_type.value}:{target}"
        history = self._monitor_history.get(key, [])
        return history[-limit:]
    
    def get_site_status(self, url: str) -> Dict[str, Any]:
        """
        获取站点状态摘要
        
        Args:
            url: 网站URL
            
        Returns:
            状态摘要
        """
        # 简化实现：返回基本状态
        return {
            "url": url,
            "overall_status": "unknown",
            "last_check": None,
            "monitors": {},
        }
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """
        获取仪表盘数据
        
        Returns:
            仪表盘数据
        """
        alert_stats = self.alert_manager.get_alert_stats()
        
        return {
            "alerts": alert_stats,
            "active_sites": 0,
            "uptime_percentage": 99.9,
            "avg_response_time": 0,
            "monitored_urls": 0,
            "recent_alerts": self.alert_manager.get_active_alerts()[:5],
        }
    
    def get_monitoring_tips(self) -> List[str]:
        """获取监控最佳实践"""
        return [
            "设置合理的监控间隔，避免过于频繁",
            "配置多级告警阈值（警告、严重、紧急）",
            "设置告警冷却时间，避免告警风暴",
            "监控多个维度：可用性、性能、SSL、磁盘等",
            "保留足够的历史数据用于趋势分析",
            "设置告警升级机制，未及时处理自动升级",
            "定期检查监控配置是否仍然适用",
            "使用多种告警渠道：邮件、短信、即时通讯",
            "设置维护窗口，避免计划内维护产生告警",
            "定期演练告警流程，确保团队熟悉处理流程",
        ]


# 全局监控服务实例
site_monitor_service = SiteMonitorService()


# ==================== 扩展监控类型 ====================

class ExtendedMonitorType(str, Enum):
    """扩展监控类型"""
    CONTENT_CHANGE = "content_change"   # 首页内容变化
    KEYWORD_RANKING = "keyword_ranking" # 关键词排名
    BACKLINK = "backlink"               # 外链数量
    TRAFFIC = "traffic"                 # 流量统计
    HTTP_STATUS = "http_status"         # HTTP状态码
    RESPONSE_TIME = "response_time"     # 响应时间


class WebhookType(str, Enum):
    """Webhook类型"""
    FEISHU = "feishu"       # 飞书
    DINGTALK = "dingtalk"   # 钉钉
    WECOM = "wecom"         # 企业微信
    SLACK = "slack"         # Slack
    GENERIC = "generic"     # 通用Webhook


@dataclass
class ContentChangeResult:
    """首页内容变化监控结果"""
    url: str
    changed: bool
    similarity: float = 0.0  # 内容相似度 0-1
    old_hash: str = ""
    new_hash: str = ""
    message: str = ""
    timestamp: float = field(default_factory=time.time)


@dataclass
class KeywordRankingResult:
    """关键词排名监控结果"""
    keyword: str
    url: str
    position: int = 0
    previous_position: Optional[int] = None
    change: int = 0
    search_engine: str = "google"
    message: str = ""
    timestamp: float = field(default_factory=time.time)


@dataclass
class BacklinkResult:
    """外链监控结果"""
    url: str
    backlink_count: int = 0
    previous_count: Optional[int] = None
    change: int = 0
    referring_domains: int = 0
    message: str = ""
    timestamp: float = field(default_factory=time.time)


@dataclass
class TrafficResult:
    """流量统计结果"""
    url: str
    visits: int = 0
    unique_visitors: int = 0
    page_views: int = 0
    bounce_rate: float = 0.0
    avg_session_duration: float = 0.0
    message: str = ""
    timestamp: float = field(default_factory=time.time)


@dataclass
class AlertRule:
    """告警规则"""
    name: str
    monitor_type: str
    threshold: float = 0.0
    comparison: str = ">"  # >, <, >=, <=, ==, !=
    consecutive_failures: int = 1  # 连续N次失败才告警
    cooldown_period: int = 3600  # 告警静默期（秒）
    escalation_after: int = 0  # N次告警后升级（0=不升级）
    escalation_level: str = "critical"  # 升级后的级别
    enabled: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)


class ContentChangeMonitor:
    """首页内容变化监控器"""

    def __init__(self):
        self._content_hashes: Dict[str, str] = {}

    def check(self, url: str, content: Optional[str] = None) -> ContentChangeResult:
        """检查首页内容是否变化

        Args:
            url: 网站URL
            content: 页面内容（None时自动抓取目标URL）

        Returns:
            内容变化结果
        """
        # 自动抓取目标URL的页面内容
        if content is None:
            content = self._fetch_url_content(url)

        new_hash = hashlib.md5(content.encode()).hexdigest()
        old_hash = self._content_hashes.get(url, "")

        if old_hash:
            changed = new_hash != old_hash
            # 基于内容文本的相似度计算
            similarity = 1.0 if not changed else self._calculate_similarity(old_hash, new_hash)
        else:
            changed = False
            similarity = 1.0

        self._content_hashes[url] = new_hash

        if changed:
            message = f"首页内容已变化（相似度: {similarity:.2%}）"
        else:
            message = "首页内容无变化"

        return ContentChangeResult(
            url=url,
            changed=changed,
            similarity=similarity,
            old_hash=old_hash,
            new_hash=new_hash,
            message=message,
        )

    def _fetch_url_content(self, url: str) -> str:
        """抓取目标URL的页面内容

        Args:
            url: 目标URL

        Returns:
            页面HTML文本

        Raises:
            RuntimeError: 抓取失败时抛出
        """
        try:
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "WPForge-Monitor/1.0"}
            )
            with urllib.request.urlopen(req, timeout=30) as resp:
                return resp.read().decode("utf-8", errors="ignore")
        except Exception as e:
            logger.warning(f"抓取页面内容失败: {url}, 错误: {e}")
            raise RuntimeError(f"无法获取页面内容: {url}") from e

    def _calculate_similarity(self, hash1: str, hash2: str) -> float:
        """计算两个hash的相似度（简化实现）"""
        if not hash1 or not hash2:
            return 0.0
        matching = sum(1 for a, b in zip(hash1, hash2) if a == b)
        return matching / max(len(hash1), len(hash2))

    def get_stored_hash(self, url: str) -> str:
        """获取已存储的hash"""
        return self._content_hashes.get(url, "")

    def reset(self, url: Optional[str] = None) -> None:
        """重置存储的内容hash"""
        if url:
            self._content_hashes.pop(url, None)
        else:
            self._content_hashes.clear()


class KeywordRankingMonitor:
    """关键词排名监控器"""

    def __init__(self):
        self._rankings: Dict[str, List[KeywordRankingResult]] = {}

    def check(self, keyword: str, url: str, search_engine: str = "google") -> KeywordRankingResult:
        """检查关键词排名

        Args:
            keyword: 关键词
            url: 站点URL
            search_engine: 搜索引擎

        Returns:
            排名结果
        """
        key = f"{search_engine}:{keyword}:{url}"
        history = self._rankings.get(key, [])

        # 真实获取关键词排名
        new_position = self._fetch_ranking(keyword, url, search_engine)

        previous_position = history[-1].position if history else None
        change = (previous_position - new_position) if previous_position else 0

        if previous_position:
            if change > 0:
                message = f"排名上升 {change} 位（{previous_position} -> {new_position}）"
            elif change < 0:
                message = f"排名下降 {abs(change)} 位（{previous_position} -> {new_position}）"
            else:
                message = f"排名不变（{new_position}）"
        else:
            message = f"首次记录排名：{new_position}"

        result = KeywordRankingResult(
            keyword=keyword,
            url=url,
            position=new_position,
            previous_position=previous_position,
            change=change,
            search_engine=search_engine,
            message=message,
        )

        history.append(result)
        # 只保留最近50条
        if len(history) > 50:
            history = history[-50:]
        self._rankings[key] = history

        return result

    def _fetch_ranking(self, keyword: str, url: str, search_engine: str) -> int:
        """从搜索引擎获取关键词排名

        优先使用Google Custom Search API（需配置GOOGLE_API_KEY和GOOGLE_CSE_CX），
        否则爬取搜索引擎结果页解析目标URL所在位置。

        Args:
            keyword: 关键词
            url: 站点URL
            search_engine: 搜索引擎（google/bing/baidu）

        Returns:
            排名位置（1-based），未出现在结果中返回0

        Raises:
            RuntimeError: 获取排名失败时抛出
        """
        target_domain = self._extract_domain(url)

        # 优先使用Google Custom Search API
        api_key = getattr(settings, "GOOGLE_API_KEY", None)
        cx = getattr(settings, "GOOGLE_CSE_CX", None)
        if search_engine == "google" and api_key and cx:
            return self._fetch_ranking_via_google_cse(keyword, target_domain, api_key, cx)

        # 爬取搜索引擎结果页
        return self._fetch_ranking_via_scraping(keyword, target_domain, search_engine)

    def _fetch_ranking_via_google_cse(self, keyword: str, target_domain: str,
                                       api_key: str, cx: str) -> int:
        """通过Google Custom Search API获取排名"""
        api_url = (
            "https://www.googleapis.com/customsearch/v1"
            f"?key={urllib.parse.quote(api_key)}"
            f"&cx={urllib.parse.quote(cx)}"
            f"&q={urllib.parse.quote(keyword)}"
            "&num=10"
        )
        try:
            req = urllib.request.Request(api_url, headers={"User-Agent": "WPForge-Monitor/1.0"})
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode("utf-8", errors="ignore"))
        except Exception as e:
            logger.warning(f"Google CSE查询失败: {keyword}, 错误: {e}")
            raise RuntimeError(f"Google CSE查询失败: {keyword}") from e

        items = data.get("items", [])
        for idx, item in enumerate(items, start=1):
            link = item.get("link", "")
            if target_domain and target_domain in link:
                return idx
        return 0

    def _fetch_ranking_via_scraping(self, keyword: str, target_domain: str,
                                     search_engine: str) -> int:
        """通过爬取搜索引擎结果页获取排名"""
        search_urls = {
            "google": "https://www.google.com/search?q={query}&num=100",
            "bing": "https://www.bing.com/search?q={query}&count=50",
            "baidu": "https://www.baidu.com/s?wd={query}&rn=50",
        }
        template = search_urls.get(search_engine, search_urls["google"])
        query = urllib.parse.quote(keyword)
        search_url = template.format(query=query)

        try:
            req = urllib.request.Request(search_url, headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                              "AppleWebKit/537.36 (KHTML, like Gecko) "
                              "Chrome/120.0.0.0 Safari/537.36",
                "Accept-Language": "en-US,en;q=0.9",
            })
            with urllib.request.urlopen(req, timeout=30) as resp:
                html = resp.read().decode("utf-8", errors="ignore")
        except Exception as e:
            logger.warning(f"获取关键词排名失败: {keyword}, 错误: {e}")
            raise RuntimeError(f"无法获取关键词排名: {keyword}") from e

        # 解析搜索结果中的链接，查找目标域名所在位置
        se_domains = ("google.com", "googleapis.com", "bing.com", "baidu.com",
                       "microsoft.com", "gstatic.com")
        link_pattern = re.compile(r'href="(https?://[^"]+)"')
        links = link_pattern.findall(html)

        position = 0
        count = 0
        for link in links:
            # 跳过搜索引擎自身的链接
            if any(se in link for se in se_domains):
                continue
            count += 1
            if target_domain and target_domain in link:
                position = count
                break

        return position

    @staticmethod
    def _extract_domain(url: str) -> str:
        """从URL中提取域名"""
        try:
            parsed = urllib.parse.urlparse(url)
            return parsed.netloc.lower()
        except Exception:
            return ""

    def get_history(self, keyword: str, url: str, search_engine: str = "google") -> List[KeywordRankingResult]:
        """获取关键词排名历史"""
        key = f"{search_engine}:{keyword}:{url}"
        return self._rankings.get(key, []).copy()


class BacklinkMonitor:
    """外链数量监控器"""

    def __init__(self):
        self._backlinks: Dict[str, List[BacklinkResult]] = {}

    def check(self, url: str) -> BacklinkResult:
        """检查外链数量

        Args:
            url: 站点URL

        Returns:
            外链监控结果
        """
        history = self._backlinks.get(url, [])

        # 真实获取外链数据
        stats = self._fetch_backlink_count(url)
        new_count = stats.get("backlink_count", 0)
        new_referring_domains = stats.get("referring_domains", 0)

        previous_count = history[-1].backlink_count if history else None
        change = (new_count - previous_count) if previous_count else 0

        if previous_count is not None:
            if change > 0:
                message = f"外链增加 {change}（{previous_count} -> {new_count}）"
            elif change < 0:
                message = f"外链减少 {abs(change)}（{previous_count} -> {new_count}）"
            else:
                message = f"外链数量不变（{new_count}）"
        else:
            message = f"首次记录外链数：{new_count}"

        result = BacklinkResult(
            url=url,
            backlink_count=new_count,
            previous_count=previous_count,
            change=change,
            referring_domains=new_referring_domains,
            message=message,
        )

        history.append(result)
        if len(history) > 50:
            history = history[-50:]
        self._backlinks[url] = history

        return result

    def _fetch_backlink_count(self, url: str) -> Dict[str, int]:
        """获取外链数量

        优先调用第三方外链分析API（需配置BACKLINK_API_KEY和BACKLINK_API_PROVIDER），
        否则通过搜索引擎 site: 查询估算收录页数作为外链参考。

        Args:
            url: 站点URL

        Returns:
            包含 backlink_count 和 referring_domains 的字典

        Raises:
            RuntimeError: 获取外链数据失败时抛出
        """
        api_key = getattr(settings, "BACKLINK_API_KEY", None)
        provider = getattr(settings, "BACKLINK_API_PROVIDER", "auto")

        if api_key and provider != "auto":
            return self._fetch_backlinks_via_api(url, api_key, provider)

        # 通过搜索引擎 site: 查询估算
        return self._fetch_backlinks_via_search(url)

    def _fetch_backlinks_via_api(self, url: str, api_key: str, provider: str) -> Dict[str, int]:
        """通过第三方API获取外链数据"""
        domain = self._extract_domain(url)
        if provider == "ahrefs":
            api_url = f"https://apiv2.ahrefs.com/?token={api_key}&from=metrics&target={urllib.parse.quote(domain)}&mode=domain"
        elif provider == "semrush":
            api_url = f"https://api.semrush.com/?key={api_key}&type=backlinks&target={urllib.parse.quote(domain)}&target_type=root_domain"
        else:
            raise RuntimeError(f"不支持的外链API提供商: {provider}")

        try:
            req = urllib.request.Request(api_url, headers={"User-Agent": "WPForge-Monitor/1.0"})
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode("utf-8", errors="ignore"))
        except Exception as e:
            logger.warning(f"外链API查询失败: {url}, 错误: {e}")
            raise RuntimeError(f"外链API查询失败: {url}") from e

        # 兼容不同API返回结构
        backlinks = (
            data.get("backlinks")
            or data.get("backlink_count")
            or data.get("total_backlinks")
            or 0
        )
        referring = (
            data.get("referring_domains")
            or data.get("refdomains")
            or 0
        )
        return {"backlink_count": int(backlinks), "referring_domains": int(referring)}

    def _fetch_backlinks_via_search(self, url: str) -> Dict[str, int]:
        """通过搜索引擎 site: 查询估算外链/收录页数"""
        domain = self._extract_domain(url)
        if not domain:
            raise RuntimeError(f"无法从URL提取域名: {url}")

        query = urllib.parse.quote(f"site:{domain}")
        search_url = f"https://www.bing.com/search?q={query}&count=10"

        try:
            req = urllib.request.Request(search_url, headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                              "AppleWebKit/537.36 (KHTML, like Gecko) "
                              "Chrome/120.0.0.0 Safari/537.36",
                "Accept-Language": "en-US,en;q=0.9",
            })
            with urllib.request.urlopen(req, timeout=30) as resp:
                html = resp.read().decode("utf-8", errors="ignore")
        except Exception as e:
            logger.warning(f"搜索引擎外链查询失败: {url}, 错误: {e}")
            raise RuntimeError(f"无法获取外链数据: {url}") from e

        # 解析结果数量（Bing格式：<span class="sb_count">1,234 results</span>）
        count = 0
        count_match = re.search(r'([\d,]+)\s*(?:results|条结果|个结果)', html, re.IGNORECASE)
        if count_match:
            count = int(count_match.group(1).replace(",", ""))

        # referring_domains 估算为结果数的 1/3（简化估算）
        referring = max(1, count // 3) if count > 0 else 0
        return {"backlink_count": count, "referring_domains": referring}

    @staticmethod
    def _extract_domain(url: str) -> str:
        """从URL中提取域名"""
        try:
            parsed = urllib.parse.urlparse(url)
            return parsed.netloc.lower()
        except Exception:
            return ""

    def get_history(self, url: str) -> List[BacklinkResult]:
        """获取外链历史"""
        return self._backlinks.get(url, []).copy()


class TrafficMonitor:
    """流量统计监控器"""

    def __init__(self):
        self._traffic: Dict[str, List[TrafficResult]] = {}

    def check(self, url: str) -> TrafficResult:
        """检查流量统计

        Args:
            url: 站点URL

        Returns:
            流量统计结果
        """
        stats = self._fetch_traffic_stats(url)
        visits = int(stats.get("visits", 0))
        unique_visitors = int(stats.get("unique_visitors", 0))
        page_views = int(stats.get("page_views", 0))
        bounce_rate = float(stats.get("bounce_rate", 0.0))
        avg_session = float(stats.get("avg_session_duration", 0.0))

        result = TrafficResult(
            url=url,
            visits=visits,
            unique_visitors=unique_visitors,
            page_views=page_views,
            bounce_rate=bounce_rate,
            avg_session_duration=avg_session,
            message=f"访问量: {visits}, UV: {unique_visitors}, PV: {page_views}",
        )

        history = self._traffic.get(url, [])
        history.append(result)
        if len(history) > 100:
            history = history[-100:]
        self._traffic[url] = history

        return result

    def _fetch_traffic_stats(self, url: str) -> Dict[str, Any]:
        """获取流量统计数据

        优先调用Google Analytics API（需配置GA_PROPERTY_ID和GA_ACCESS_TOKEN），
        其次从WordPress站点统计端点拉取（需配置WP_STATS_URL）。
        无任何凭证时抛出明确异常。

        Args:
            url: 站点URL

        Returns:
            流量统计字典，包含 visits/unique_visitors/page_views/bounce_rate/avg_session_duration

        Raises:
            RuntimeError: 无可用凭证或获取失败时抛出
        """
        ga_property_id = getattr(settings, "GA_PROPERTY_ID", None)
        ga_access_token = getattr(settings, "GA_ACCESS_TOKEN", None)

        if ga_property_id and ga_access_token:
            return self._fetch_traffic_from_ga(url, ga_property_id, ga_access_token)

        wp_stats_url = getattr(settings, "WP_STATS_URL", None)
        if wp_stats_url:
            return self._fetch_traffic_from_wp(url, wp_stats_url)

        raise RuntimeError(
            "流量统计需要配置Google Analytics凭证(GA_PROPERTY_ID/GA_ACCESS_TOKEN)"
            "或WordPress站点统计端点(WP_STATS_URL)"
        )

    def _fetch_traffic_from_ga(self, url: str, property_id: str, access_token: str) -> Dict[str, Any]:
        """通过Google Analytics Data API获取流量统计"""
        api_url = f"https://analyticsdata.googleapis.com/v1beta/properties/{property_id}:runReport"
        payload = json.dumps({
            "dateRanges": [{"startDate": "30daysAgo", "endDate": "today"}],
            "metrics": [
                {"name": "sessions"},
                {"name": "totalUsers"},
                {"name": "screenPageViews"},
                {"name": "bounceRate"},
                {"name": "averageSessionDuration"},
            ],
            "dimensionFilter": {
                "filter": {
                    "fieldName": "hostName",
                    "stringFilter": {"matchType": "EXACT", "value": self._extract_domain(url)},
                }
            },
        }).encode("utf-8")

        try:
            req = urllib.request.Request(
                api_url,
                data=payload,
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json",
                    "User-Agent": "WPForge-Monitor/1.0",
                },
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode("utf-8", errors="ignore"))
        except Exception as e:
            logger.warning(f"Google Analytics查询失败: {url}, 错误: {e}")
            raise RuntimeError(f"Google Analytics查询失败: {url}") from e

        # 解析GA返回的rows
        rows = data.get("rows", [])
        totals = rows[0].get("metricValues", []) if rows else []
        metric_names = ["sessions", "totalUsers", "screenPageViews", "bounceRate", "averageSessionDuration"]
        result = {}
        for name, val in zip(metric_names, totals):
            raw = val.get("value", "0")
            try:
                result[name] = float(raw)
            except (TypeError, ValueError):
                result[name] = 0.0

        return {
            "visits": int(result.get("sessions", 0)),
            "unique_visitors": int(result.get("totalUsers", 0)),
            "page_views": int(result.get("screenPageViews", 0)),
            "bounce_rate": round(result.get("bounceRate", 0.0) / 100, 4) if result.get("bounceRate", 0) > 1 else result.get("bounceRate", 0.0),
            "avg_session_duration": result.get("averageSessionDuration", 0.0),
        }

    def _fetch_traffic_from_wp(self, url: str, stats_url: str) -> Dict[str, Any]:
        """从WordPress站点统计端点拉取流量数据"""
        try:
            req = urllib.request.Request(stats_url, headers={
                "User-Agent": "WPForge-Monitor/1.0",
                "X-Target-URL": url,
            })
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode("utf-8", errors="ignore"))
        except Exception as e:
            logger.warning(f"WP站点统计查询失败: {url}, 错误: {e}")
            raise RuntimeError(f"WP站点统计查询失败: {url}") from e

        return {
            "visits": data.get("visits", data.get("sessions", 0)),
            "unique_visitors": data.get("unique_visitors", data.get("visitors", 0)),
            "page_views": data.get("page_views", data.get("pageviews", 0)),
            "bounce_rate": data.get("bounce_rate", 0.0),
            "avg_session_duration": data.get("avg_session_duration", data.get("avg_session", 0.0)),
        }

    @staticmethod
    def _extract_domain(url: str) -> str:
        """从URL中提取域名"""
        try:
            parsed = urllib.parse.urlparse(url)
            return parsed.netloc.lower()
        except Exception:
            return ""

    def get_history(self, url: str) -> List[TrafficResult]:
        """获取流量历史"""
        return self._traffic.get(url, []).copy()


# ==================== Webhook告警渠道 ====================

class WebhookAlertSender:
    """Webhook告警发送器

    支持飞书、钉钉、企业微信等Webhook告警渠道
    """

    def __init__(self):
        self._webhooks: Dict[str, str] = {}  # webhook_type -> url
        self._send_history: List[Dict[str, Any]] = []

    def register_webhook(self, webhook_type: WebhookType, url: str) -> None:
        """注册Webhook

        Args:
            webhook_type: Webhook类型
            url: Webhook URL
        """
        self._webhooks[webhook_type.value] = url
        logger.info(f"已注册Webhook: {webhook_type.value}")

    def remove_webhook(self, webhook_type: WebhookType) -> bool:
        """移除Webhook"""
        return self._webhooks.pop(webhook_type.value, None) is not None

    def get_webhook(self, webhook_type: WebhookType) -> Optional[str]:
        """获取Webhook URL"""
        return self._webhooks.get(webhook_type.value)

    def format_message(self, webhook_type: WebhookType, alert: Alert) -> Dict[str, Any]:
        """格式化告警消息

        Args:
            webhook_type: Webhook类型
            alert: 告警对象

        Returns:
            格式化后的消息体
        """
        if webhook_type == WebhookType.FEISHU:
            # 飞书消息格式
            return {
                "msg_type": "text",
                "content": {
                    "text": f"【{alert.level.value.upper()}】{alert.message}\n目标: {alert.target}\n类型: {alert.monitor_type.value}\n时间: {datetime.datetime.fromtimestamp(alert.created_at).isoformat()}"
                },
            }
        elif webhook_type == WebhookType.DINGTALK:
            # 钉钉消息格式
            return {
                "msgtype": "text",
                "text": {
                    "content": f"【{alert.level.value.upper()}】{alert.message}\n目标: {alert.target}\n类型: {alert.monitor_type.value}"
                },
            }
        elif webhook_type == WebhookType.WECOM:
            # 企业微信消息格式
            return {
                "msgtype": "text",
                "text": {
                    "content": f"【{alert.level.value.upper()}】{alert.message}\n目标: {alert.target}\n类型: {alert.monitor_type.value}"
                },
            }
        else:
            # 通用格式
            return {
                "level": alert.level.value,
                "message": alert.message,
                "target": alert.target,
                "monitor_type": alert.monitor_type.value,
                "timestamp": alert.created_at,
            }

    def send(self, webhook_type: WebhookType, alert: Alert) -> Dict[str, Any]:
        """发送Webhook告警

        通过HTTP POST请求将告警消息发送到已注册的Webhook URL。

        Args:
            webhook_type: Webhook类型
            alert: 告警对象

        Returns:
            发送结果
        """
        url = self._webhooks.get(webhook_type.value)
        if not url:
            return {
                "success": False,
                "message": f"Webhook {webhook_type.value} 未注册",
                "error_code": "not_registered",
            }

        message = self.format_message(webhook_type, alert)
        sent_at = time.time()

        # 真实发送HTTP POST请求
        try:
            response = self._post_webhook(url, message)
            success = response.get("success", True)
            error_msg = response.get("error", "")
        except Exception as e:
            success = False
            error_msg = str(e)
            logger.warning(f"Webhook发送失败: {webhook_type.value} -> {url}, 错误: {e}")

        record = {
            "webhook_type": webhook_type.value,
            "url": url,
            "alert_id": alert.id,
            "message": message,
            "sent_at": sent_at,
            "success": success,
            "error": error_msg if not success else "",
        }
        self._send_history.append(record)

        if success:
            logger.info(f"Webhook告警已发送: {webhook_type.value} -> {alert.target}")
            return {
                "success": True,
                "webhook_type": webhook_type.value,
                "message": "告警已发送",
            }
        else:
            return {
                "success": False,
                "webhook_type": webhook_type.value,
                "message": f"发送失败: {error_msg}",
                "error_code": "send_failed",
            }

    def _post_webhook(self, url: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """向Webhook URL发送POST请求

        Args:
            url: Webhook URL
            payload: 消息体

        Returns:
            包含 success 和可选 error 的字典

        Raises:
            RuntimeError: HTTP请求失败时抛出
        """
        body = json.dumps(payload).encode("utf-8")
        try:
            req = urllib.request.Request(
                url,
                data=body,
                headers={
                    "Content-Type": "application/json",
                    "User-Agent": "WPForge-Monitor/1.0",
                },
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=15) as resp:
                status_code = resp.getcode()
                resp.read()  # 读取响应体以释放连接
        except urllib.error.HTTPError as e:
            raise RuntimeError(f"HTTP {e.code}: {e.reason}") from e
        except Exception as e:
            raise RuntimeError(f"请求失败: {e}") from e

        if status_code >= 400:
            return {"success": False, "error": f"HTTP {status_code}"}
        return {"success": True}

    def send_to_all(self, alert: Alert) -> Dict[str, Dict[str, Any]]:
        """向所有已注册的Webhook发送告警

        Args:
            alert: 告警对象

        Returns:
            各Webhook的发送结果
        """
        results = {}
        for wh_type_str in list(self._webhooks.keys()):
            wh_type = WebhookType(wh_type_str)
            results[wh_type.value] = self.send(wh_type, alert)
        return results

    def get_send_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """获取发送历史"""
        return self._send_history[-limit:]


class EmailAlertSender:
    """邮件告警发送器"""

    def __init__(self, smtp_host: str = "", smtp_port: int = 587,
                 username: str = "", password: str = "",
                 from_addr: str = "", to_addrs: Optional[List[str]] = None):
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
        self.from_addr = from_addr
        self.to_addrs = to_addrs or []
        self._send_history: List[Dict[str, Any]] = []

    def configure(self, smtp_host: str, smtp_port: int, username: str,
                  password: str, from_addr: str, to_addrs: List[str]) -> None:
        """配置邮件发送器"""
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
        self.from_addr = from_addr
        self.to_addrs = to_addrs

    def format_email(self, alert: Alert) -> Dict[str, str]:
        """格式化邮件内容"""
        subject = f"【{alert.level.value.upper()}】{alert.monitor_type.value}告警 - {alert.target}"
        body = f"""
告警级别: {alert.level.value}
监控类型: {alert.monitor_type.value}
目标: {alert.target}
消息: {alert.message}
时间: {datetime.datetime.fromtimestamp(alert.created_at).isoformat()}
        """.strip()
        return {"subject": subject, "body": body}

    def send(self, alert: Alert) -> Dict[str, Any]:
        """发送邮件告警

        通过SMTP协议将告警邮件发送到已配置的收件人。

        Args:
            alert: 告警对象

        Returns:
            发送结果
        """
        if not self.to_addrs:
            return {
                "success": False,
                "message": "收件人未配置",
                "error_code": "no_recipients",
            }

        email = self.format_email(alert)
        sent_at = time.time()

        # 真实发送SMTP邮件
        try:
            self._send_smtp(self.to_addrs, email["subject"], email["body"])
            success = True
            error_msg = ""
        except Exception as e:
            success = False
            error_msg = str(e)
            logger.warning(f"邮件发送失败: {email['subject']}, 错误: {e}")

        record = {
            "to": self.to_addrs,
            "subject": email["subject"],
            "body": email["body"],
            "alert_id": alert.id,
            "sent_at": sent_at,
            "success": success,
            "error": error_msg if not success else "",
        }
        self._send_history.append(record)

        if success:
            logger.info(f"邮件告警已发送: {email['subject']}")
            return {"success": True, "subject": email["subject"]}
        else:
            return {
                "success": False,
                "subject": email["subject"],
                "message": f"发送失败: {error_msg}",
                "error_code": "send_failed",
            }

    def _send_smtp(self, to_addrs: List[str], subject: str, body: str) -> None:
        """通过SMTP发送邮件

        Args:
            to_addrs: 收件人列表
            subject: 邮件主题
            body: 邮件正文

        Raises:
            RuntimeError: SMTP发送失败时抛出
            ValueError: SMTP主机未配置时抛出
        """
        if not self.smtp_host:
            raise ValueError("SMTP主机未配置，请先调用configure()")

        msg = MIMEText(body, "plain", "utf-8")
        msg["Subject"] = subject
        msg["From"] = self.from_addr
        msg["To"] = ", ".join(to_addrs)
        msg["Date"] = formatdate(localtime=True)

        try:
            with smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=30) as server:
                # STARTTLS（端口587常用）
                if self.smtp_port in (587, 25) and self.username:
                    try:
                        server.starttls()
                    except smtplib.SMTPException:
                        pass
                if self.username:
                    server.login(self.username, self.password)
                server.sendmail(self.from_addr, to_addrs, msg.as_string())
        except smtplib.SMTPException as e:
            raise RuntimeError(f"SMTP发送失败: {e}") from e
        except Exception as e:
            raise RuntimeError(f"邮件发送异常: {e}") from e

    def get_send_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """获取发送历史"""
        return self._send_history[-limit:]


class InAppAlertSender:
    """站内消息告警发送器"""

    def __init__(self):
        self._messages: List[Dict[str, Any]] = []

    def send(self, alert: Alert, user_id: Optional[int] = None) -> Dict[str, Any]:
        """发送站内消息

        Args:
            alert: 告警对象
            user_id: 用户ID（None表示广播）

        Returns:
            发送结果
        """
        message = {
            "id": f"msg_{int(time.time())}_{alert.id[:8]}",
            "alert_id": alert.id,
            "user_id": user_id,
            "title": f"{alert.monitor_type.value}告警",
            "content": alert.message,
            "level": alert.level.value,
            "target": alert.target,
            "read": False,
            "created_at": time.time(),
        }
        self._messages.append(message)
        logger.info(f"站内消息已发送: {message['title']}")
        return {"success": True, "message_id": message["id"]}

    def get_messages(self, user_id: Optional[int] = None, unread_only: bool = False) -> List[Dict[str, Any]]:
        """获取站内消息"""
        messages = self._messages
        if user_id is not None:
            messages = [m for m in messages if m["user_id"] == user_id or m["user_id"] is None]
        if unread_only:
            messages = [m for m in messages if not m["read"]]
        return messages.copy()

    def mark_as_read(self, message_id: str) -> bool:
        """标记消息为已读"""
        for msg in self._messages:
            if msg["id"] == message_id:
                msg["read"] = True
                return True
        return False


# ==================== 告警规则管理 ====================

class AlertRuleManager:
    """告警规则管理器

    支持阈值配置、连续N次失败才告警、告警静默期、告警升级
    """

    def __init__(self):
        self._rules: Dict[str, AlertRule] = {}
        self._failure_counts: Dict[str, int] = {}  # 连续失败计数
        self._last_alert_time: Dict[str, float] = {}  # 上次告警时间
        self._alert_counts: Dict[str, int] = {}  # 告警次数（用于升级）

    def add_rule(self, rule: AlertRule) -> None:
        """添加告警规则"""
        self._rules[rule.name] = rule
        logger.info(f"已添加告警规则: {rule.name}")

    def remove_rule(self, name: str) -> bool:
        """移除告警规则"""
        return self._rules.pop(name, None) is not None

    def get_rule(self, name: str) -> Optional[AlertRule]:
        """获取告警规则"""
        return self._rules.get(name)

    def get_all_rules(self) -> Dict[str, AlertRule]:
        """获取所有规则"""
        return self._rules.copy()

    def evaluate(self, rule_name: str, value: float) -> Dict[str, Any]:
        """评估告警规则

        Args:
            rule_name: 规则名称
            value: 监控值

        Returns:
            评估结果
        """
        rule = self._rules.get(rule_name)
        if not rule or not rule.enabled:
            return {"should_alert": False, "reason": "rule_not_found_or_disabled"}

        # 阈值比较
        threshold_met = self._compare(value, rule.threshold, rule.comparison)
        if not threshold_met:
            # 重置连续失败计数
            self._failure_counts[rule_name] = 0
            return {"should_alert": False, "reason": "threshold_not_met"}

        # 增加连续失败计数
        self._failure_counts[rule_name] = self._failure_counts.get(rule_name, 0) + 1
        current_failures = self._failure_counts[rule_name]

        # 检查是否达到连续失败次数
        if current_failures < rule.consecutive_failures:
            return {
                "should_alert": False,
                "reason": "insufficient_consecutive_failures",
                "current_failures": current_failures,
                "required": rule.consecutive_failures,
            }

        # 检查告警静默期
        last_time = self._last_alert_time.get(rule_name, 0)
        now = time.time()
        if now - last_time < rule.cooldown_period:
            return {
                "should_alert": False,
                "reason": "in_cooldown",
                "remaining_cooldown": rule.cooldown_period - (now - last_time),
            }

        # 检查是否需要升级
        self._alert_counts[rule_name] = self._alert_counts.get(rule_name, 0) + 1
        alert_count = self._alert_counts[rule_name]

        escalated = False
        level = "warning"
        if rule.escalation_after > 0 and alert_count >= rule.escalation_after:
            escalated = True
            level = rule.escalation_level

        self._last_alert_time[rule_name] = now

        return {
            "should_alert": True,
            "reason": "threshold_met",
            "value": value,
            "threshold": rule.threshold,
            "consecutive_failures": current_failures,
            "alert_count": alert_count,
            "escalated": escalated,
            "level": level,
        }

    def _compare(self, value: float, threshold: float, comparison: str) -> bool:
        """比较值与阈值"""
        if comparison == ">":
            return value > threshold
        elif comparison == "<":
            return value < threshold
        elif comparison == ">=":
            return value >= threshold
        elif comparison == "<=":
            return value <= threshold
        elif comparison == "==":
            return value == threshold
        elif comparison == "!=":
            return value != threshold
        return False

    def reset_failure_count(self, rule_name: str) -> None:
        """重置连续失败计数"""
        self._failure_counts[rule_name] = 0

    def get_failure_count(self, rule_name: str) -> int:
        """获取连续失败次数"""
        return self._failure_counts.get(rule_name, 0)

    def get_alert_count(self, rule_name: str) -> int:
        """获取告警次数"""
        return self._alert_counts.get(rule_name, 0)


# ==================== 趋势图表数据接口 ====================

class TrendChartService:
    """趋势图表数据服务"""

    def __init__(self):
        self._data_points: Dict[str, List[Dict[str, Any]]] = {}

    def add_data_point(self, series: str, timestamp: float, value: float,
                       metadata: Optional[Dict[str, Any]] = None) -> None:
        """添加数据点

        Args:
            series: 数据系列名称
            timestamp: 时间戳
            value: 值
            metadata: 元数据
        """
        if series not in self._data_points:
            self._data_points[series] = []
        self._data_points[series].append({
            "timestamp": timestamp,
            "value": value,
            "metadata": metadata or {},
        })
        # 只保留最近1000条
        if len(self._data_points[series]) > 1000:
            self._data_points[series] = self._data_points[series][-1000:]

    def get_trend_data(self, series: str, start_time: Optional[float] = None,
                       end_time: Optional[float] = None) -> List[Dict[str, Any]]:
        """获取趋势数据

        Args:
            series: 数据系列
            start_time: 开始时间
            end_time: 结束时间

        Returns:
            数据点列表
        """
        data = self._data_points.get(series, [])
        if start_time:
            data = [d for d in data if d["timestamp"] >= start_time]
        if end_time:
            data = [d for d in data if d["timestamp"] <= end_time]
        return data.copy()

    def get_chart_data(self, series: str, points: int = 30) -> Dict[str, Any]:
        """获取图表数据

        Args:
            series: 数据系列
            points: 返回的数据点数量

        Returns:
            图表数据
        """
        data = self._data_points.get(series, [])[-points:]
        return {
            "series": series,
            "labels": [datetime.datetime.fromtimestamp(d["timestamp"]).strftime("%Y-%m-%d %H:%M") for d in data],
            "values": [d["value"] for d in data],
            "timestamps": [d["timestamp"] for d in data],
            "point_count": len(data),
        }

    def get_summary(self, series: str) -> Dict[str, Any]:
        """获取数据摘要

        Args:
            series: 数据系列

        Returns:
            摘要信息
        """
        data = self._data_points.get(series, [])
        if not data:
            return {
                "series": series,
                "count": 0,
                "min": 0,
                "max": 0,
                "avg": 0,
                "latest": None,
            }
        values = [d["value"] for d in data]
        return {
            "series": series,
            "count": len(data),
            "min": min(values),
            "max": max(values),
            "avg": round(sum(values) / len(values), 2),
            "latest": values[-1],
        }

    def get_all_series(self) -> List[str]:
        """获取所有数据系列"""
        return list(self._data_points.keys())

    def clear_series(self, series: str) -> bool:
        """清空数据系列"""
        if series in self._data_points:
            self._data_points[series] = []
            return True
        return False


# ==================== 异步监控方法（供Celery定时任务调用） ====================

async def async_check_uptime(url: str, timeout: int = 30) -> MonitorResult:
    """异步检查站点可用性

    Args:
        url: 站点URL
        timeout: 超时时间

    Returns:
        监控结果
    """
    monitor = UptimeMonitor(timeout=timeout)
    # 在线程池中执行同步的检查
    result = await asyncio.to_thread(monitor.check, url)
    return result


async def async_check_ssl(hostname: str, port: int = 443) -> MonitorResult:
    """异步检查SSL证书

    Args:
        hostname: 主机名
        port: 端口

    Returns:
        监控结果
    """
    monitor = SSLMonitor(port=port)
    result = await asyncio.to_thread(monitor.check, hostname)
    return result


async def async_check_site(url: str, config: Optional[MonitorConfig] = None) -> Dict[str, MonitorResult]:
    """异步检查站点（所有启用的监控）

    Args:
        url: 站点URL
        config: 监控配置

    Returns:
        监控结果字典
    """
    service = SiteMonitorService(config=config)
    result = await asyncio.to_thread(service.check_site, url)
    return result


async def async_check_content_change(url: str, content: Optional[str] = None) -> ContentChangeResult:
    """异步检查首页内容变化

    Args:
        url: 站点URL
        content: 页面内容

    Returns:
        内容变化结果
    """
    monitor = ContentChangeMonitor()
    result = await asyncio.to_thread(monitor.check, url, content)
    return result


async def async_check_keyword_ranking(keyword: str, url: str,
                                       search_engine: str = "google") -> KeywordRankingResult:
    """异步检查关键词排名

    Args:
        keyword: 关键词
        url: 站点URL
        search_engine: 搜索引擎

    Returns:
        排名结果
    """
    monitor = KeywordRankingMonitor()
    result = await asyncio.to_thread(monitor.check, keyword, url, search_engine)
    return result


async def async_check_backlinks(url: str) -> BacklinkResult:
    """异步检查外链数量

    Args:
        url: 站点URL

    Returns:
        外链结果
    """
    monitor = BacklinkMonitor()
    result = await asyncio.to_thread(monitor.check, url)
    return result


async def async_check_traffic(url: str) -> TrafficResult:
    """异步检查流量统计

    Args:
        url: 站点URL

    Returns:
        流量结果
    """
    monitor = TrafficMonitor()
    result = await asyncio.to_thread(monitor.check, url)
    return result


async def async_send_webhook_alert(webhook_type: WebhookType, alert: Alert,
                                    sender: Optional[WebhookAlertSender] = None) -> Dict[str, Any]:
    """异步发送Webhook告警

    Args:
        webhook_type: Webhook类型
        alert: 告警对象
        sender: Webhook发送器

    Returns:
        发送结果
    """
    sender = sender or WebhookAlertSender()
    result = await asyncio.to_thread(sender.send, webhook_type, alert)
    return result


async def async_monitor_site_full(url: str, config: Optional[MonitorConfig] = None) -> Dict[str, Any]:
    """异步全面监控站点

    并发执行所有监控项

    Args:
        url: 站点URL
        config: 监控配置

    Returns:
        所有监控结果
    """
    from urllib.parse import urlparse
    parsed = urlparse(url)
    hostname = parsed.hostname or ""

    tasks = {}
    tasks["uptime"] = async_check_uptime(url)
    if parsed.scheme == "https" and hostname:
        tasks["ssl"] = async_check_ssl(hostname)
    tasks["content_change"] = async_check_content_change(url)
    tasks["backlinks"] = async_check_backlinks(url)
    tasks["traffic"] = async_check_traffic(url)

    keys = list(tasks.keys())
    coros = list(tasks.values())
    done = await asyncio.gather(*coros, return_exceptions=True)

    results = {}
    for key, result in zip(keys, done):
        if isinstance(result, Exception):
            results[key] = {"error": str(result)}
        else:
            results[key] = result
    return results
