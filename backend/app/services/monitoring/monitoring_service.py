"""
站点监控与告警服务
包含可用性监控、SSL监控、域名监控、收录监控、排名监控等
"""
from typing import List, Dict, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
import time
import re
import ssl
import socket
import asyncio
from datetime import datetime, timedelta
from urllib.parse import urlparse
import http.client
import json


class MonitorType(str, Enum):
    """监控类型枚举"""
    AVAILABILITY = "availability"
    SSL = "ssl"
    DOMAIN = "domain"
    DISK = "disk"
    INDEXING = "indexing"
    RANKING = "ranking"
    RESPONSE_TIME = "response_time"


class AlertLevel(str, Enum):
    """告警级别"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class AlertChannel(str, Enum):
    """告警渠道"""
    EMAIL = "email"
    WEBHOOK = "webhook"
    IN_APP = "in_app"
    SLACK = "slack"
    TELEGRAM = "telegram"


@dataclass
class MonitorResult:
    """监控结果"""
    monitor_type: MonitorType
    site_id: str
    status: str  # ok, warning, critical, error
    value: Optional[float] = None
    message: str = ""
    checked_at: float = field(default_factory=time.time)
    details: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "monitor_type": self.monitor_type.value,
            "site_id": self.site_id,
            "status": self.status,
            "value": self.value,
            "message": self.message,
            "checked_at": self.checked_at,
            "details": self.details,
        }


@dataclass
class Alert:
    """告警"""
    id: str
    site_id: str
    monitor_type: MonitorType
    level: AlertLevel
    title: str
    message: str
    created_at: float = field(default_factory=time.time)
    resolved: bool = False
    resolved_at: Optional[float] = None
    channels: List[AlertChannel] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "site_id": self.site_id,
            "monitor_type": self.monitor_type.value,
            "level": self.level.value,
            "title": self.title,
            "message": self.message,
            "created_at": self.created_at,
            "resolved": self.resolved,
            "resolved_at": self.resolved_at,
            "channels": [c.value for c in self.channels],
        }


@dataclass
class MonitorConfig:
    """监控配置"""
    # 可用性监控
    availability_enabled: bool = True
    availability_interval: int = 300  # 5分钟
    availability_timeout: int = 30
    availability_warning_threshold: int = 500  # ms
    availability_critical_threshold: int = 2000  # ms

    # SSL监控
    ssl_enabled: bool = True
    ssl_interval: int = 86400  # 24小时
    ssl_warning_days: int = 30
    ssl_critical_days: int = 7

    # 域名监控
    domain_enabled: bool = True
    domain_interval: int = 86400  # 24小时
    domain_warning_days: int = 60
    domain_critical_days: int = 30

    # 磁盘监控
    disk_enabled: bool = False
    disk_interval: int = 3600  # 1小时
    disk_warning_percent: int = 80
    disk_critical_percent: int = 90

    # 收录监控
    indexing_enabled: bool = False
    indexing_interval: int = 86400  # 24小时

    # 排名监控
    ranking_enabled: bool = False
    ranking_interval: int = 86400  # 24小时

    # 告警设置
    alert_enabled: bool = True
    alert_channels: List[AlertChannel] = field(default_factory=lambda: [AlertChannel.IN_APP])
    alert_cooldown: int = 3600  # 同一告警冷却时间（秒）

    def to_dict(self) -> Dict[str, Any]:
        return {
            "availability_enabled": self.availability_enabled,
            "availability_interval": self.availability_interval,
            "availability_timeout": self.availability_timeout,
            "availability_warning_threshold": self.availability_warning_threshold,
            "availability_critical_threshold": self.availability_critical_threshold,
            "ssl_enabled": self.ssl_enabled,
            "ssl_interval": self.ssl_interval,
            "ssl_warning_days": self.ssl_warning_days,
            "ssl_critical_days": self.ssl_critical_days,
            "domain_enabled": self.domain_enabled,
            "domain_interval": self.domain_interval,
            "domain_warning_days": self.domain_warning_days,
            "domain_critical_days": self.domain_critical_days,
            "disk_enabled": self.disk_enabled,
            "disk_interval": self.disk_interval,
            "disk_warning_percent": self.disk_warning_percent,
            "disk_critical_percent": self.disk_critical_percent,
            "indexing_enabled": self.indexing_enabled,
            "indexing_interval": self.indexing_interval,
            "ranking_enabled": self.ranking_enabled,
            "ranking_interval": self.ranking_interval,
            "alert_enabled": self.alert_enabled,
            "alert_channels": [c.value for c in self.alert_channels],
            "alert_cooldown": self.alert_cooldown,
        }


class MonitoringService:
    """
    站点监控与告警服务
    """

    def __init__(self, config: Optional[MonitorConfig] = None):
        self.config = config or MonitorConfig()
        self._monitor_results: Dict[str, List[MonitorResult]] = {}
        self._alerts: List[Alert] = []
        self._last_alert_time: Dict[str, float] = {}
        self._alert_handlers: Dict[AlertChannel, Callable] = {}

    # ==================== 可用性监控 ====================

    def check_availability(self, url: str, site_id: str = "") -> MonitorResult:
        """
        检查站点可用性

        Args:
            url: 站点URL
            site_id: 站点ID

        Returns:
            监控结果
        """
        result = MonitorResult(
            monitor_type=MonitorType.AVAILABILITY,
            site_id=site_id,
            status="error",
            message="",
        )

        try:
            parsed = urlparse(url)
            host = parsed.hostname
            path = parsed.path or "/"
            port = parsed.port or (443 if parsed.scheme == "https" else 80)

            start_time = time.time()

            if parsed.scheme == "https":
                conn = http.client.HTTPSConnection(
                    host, port, timeout=self.config.availability_timeout
                )
            else:
                conn = http.client.HTTPConnection(
                    host, port, timeout=self.config.availability_timeout
                )

            conn.request("GET", path, headers={
                "User-Agent": "WPForge Monitor/1.0",
                "Accept": "text/html,application/xhtml+xml",
            })

            response = conn.getresponse()
            response_time = (time.time() - start_time) * 1000  # 转换为ms

            result.value = response_time
            result.details = {
                "status_code": response.status,
                "response_time_ms": response_time,
            }

            if response.status >= 200 and response.status < 400:
                if response_time <= self.config.availability_warning_threshold:
                    result.status = "ok"
                    result.message = f"Site is up. Response time: {response_time:.0f}ms"
                elif response_time <= self.config.availability_critical_threshold:
                    result.status = "warning"
                    result.message = f"Site is slow. Response time: {response_time:.0f}ms"
                else:
                    result.status = "critical"
                    result.message = f"Site is very slow. Response time: {response_time:.0f}ms"
            else:
                result.status = "critical"
                result.message = f"Site returned HTTP {response.status}"

            conn.close()

        except socket.timeout:
            result.status = "critical"
            result.message = "Connection timeout"
        except ssl.SSLError as e:
            result.status = "critical"
            result.message = f"SSL error: {str(e)}"
        except Exception as e:
            result.status = "error"
            result.message = f"Error checking availability: {str(e)}"

        # 记录结果
        self._record_result(site_id, result)

        # 检查是否需要告警
        if result.status in ["warning", "critical", "error"]:
            self._check_and_send_alert(result)

        return result

    # ==================== SSL证书监控 ====================

    def check_ssl_certificate(self, url: str, site_id: str = "") -> MonitorResult:
        """
        检查SSL证书

        Args:
            url: 站点URL
            site_id: 站点ID

        Returns:
            监控结果
        """
        result = MonitorResult(
            monitor_type=MonitorType.SSL,
            site_id=site_id,
            status="error",
            message="",
        )

        try:
            parsed = urlparse(url)
            host = parsed.hostname
            port = parsed.port or 443

            ctx = ssl.create_default_context()
            with ctx.wrap_socket(socket.socket(), server_hostname=host) as s:
                s.settimeout(10)
                s.connect((host, port))
                cert = s.getpeercert()

            # 解析证书信息
            not_after_str = cert.get("notAfter", "")
            if not_after_str:
                # 解析日期格式："Sep 15 12:00:00 2025 GMT"
                not_after = datetime.strptime(not_after_str, "%b %d %H:%M:%S %Y %Z")
                days_remaining = (not_after - datetime.utcnow()).days

                result.value = days_remaining
                result.details = {
                    "issuer": dict(x[0] for x in cert.get("issuer", [])),
                    "subject": dict(x[0] for x in cert.get("subject", [])),
                    "not_before": cert.get("notBefore", ""),
                    "not_after": not_after_str,
                    "days_remaining": days_remaining,
                }

                if days_remaining > self.config.ssl_warning_days:
                    result.status = "ok"
                    result.message = f"SSL certificate is valid. {days_remaining} days remaining."
                elif days_remaining > self.config.ssl_critical_days:
                    result.status = "warning"
                    result.message = f"SSL certificate expires in {days_remaining} days."
                else:
                    result.status = "critical"
                    result.message = f"SSL certificate expires in {days_remaining} days! Renew immediately!"
            else:
                result.status = "error"
                result.message = "Could not parse certificate expiry date"

        except ssl.SSLCertVerificationError as e:
            result.status = "critical"
            result.message = f"SSL certificate verification failed: {str(e)}"
        except socket.timeout:
            result.status = "error"
            result.message = "Connection timeout"
        except Exception as e:
            result.status = "error"
            result.message = f"Error checking SSL: {str(e)}"

        # 记录结果
        self._record_result(site_id, result)

        # 检查是否需要告警
        if result.status in ["warning", "critical", "error"]:
            self._check_and_send_alert(result)

        return result

    # ==================== 域名到期监控 ====================

    def check_domain_expiry(self, domain: str, site_id: str = "") -> MonitorResult:
        """
        检查域名到期时间

        Args:
            domain: 域名
            site_id: 站点ID

        Returns:
            监控结果
        """
        result = MonitorResult(
            monitor_type=MonitorType.DOMAIN,
            site_id=site_id,
            status="error",
            message="",
        )

        try:
            # 使用 python-whois 库查询真实域名到期时间
            import whois

            w = whois.whois(domain)
            expiry_date = w.expiration_date

            # 处理返回的日期可能是列表或单个值的情况
            if isinstance(expiry_date, list):
                expiry_date = expiry_date[0]

            if not expiry_date:
                result.status = "error"
                result.message = f"无法获取域名 {domain} 的到期时间"
                self._record_result(site_id, result)
                if result.status in ["warning", "critical", "error"]:
                    self._check_and_send_alert(result)
                return result

            # 计算剩余天数
            if isinstance(expiry_date, str):
                expiry_date = datetime.strptime(expiry_date, "%Y-%m-%d")
            elif hasattr(expiry_date, 'date'):
                expiry_date = expiry_date.date() if hasattr(expiry_date, 'date') else expiry_date

            now = datetime.now()
            if hasattr(expiry_date, 'year') and hasattr(expiry_date, 'month'):
                # 处理 date 或 datetime 对象
                if not hasattr(expiry_date, 'hour'):
                    expiry_date = datetime(expiry_date.year, expiry_date.month, expiry_date.day)

            days_remaining = (expiry_date - now).days

            registrar = w.registrar if w.registrar else "Unknown"

            result.value = days_remaining
            result.details = {
                "domain": domain,
                "days_remaining": days_remaining,
                "registrar": registrar,
                "expiry_date": expiry_date.strftime("%Y-%m-%d") if hasattr(expiry_date, 'strftime') else str(expiry_date),
            }

            if days_remaining > self.config.domain_warning_days:
                result.status = "ok"
                result.message = f"Domain is valid. {days_remaining} days remaining."
            elif days_remaining > self.config.domain_critical_days:
                result.status = "warning"
                result.message = f"Domain expires in {days_remaining} days."
            else:
                result.status = "critical"
                result.message = f"Domain expires in {days_remaining} days! Renew immediately!"

        except ImportError:
            result.status = "error"
            result.message = "python-whois 库未安装，无法查询域名到期时间。请运行: pip install python-whois"
        except Exception as e:
            result.status = "error"
            result.message = f"Error checking domain: {str(e)}"

        # 记录结果
        self._record_result(site_id, result)

        # 检查是否需要告警
        if result.status in ["warning", "critical", "error"]:
            self._check_and_send_alert(result)

        return result

    # ==================== 响应时间监控 ====================

    def check_response_time(self, url: str, site_id: str = "", num_checks: int = 3) -> MonitorResult:
        """
        检查响应时间（多次检查取平均）

        Args:
            url: 站点URL
            site_id: 站点ID
            num_checks: 检查次数

        Returns:
            监控结果
        """
        result = MonitorResult(
            monitor_type=MonitorType.RESPONSE_TIME,
            site_id=site_id,
            status="error",
            message="",
        )

        try:
            response_times = []
            status_codes = []

            for i in range(num_checks):
                avail_result = self.check_availability(url, site_id)
                if avail_result.value:
                    response_times.append(avail_result.value)
                    status_codes.append(avail_result.details.get("status_code", 0))
                time.sleep(1)  # 间隔1秒

            if response_times:
                avg_time = sum(response_times) / len(response_times)
                min_time = min(response_times)
                max_time = max(response_times)

                result.value = avg_time
                result.details = {
                    "avg_response_time_ms": avg_time,
                    "min_response_time_ms": min_time,
                    "max_response_time_ms": max_time,
                    "checks_count": len(response_times),
                    "status_codes": status_codes,
                }

                if avg_time <= self.config.availability_warning_threshold:
                    result.status = "ok"
                    result.message = f"Average response time: {avg_time:.0f}ms"
                elif avg_time <= self.config.availability_critical_threshold:
                    result.status = "warning"
                    result.message = f"Slow response time: {avg_time:.0f}ms"
                else:
                    result.status = "critical"
                    result.message = f"Very slow response time: {avg_time:.0f}ms"
            else:
                result.status = "error"
                result.message = "Failed to get response times"

        except Exception as e:
            result.status = "error"
            result.message = f"Error checking response time: {str(e)}"

        # 记录结果
        self._record_result(site_id, result)

        return result

    # ==================== 批量监控 ====================

    def check_all_monitors(self, site_url: str, site_id: str = "") -> List[MonitorResult]:
        """
        执行所有启用的监控检查

        Args:
            site_url: 站点URL
            site_id: 站点ID

        Returns:
            监控结果列表
        """
        results = []
        parsed = urlparse(site_url)
        domain = parsed.hostname or ""

        # 可用性监控
        if self.config.availability_enabled:
            result = self.check_availability(site_url, site_id)
            results.append(result)

        # SSL监控
        if self.config.ssl_enabled and parsed.scheme == "https":
            result = self.check_ssl_certificate(site_url, site_id)
            results.append(result)

        # 域名监控
        if self.config.domain_enabled and domain:
            result = self.check_domain_expiry(domain, site_id)
            results.append(result)

        return results

    # ==================== 告警管理 ====================

    def _check_and_send_alert(self, result: MonitorResult):
        """检查并发送告警"""
        if not self.config.alert_enabled:
            return

        # 生成告警唯一键
        alert_key = f"{result.site_id}_{result.monitor_type.value}_{result.status}"

        # 检查冷却时间
        last_time = self._last_alert_time.get(alert_key, 0)
        if time.time() - last_time < self.config.alert_cooldown:
            return  # 在冷却期内，不重复告警

        # 确定告警级别
        if result.status == "critical":
            level = AlertLevel.CRITICAL
        elif result.status == "warning":
            level = AlertLevel.WARNING
        else:
            level = AlertLevel.INFO

        # 创建告警
        alert = Alert(
            id=f"alert_{int(time.time())}_{result.site_id}",
            site_id=result.site_id,
            monitor_type=result.monitor_type,
            level=level,
            title=f"{result.monitor_type.value.capitalize()} {result.status.capitalize()}",
            message=result.message,
            channels=self.config.alert_channels.copy(),
        )

        # 保存告警
        self._alerts.append(alert)
        self._last_alert_time[alert_key] = time.time()

        # 发送告警
        self._send_alert(alert)

    def _send_alert(self, alert: Alert):
        """发送告警"""
        for channel in alert.channels:
            handler = self._alert_handlers.get(channel)
            if handler:
                try:
                    handler(alert)
                except Exception as e:
                    print(f"Error sending alert to {channel.value}: {e}")

    def register_alert_handler(self, channel: AlertChannel, handler: Callable):
        """注册告警处理器"""
        self._alert_handlers[channel] = handler

    def get_alerts(self, site_id: Optional[str] = None, 
                   level: Optional[AlertLevel] = None,
                   unresolved_only: bool = True) -> List[Alert]:
        """
        获取告警列表

        Args:
            site_id: 站点ID过滤
            level: 级别过滤
            unresolved_only: 只显示未解决的

        Returns:
            告警列表
        """
        alerts = self._alerts.copy()

        if site_id:
            alerts = [a for a in alerts if a.site_id == site_id]

        if level:
            alerts = [a for a in alerts if a.level == level]

        if unresolved_only:
            alerts = [a for a in alerts if not a.resolved]

        # 按时间倒序
        alerts.sort(key=lambda a: a.created_at, reverse=True)

        return alerts

    def resolve_alert(self, alert_id: str) -> bool:
        """
        标记告警为已解决

        Args:
            alert_id: 告警ID

        Returns:
            是否成功
        """
        for alert in self._alerts:
            if alert.id == alert_id:
                alert.resolved = True
                alert.resolved_at = time.time()
                return True
        return False

    # ==================== 监控结果管理 ====================

    def _record_result(self, site_id: str, result: MonitorResult):
        """记录监控结果"""
        if site_id not in self._monitor_results:
            self._monitor_results[site_id] = []

        self._monitor_results[site_id].append(result)

        # 只保留最近100条记录
        if len(self._monitor_results[site_id]) > 100:
            self._monitor_results[site_id] = self._monitor_results[site_id][-100:]

    def get_monitor_history(self, site_id: str, 
                            monitor_type: Optional[MonitorType] = None,
                            limit: int = 50) -> List[MonitorResult]:
        """
        获取监控历史

        Args:
            site_id: 站点ID
            monitor_type: 监控类型过滤
            limit: 数量限制

        Returns:
            监控结果列表
        """
        results = self._monitor_results.get(site_id, []).copy()

        if monitor_type:
            results = [r for r in results if r.monitor_type == monitor_type]

        results.sort(key=lambda r: r.checked_at, reverse=True)
        return results[:limit]

    def get_monitor_summary(self, site_id: str) -> Dict[str, Any]:
        """
        获取监控摘要

        Args:
            site_id: 站点ID

        Returns:
            摘要信息
        """
        results = self._monitor_results.get(site_id, [])

        if not results:
            return {
                "site_id": site_id,
                "overall_status": "unknown",
                "last_check": None,
                "checks_count": 0,
                "ok_count": 0,
                "warning_count": 0,
                "critical_count": 0,
                "error_count": 0,
            }

        # 按类型分组获取最新结果
        latest_by_type = {}
        for result in results:
            mt = result.monitor_type.value
            if mt not in latest_by_type or result.checked_at > latest_by_type[mt].checked_at:
                latest_by_type[mt] = result

        # 统计
        status_counts = {"ok": 0, "warning": 0, "critical": 0, "error": 0}
        for result in results:
            status_counts[result.status] = status_counts.get(result.status, 0) + 1

        # 总体状态
        overall = "ok"
        for result in latest_by_type.values():
            if result.status == "critical":
                overall = "critical"
                break
            elif result.status == "error":
                if overall != "critical":
                    overall = "error"
            elif result.status == "warning":
                if overall not in ["critical", "error"]:
                    overall = "warning"

        last_check = max(r.checked_at for r in results) if results else None

        return {
            "site_id": site_id,
            "overall_status": overall,
            "last_check": last_check,
            "checks_count": len(results),
            "ok_count": status_counts.get("ok", 0),
            "warning_count": status_counts.get("warning", 0),
            "critical_count": status_counts.get("critical", 0),
            "error_count": status_counts.get("error", 0),
            "latest_by_type": {k: v.to_dict() for k, v in latest_by_type.items()},
        }

    # ==================== 配置管理 ====================

    def set_config(self, config: MonitorConfig):
        """设置配置"""
        self.config = config

    def get_config(self) -> MonitorConfig:
        """获取配置"""
        return self.config

    # ==================== 统计信息 ====================

    def get_uptime_stats(self, site_id: str, days: int = 30) -> Dict[str, Any]:
        """
        获取正常运行时间统计

        Args:
            site_id: 站点ID
            days: 统计天数

        Returns:
            统计信息
        """
        results = self._monitor_results.get(site_id, [])

        # 过滤可用性监控结果
        avail_results = [r for r in results if r.monitor_type == MonitorType.AVAILABILITY]

        if not avail_results:
            return {
                "uptime_percent": 100.0,
                "total_checks": 0,
                "successful_checks": 0,
                "failed_checks": 0,
                "avg_response_time_ms": 0,
            }

        total = len(avail_results)
        successful = sum(1 for r in avail_results if r.status == "ok")
        failed = total - successful

        response_times = [r.value for r in avail_results if r.value]
        avg_time = sum(response_times) / len(response_times) if response_times else 0

        uptime_percent = (successful / total * 100) if total > 0 else 100

        return {
            "uptime_percent": round(uptime_percent, 2),
            "total_checks": total,
            "successful_checks": successful,
            "failed_checks": failed,
            "avg_response_time_ms": round(avg_time, 2),
        }


# 单例实例
_monitoring_service = None


def get_monitoring_service() -> MonitoringService:
    """获取监控服务单例"""
    global _monitoring_service
    if _monitoring_service is None:
        _monitoring_service = MonitoringService()
    return _monitoring_service
