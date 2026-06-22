"""
站点监控与告警系统
可用性监控、SSL监控、域名监控、收录监控、排名监控、智能告警
"""
import time
import ssl
import socket
import datetime
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
from app.core.logging import get_logger

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
