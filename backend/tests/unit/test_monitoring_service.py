"""
监控服务测试
"""
import time
import socket
import asyncio
import datetime
import urllib.error
from unittest.mock import patch, MagicMock

import pytest

from app.services.monitoring_service import (
    MonitorType,
    AlertLevel,
    AlertStatus,
    MonitorResult,
    Alert,
    MonitorConfig,
    UptimeMonitor,
    SSLMonitor,
    DiskMonitor,
    PerformanceMonitor,
    AlertManager,
    SiteMonitorService,
    site_monitor_service,
    ExtendedMonitorType,
    WebhookType,
    ContentChangeResult,
    KeywordRankingResult,
    BacklinkResult,
    TrafficResult,
    AlertRule,
    ContentChangeMonitor,
    KeywordRankingMonitor,
    BacklinkMonitor,
    TrafficMonitor,
    WebhookAlertSender,
    EmailAlertSender,
    InAppAlertSender,
    AlertRuleManager,
    TrendChartService,
    async_check_uptime,
    async_check_ssl,
    async_check_site,
    async_check_content_change,
    async_check_keyword_ranking,
    async_check_backlinks,
    async_check_traffic,
    async_send_webhook_alert,
    async_monitor_site_full,
)


# ---------------------------------------------------------------------------
# 枚举
# ---------------------------------------------------------------------------
class TestMonitorEnums:
    """监控相关枚举测试"""

    def test_monitor_type_values(self):
        assert MonitorType.UPTIME.value == "uptime"
        assert MonitorType.SSL.value == "ssl"
        assert MonitorType.DOMAIN.value == "domain"
        assert MonitorType.DISK.value == "disk"
        assert MonitorType.INDEXING.value == "indexing"
        assert MonitorType.RANKING.value == "ranking"
        assert MonitorType.PERFORMANCE.value == "performance"
        assert MonitorType.SEO.value == "seo"

    def test_alert_level_values(self):
        assert AlertLevel.INFO.value == "info"
        assert AlertLevel.WARNING.value == "warning"
        assert AlertLevel.ERROR.value == "error"
        assert AlertLevel.CRITICAL.value == "critical"

    def test_alert_status_values(self):
        assert AlertStatus.NEW.value == "new"
        assert AlertStatus.ACKNOWLEDGED.value == "acknowledged"
        assert AlertStatus.RESOLVED.value == "resolved"
        assert AlertStatus.IGNORED.value == "ignored"

    def test_monitor_type_is_str_enum(self):
        assert isinstance(MonitorType.UPTIME, str)

    def test_alert_level_is_str_enum(self):
        assert isinstance(AlertLevel.CRITICAL, str)


# ---------------------------------------------------------------------------
# 数据类
# ---------------------------------------------------------------------------
class TestDataclasses:
    """数据类测试"""

    def test_monitor_result_defaults(self):
        result = MonitorResult(
            monitor_type=MonitorType.UPTIME,
            target="https://example.com",
            status="ok",
        )
        assert result.value is None
        assert result.message == ""
        assert result.timestamp > 0
        assert result.metadata == {}
        assert result.duration == 0.0

    def test_monitor_result_full(self):
        result = MonitorResult(
            monitor_type=MonitorType.SSL,
            target="example.com",
            status="warning",
            value=15.0,
            message="expiring soon",
            metadata={"days": 15},
            duration=42.5,
        )
        assert result.value == 15.0
        assert result.message == "expiring soon"
        assert result.metadata == {"days": 15}
        assert result.duration == 42.5

    def test_monitor_result_metadata_independent(self):
        r1 = MonitorResult(monitor_type=MonitorType.DISK, target="/", status="ok")
        r2 = MonitorResult(monitor_type=MonitorType.DISK, target="/", status="ok")
        r1.metadata["foo"] = "bar"
        assert "foo" not in r2.metadata

    def test_alert_defaults(self):
        alert = Alert(
            id="abc",
            monitor_type=MonitorType.UPTIME,
            level=AlertLevel.WARNING,
            target="https://example.com",
            message="down",
        )
        assert alert.status == AlertStatus.NEW
        assert alert.created_at > 0
        assert alert.resolved_at is None
        assert alert.metadata == {}
        assert alert.acknowledged_by is None
        assert alert.acknowledged_at is None

    def test_monitor_config_defaults(self):
        config = MonitorConfig()
        assert config.uptime_enabled is True
        assert config.uptime_interval == 300
        assert config.ssl_warning_days == 30
        assert config.ssl_critical_days == 7
        assert config.disk_warning_percent == 80
        assert config.disk_critical_percent == 90
        assert config.alert_enabled is True
        assert config.alert_cooldown == 3600
        assert config.alert_channels == ["email"]

    def test_monitor_config_alert_channels_independent(self):
        c1 = MonitorConfig()
        c2 = MonitorConfig()
        c1.alert_channels.append("slack")
        assert c2.alert_channels == ["email"]


# ---------------------------------------------------------------------------
# UptimeMonitor
# ---------------------------------------------------------------------------
class TestUptimeMonitor:
    """可用性监控测试"""

    def test_init_default(self):
        monitor = UptimeMonitor()
        assert monitor.timeout == 30

    def test_init_custom(self):
        monitor = UptimeMonitor(timeout=10)
        assert monitor.timeout == 10

    def test_check_ok(self):
        monitor = UptimeMonitor(timeout=5)
        mock_response = MagicMock()
        mock_response.getcode.return_value = 200

        with patch("urllib.request.urlopen", return_value=mock_response):
            result = monitor.check("https://example.com")

        assert result.monitor_type == MonitorType.UPTIME
        assert result.target == "https://example.com"
        assert result.status == "ok"
        assert result.value == 200.0
        assert "HTTP 200" in result.message
        assert result.metadata["status_code"] == 200
        assert result.duration >= 0

    def test_check_warning_status_code(self):
        monitor = UptimeMonitor(timeout=5)
        mock_response = MagicMock()
        mock_response.getcode.return_value = 404

        with patch("urllib.request.urlopen", return_value=mock_response):
            result = monitor.check("https://example.com")

        assert result.status == "warning"
        assert result.value == 404.0
        assert "404" in result.message

    def test_check_redirect_ok(self):
        monitor = UptimeMonitor(timeout=5)
        mock_response = MagicMock()
        mock_response.getcode.return_value = 301

        with patch("urllib.request.urlopen", return_value=mock_response):
            result = monitor.check("https://example.com")

        assert result.status == "ok"

    def test_check_http_error(self):
        monitor = UptimeMonitor(timeout=5)
        err = urllib.error.HTTPError(
            url="https://example.com",
            code=500,
            msg="Internal Server Error",
            hdrs=None,
            fp=None,
        )

        with patch("urllib.request.urlopen", side_effect=err):
            result = monitor.check("https://example.com")

        assert result.status == "error"
        assert result.value == 500.0
        assert "HTTP Error" in result.message

    def test_check_url_error(self):
        monitor = UptimeMonitor(timeout=5)
        err = urllib.error.URLError("Connection refused")

        with patch("urllib.request.urlopen", side_effect=err):
            result = monitor.check("https://example.com")

        assert result.status == "critical"
        assert result.value == 0.0
        assert "Connection failed" in result.message

    def test_check_generic_exception(self):
        monitor = UptimeMonitor(timeout=5)

        with patch("urllib.request.urlopen", side_effect=ValueError("boom")):
            result = monitor.check("https://example.com")

        assert result.status == "error"
        assert "boom" in result.message


# ---------------------------------------------------------------------------
# SSLMonitor
# ---------------------------------------------------------------------------
class TestSSLMonitor:
    """SSL证书监控测试"""

    def test_init_default(self):
        monitor = SSLMonitor()
        assert monitor.port == 443

    def test_init_custom(self):
        monitor = SSLMonitor(port=8443)
        assert monitor.port == 8443

    def test_check_ok(self):
        monitor = SSLMonitor()
        future = datetime.datetime.utcnow() + datetime.timedelta(days=90)
        cert = {
            "notAfter": future.strftime("%b %d %H:%M:%S %Y GMT"),
            "issuer": ((("organizationName", "Test CA"),),),
            "subject": ((("commonName", "example.com"),),),
            "subjectAltName": (("DNS", "example.com"),),
        }

        mock_ssock = MagicMock()
        mock_ssock.getpeercert.return_value = cert

        mock_context = MagicMock()
        mock_context.wrap_socket.return_value.__enter__.return_value = mock_ssock

        mock_sock = MagicMock()

        with patch("ssl.create_default_context", return_value=mock_context), \
             patch("socket.create_connection", return_value=mock_sock):
            result = monitor.check("example.com")

        assert result.monitor_type == MonitorType.SSL
        assert result.target == "example.com"
        assert result.status == "ok"
        assert result.value >= 89
        assert "days left" in result.message
        assert result.metadata["issuer"] == "Test CA"
        assert result.metadata["common_name"] == "example.com"

    def test_check_warning(self):
        monitor = SSLMonitor()
        future = datetime.datetime.utcnow() + datetime.timedelta(days=20)
        cert = {
            "notAfter": future.strftime("%b %d %H:%M:%S %Y GMT"),
            "issuer": ((("organizationName", "Test CA"),),),
            "subject": ((("commonName", "example.com"),),),
        }

        mock_ssock = MagicMock()
        mock_ssock.getpeercert.return_value = cert

        mock_context = MagicMock()
        mock_context.wrap_socket.return_value.__enter__.return_value = mock_ssock

        with patch("ssl.create_default_context", return_value=mock_context), \
             patch("socket.create_connection", return_value=MagicMock()):
            result = monitor.check("example.com")

        assert result.status == "warning"
        assert result.value >= 19

    def test_check_critical(self):
        monitor = SSLMonitor()
        future = datetime.datetime.utcnow() + datetime.timedelta(days=3)
        cert = {
            "notAfter": future.strftime("%b %d %H:%M:%S %Y GMT"),
            "issuer": ((("organizationName", "Test CA"),),),
            "subject": ((("commonName", "example.com"),),),
        }

        mock_ssock = MagicMock()
        mock_ssock.getpeercert.return_value = cert

        mock_context = MagicMock()
        mock_context.wrap_socket.return_value.__enter__.return_value = mock_ssock

        with patch("ssl.create_default_context", return_value=mock_context), \
             patch("socket.create_connection", return_value=MagicMock()):
            result = monitor.check("example.com")

        assert result.status == "critical"
        assert result.value >= 2

    def test_check_ssl_error(self):
        monitor = SSLMonitor()
        import ssl as _ssl

        with patch("ssl.create_default_context", side_effect=_ssl.SSLError("bad cert")):
            result = monitor.check("example.com")

        assert result.status == "critical"
        assert "SSL Error" in result.message

    def test_check_timeout(self):
        monitor = SSLMonitor()

        with patch("socket.create_connection", side_effect=socket.timeout("timed out")):
            result = monitor.check("example.com")

        assert result.status == "error"
        assert "timed out" in result.message.lower() or "Connection timed out" in result.message

    def test_check_generic_exception(self):
        monitor = SSLMonitor()

        with patch("socket.create_connection", side_effect=OSError("nope")):
            result = monitor.check("example.com")

        assert result.status == "error"
        assert "nope" in result.message


# ---------------------------------------------------------------------------
# DiskMonitor
# ---------------------------------------------------------------------------
class TestDiskMonitor:
    """磁盘监控测试"""

    def test_check_ok(self):
        monitor = DiskMonitor()
        # total=100GB, used=50GB, free=50GB -> 50% used
        total = 100 * (1024 ** 3)
        used = 50 * (1024 ** 3)
        free = 50 * (1024 ** 3)

        with patch("shutil.disk_usage", return_value=(total, used, free)):
            result = monitor.check("/")

        assert result.monitor_type == MonitorType.DISK
        assert result.target == "/"
        assert result.status == "ok"
        assert result.value == 50.0
        assert "normal" in result.message
        assert result.metadata["total_gb"] == 100.0
        assert result.metadata["used_gb"] == 50.0
        assert result.metadata["free_gb"] == 50.0

    def test_check_warning(self):
        monitor = DiskMonitor()
        total = 100 * (1024 ** 3)
        used = 85 * (1024 ** 3)
        free = 15 * (1024 ** 3)

        with patch("shutil.disk_usage", return_value=(total, used, free)):
            result = monitor.check("/")

        assert result.status == "warning"
        assert result.value == 85.0
        assert "high" in result.message

    def test_check_critical(self):
        monitor = DiskMonitor()
        total = 100 * (1024 ** 3)
        used = 95 * (1024 ** 3)
        free = 5 * (1024 ** 3)

        with patch("shutil.disk_usage", return_value=(total, used, free)):
            result = monitor.check("/")

        assert result.status == "critical"
        assert result.value == 95.0
        assert "critical" in result.message

    def test_check_exception(self):
        monitor = DiskMonitor()

        with patch("shutil.disk_usage", side_effect=OSError("no disk")):
            result = monitor.check("/nonexistent")

        assert result.status == "error"
        assert "no disk" in result.message


# ---------------------------------------------------------------------------
# PerformanceMonitor
# ---------------------------------------------------------------------------
class TestPerformanceMonitor:
    """性能监控测试"""

    def test_check_fast(self):
        monitor = PerformanceMonitor()
        mock_response = MagicMock()
        mock_response.getcode.return_value = 200
        mock_response.read.return_value = b"x" * 1024

        with patch("urllib.request.urlopen", return_value=mock_response):
            result = monitor.check("https://example.com")

        assert result.monitor_type == MonitorType.PERFORMANCE
        assert result.target == "https://example.com"
        assert result.status == "ok"
        assert result.value >= 0
        assert result.metadata["page_size_kb"] == 1.0

    def test_check_exception(self):
        monitor = PerformanceMonitor()

        with patch("urllib.request.urlopen", side_effect=ValueError("boom")):
            result = monitor.check("https://example.com")

        assert result.status == "error"
        assert "boom" in result.message

    def test_check_returns_metadata(self):
        monitor = PerformanceMonitor()
        mock_response = MagicMock()
        mock_response.getcode.return_value = 200
        mock_response.read.return_value = b"x" * 2048

        with patch("urllib.request.urlopen", return_value=mock_response):
            result = monitor.check("https://example.com")

        assert "load_time_ms" in result.metadata
        assert "page_size_kb" in result.metadata
        assert "status_code" in result.metadata
        assert result.metadata["page_size_kb"] == 2.0


# ---------------------------------------------------------------------------
# AlertManager
# ---------------------------------------------------------------------------
class TestAlertManager:
    """告警管理器测试"""

    def test_init(self):
        manager = AlertManager()
        assert manager.alerts == {}
        assert manager._alert_history == []
        assert manager._cooldown == 3600

    def test_create_alert(self):
        manager = AlertManager()
        alert = manager.create_alert(
            monitor_type=MonitorType.UPTIME,
            level=AlertLevel.CRITICAL,
            target="https://example.com",
            message="Site down",
        )
        assert alert.id != ""
        assert alert.monitor_type == MonitorType.UPTIME
        assert alert.level == AlertLevel.CRITICAL
        assert alert.target == "https://example.com"
        assert alert.message == "Site down"
        assert alert.status == AlertStatus.NEW
        assert alert.id in manager.alerts
        assert len(manager._alert_history) == 1

    def test_create_alert_with_metadata(self):
        manager = AlertManager()
        alert = manager.create_alert(
            monitor_type=MonitorType.SSL,
            level=AlertLevel.WARNING,
            target="example.com",
            message="expiring",
            metadata={"days": 20},
        )
        assert alert.metadata == {"days": 20}

    def test_create_alert_cooldown(self):
        manager = AlertManager()
        manager._cooldown = 3600

        alert1 = manager.create_alert(
            monitor_type=MonitorType.UPTIME,
            level=AlertLevel.CRITICAL,
            target="https://example.com",
            message="down",
        )
        # 同样的 key 在冷却期内不会创建新告警，返回已存在的
        alert2 = manager.create_alert(
            monitor_type=MonitorType.UPTIME,
            level=AlertLevel.CRITICAL,
            target="https://example.com",
            message="down again",
        )
        assert alert1.id == alert2.id
        # 历史中只有一条
        assert len(manager._alert_history) == 1
        # 消息保持原样
        assert alert2.message == "down"

    def test_create_alert_after_cooldown(self):
        manager = AlertManager()
        manager._cooldown = 0  # 无冷却

        alert1 = manager.create_alert(
            monitor_type=MonitorType.UPTIME,
            level=AlertLevel.CRITICAL,
            target="https://example.com",
            message="down",
        )
        # 冷却时间为 0，但 alert_id 相同所以会被覆盖
        alert2 = manager.create_alert(
            monitor_type=MonitorType.UPTIME,
            level=AlertLevel.CRITICAL,
            target="https://example.com",
            message="down again",
        )
        assert alert1.id == alert2.id
        # 因为 alert_id 相同，新告警覆盖旧告警，历史中应有 2 条
        assert len(manager._alert_history) == 2

    def test_resolve_alert(self):
        manager = AlertManager()
        alert = manager.create_alert(
            monitor_type=MonitorType.UPTIME,
            level=AlertLevel.ERROR,
            target="https://example.com",
            message="error",
        )
        resolved = manager.resolve_alert(alert.id)
        assert resolved is not None
        assert resolved.status == AlertStatus.RESOLVED
        assert resolved.resolved_at is not None
        assert alert.id not in manager.alerts

    def test_resolve_alert_not_found(self):
        manager = AlertManager()
        assert manager.resolve_alert("nonexistent") is None

    def test_acknowledge_alert(self):
        manager = AlertManager()
        alert = manager.create_alert(
            monitor_type=MonitorType.SSL,
            level=AlertLevel.WARNING,
            target="example.com",
            message="warning",
        )
        ack = manager.acknowledge_alert(alert.id, user="admin")
        assert ack is not None
        assert ack.status == AlertStatus.ACKNOWLEDGED
        assert ack.acknowledged_by == "admin"
        assert ack.acknowledged_at is not None
        # acknowledged alerts remain in active alerts
        assert alert.id in manager.alerts

    def test_acknowledge_alert_not_found(self):
        manager = AlertManager()
        assert manager.acknowledge_alert("nonexistent") is None

    def test_get_active_alerts_all(self):
        manager = AlertManager()
        manager.create_alert(MonitorType.UPTIME, AlertLevel.CRITICAL, "t1", "m1")
        manager.create_alert(MonitorType.SSL, AlertLevel.WARNING, "t2", "m2")
        alerts = manager.get_active_alerts()
        assert len(alerts) == 2

    def test_get_active_alerts_filter_level(self):
        manager = AlertManager()
        manager.create_alert(MonitorType.UPTIME, AlertLevel.CRITICAL, "t1", "m1")
        manager.create_alert(MonitorType.SSL, AlertLevel.WARNING, "t2", "m2")
        alerts = manager.get_active_alerts(level=AlertLevel.CRITICAL)
        assert len(alerts) == 1
        assert alerts[0].level == AlertLevel.CRITICAL

    def test_get_active_alerts_filter_type(self):
        manager = AlertManager()
        manager.create_alert(MonitorType.UPTIME, AlertLevel.CRITICAL, "t1", "m1")
        manager.create_alert(MonitorType.SSL, AlertLevel.WARNING, "t2", "m2")
        alerts = manager.get_active_alerts(monitor_type=MonitorType.SSL)
        assert len(alerts) == 1
        assert alerts[0].monitor_type == MonitorType.SSL

    def test_get_alert_history(self):
        manager = AlertManager()
        manager.create_alert(MonitorType.UPTIME, AlertLevel.CRITICAL, "t1", "m1")
        manager.create_alert(MonitorType.SSL, AlertLevel.WARNING, "t2", "m2")
        history = manager.get_alert_history()
        assert len(history) == 2

    def test_get_alert_history_limit(self):
        manager = AlertManager()
        for i in range(5):
            manager.create_alert(MonitorType.UPTIME, AlertLevel.CRITICAL, f"t{i}", f"m{i}")
        history = manager.get_alert_history(limit=3)
        assert len(history) == 3

    def test_get_alert_stats(self):
        manager = AlertManager()
        manager.create_alert(MonitorType.UPTIME, AlertLevel.CRITICAL, "t1", "m1")
        manager.create_alert(MonitorType.UPTIME, AlertLevel.ERROR, "t2", "m2")
        manager.create_alert(MonitorType.SSL, AlertLevel.WARNING, "t3", "m3")
        stats = manager.get_alert_stats()
        assert stats["active_alerts"] == 3
        assert stats["critical"] == 1
        assert stats["errors"] == 1
        assert stats["warnings"] == 1
        assert stats["total_history"] == 3
        assert "uptime" in stats["by_type"]
        assert "ssl" in stats["by_type"]

    def test_get_alert_stats_empty(self):
        manager = AlertManager()
        stats = manager.get_alert_stats()
        assert stats["active_alerts"] == 0
        assert stats["critical"] == 0
        assert stats["total_history"] == 0
        assert stats["by_type"] == {}


# ---------------------------------------------------------------------------
# SiteMonitorService
# ---------------------------------------------------------------------------
class TestSiteMonitorService:
    """站点监控服务测试"""

    def test_init_default(self):
        service = SiteMonitorService()
        assert isinstance(service.config, MonitorConfig)
        assert isinstance(service.uptime_monitor, UptimeMonitor)
        assert isinstance(service.ssl_monitor, SSLMonitor)
        assert isinstance(service.disk_monitor, DiskMonitor)
        assert isinstance(service.performance_monitor, PerformanceMonitor)
        assert isinstance(service.alert_manager, AlertManager)
        assert service._monitor_history == {}

    def test_init_with_config(self):
        config = MonitorConfig(uptime_enabled=False, ssl_enabled=False)
        service = SiteMonitorService(config=config)
        assert service.config.uptime_enabled is False
        assert service.config.ssl_enabled is False

    def test_check_site_uptime_ok(self):
        service = SiteMonitorService(MonitorConfig(
            uptime_enabled=True,
            ssl_enabled=False,
            performance_enabled=False,
        ))
        mock_response = MagicMock()
        mock_response.getcode.return_value = 200

        with patch("urllib.request.urlopen", return_value=mock_response):
            results = service.check_site("https://example.com")

        assert "uptime" in results
        assert results["uptime"].status == "ok"

    def test_check_site_with_ssl(self):
        service = SiteMonitorService(MonitorConfig(
            uptime_enabled=False,
            ssl_enabled=True,
            performance_enabled=False,
        ))
        future = datetime.datetime.utcnow() + datetime.timedelta(days=90)
        cert = {
            "notAfter": future.strftime("%b %d %H:%M:%S %Y GMT"),
            "issuer": ((("organizationName", "Test CA"),),),
            "subject": ((("commonName", "example.com"),),),
        }
        mock_ssock = MagicMock()
        mock_ssock.getpeercert.return_value = cert
        mock_context = MagicMock()
        mock_context.wrap_socket.return_value.__enter__.return_value = mock_ssock

        with patch("ssl.create_default_context", return_value=mock_context), \
             patch("socket.create_connection", return_value=MagicMock()):
            results = service.check_site("https://example.com")

        assert "ssl" in results
        assert results["ssl"].status == "ok"

    def test_check_site_hostname_extracted(self):
        service = SiteMonitorService(MonitorConfig(
            uptime_enabled=False,
            ssl_enabled=True,
            performance_enabled=False,
        ))
        future = datetime.datetime.utcnow() + datetime.timedelta(days=90)
        cert = {
            "notAfter": future.strftime("%b %d %H:%M:%S %Y GMT"),
            "issuer": ((("organizationName", "Test CA"),),),
            "subject": ((("commonName", "example.com"),),),
        }
        mock_ssock = MagicMock()
        mock_ssock.getpeercert.return_value = cert
        mock_context = MagicMock()
        mock_context.wrap_socket.return_value.__enter__.return_value = mock_ssock

        with patch("ssl.create_default_context", return_value=mock_context), \
             patch("socket.create_connection", return_value=MagicMock()) as mock_conn:
            service.check_site("https://example.com/path")

        # socket.create_connection 应该被调用，主机名为 example.com
        mock_conn.assert_called_once()
        args, _ = mock_conn.call_args
        assert args[0][0] == "example.com"

    def test_check_site_all_disabled(self):
        service = SiteMonitorService(MonitorConfig(
            uptime_enabled=False,
            ssl_enabled=False,
            performance_enabled=False,
        ))
        results = service.check_site("https://example.com")
        assert results == {}

    def test_check_site_critical_creates_alert(self):
        service = SiteMonitorService(MonitorConfig(
            uptime_enabled=True,
            ssl_enabled=False,
            performance_enabled=False,
        ))
        err = urllib.error.URLError("Connection refused")
        with patch("urllib.request.urlopen", side_effect=err):
            service.check_site("https://example.com")
        # critical 状态应触发告警
        alerts = service.alert_manager.get_active_alerts()
        assert len(alerts) >= 1
        assert alerts[0].level == AlertLevel.CRITICAL

    def test_check_system_disk_ok(self):
        service = SiteMonitorService(MonitorConfig(disk_enabled=True))
        total = 100 * (1024 ** 3)
        used = 50 * (1024 ** 3)
        free = 50 * (1024 ** 3)

        with patch("shutil.disk_usage", return_value=(total, used, free)):
            results = service.check_system()

        assert "disk" in results
        assert results["disk"].status == "ok"

    def test_check_system_disk_disabled(self):
        service = SiteMonitorService(MonitorConfig(disk_enabled=False))
        results = service.check_system()
        assert results == {}

    def test_process_result_saves_history(self):
        service = SiteMonitorService()
        result = MonitorResult(
            monitor_type=MonitorType.UPTIME,
            target="https://example.com",
            status="ok",
        )
        service._process_result(result)
        history = service.get_monitor_history(MonitorType.UPTIME, "https://example.com")
        assert len(history) == 1
        assert history[0] is result

    def test_process_result_critical_creates_alert(self):
        service = SiteMonitorService(MonitorConfig(alert_enabled=True))
        result = MonitorResult(
            monitor_type=MonitorType.UPTIME,
            target="https://example.com",
            status="critical",
            message="site down",
        )
        service._process_result(result)
        alerts = service.alert_manager.get_active_alerts()
        assert len(alerts) == 1
        assert alerts[0].level == AlertLevel.CRITICAL

    def test_process_result_error_creates_alert(self):
        service = SiteMonitorService(MonitorConfig(alert_enabled=True))
        result = MonitorResult(
            monitor_type=MonitorType.SSL,
            target="example.com",
            status="error",
            message="ssl error",
        )
        service._process_result(result)
        alerts = service.alert_manager.get_active_alerts()
        assert len(alerts) == 1
        assert alerts[0].level == AlertLevel.ERROR

    def test_process_result_warning_creates_alert(self):
        service = SiteMonitorService(MonitorConfig(alert_enabled=True))
        result = MonitorResult(
            monitor_type=MonitorType.DISK,
            target="/",
            status="warning",
            message="disk high",
        )
        service._process_result(result)
        alerts = service.alert_manager.get_active_alerts()
        assert len(alerts) == 1
        assert alerts[0].level == AlertLevel.WARNING

    def test_process_result_ok_no_alert(self):
        service = SiteMonitorService(MonitorConfig(alert_enabled=True))
        result = MonitorResult(
            monitor_type=MonitorType.UPTIME,
            target="https://example.com",
            status="ok",
            message="up",
        )
        service._process_result(result)
        alerts = service.alert_manager.get_active_alerts()
        assert len(alerts) == 0

    def test_process_result_alert_disabled(self):
        service = SiteMonitorService(MonitorConfig(alert_enabled=False))
        result = MonitorResult(
            monitor_type=MonitorType.UPTIME,
            target="https://example.com",
            status="critical",
            message="down",
        )
        service._process_result(result)
        # alert disabled, no alert created
        alerts = service.alert_manager.get_active_alerts()
        assert len(alerts) == 0
        # but history still saved
        history = service.get_monitor_history(MonitorType.UPTIME, "https://example.com")
        assert len(history) == 1

    def test_process_result_history_limit(self):
        service = SiteMonitorService()
        # 添加 110 条记录
        for i in range(110):
            result = MonitorResult(
                monitor_type=MonitorType.UPTIME,
                target="https://example.com",
                status="ok",
                message=f"m{i}",
            )
            service._process_result(result)
        history = service.get_monitor_history(MonitorType.UPTIME, "https://example.com", limit=200)
        # 应只保留最近 100 条
        assert len(history) == 100

    def test_get_monitor_history_empty(self):
        service = SiteMonitorService()
        history = service.get_monitor_history(MonitorType.UPTIME, "https://nope.com")
        assert history == []

    def test_get_monitor_history_limit(self):
        service = SiteMonitorService()
        for i in range(10):
            service._process_result(MonitorResult(
                monitor_type=MonitorType.UPTIME,
                target="https://example.com",
                status="ok",
            ))
        history = service.get_monitor_history(MonitorType.UPTIME, "https://example.com", limit=5)
        assert len(history) == 5

    def test_get_site_status(self):
        service = SiteMonitorService()
        status = service.get_site_status("https://example.com")
        assert status["url"] == "https://example.com"
        assert "overall_status" in status
        assert "last_check" in status
        assert "monitors" in status

    def test_get_dashboard_data(self):
        service = SiteMonitorService()
        data = service.get_dashboard_data()
        assert "alerts" in data
        assert "active_sites" in data
        assert "uptime_percentage" in data
        assert "avg_response_time" in data
        assert "monitored_urls" in data
        assert "recent_alerts" in data

    def test_get_dashboard_data_with_alerts(self):
        service = SiteMonitorService()
        service.alert_manager.create_alert(
            MonitorType.UPTIME, AlertLevel.CRITICAL, "https://example.com", "down"
        )
        data = service.get_dashboard_data()
        assert data["alerts"]["active_alerts"] == 1

    def test_get_monitoring_tips(self):
        service = SiteMonitorService()
        tips = service.get_monitoring_tips()
        assert isinstance(tips, list)
        assert len(tips) > 0
        assert all(isinstance(t, str) for t in tips)


# ---------------------------------------------------------------------------
# 全局实例
# ---------------------------------------------------------------------------
class TestGlobalInstance:
    """全局实例测试"""

    def test_global_instance_exists(self):
        assert site_monitor_service is not None
        assert isinstance(site_monitor_service, SiteMonitorService)

    def test_global_instance_has_components(self):
        assert isinstance(site_monitor_service.uptime_monitor, UptimeMonitor)
        assert isinstance(site_monitor_service.alert_manager, AlertManager)


# ===========================================================================
# 以下为新增测试用例：扩展监控类型、Webhook告警、告警规则、趋势图表、异步方法
# ===========================================================================


class TestExtendedMonitorType:
    """扩展监控类型枚举测试"""

    def test_values(self):
        assert ExtendedMonitorType.CONTENT_CHANGE.value == "content_change"
        assert ExtendedMonitorType.KEYWORD_RANKING.value == "keyword_ranking"
        assert ExtendedMonitorType.BACKLINK.value == "backlink"
        assert ExtendedMonitorType.TRAFFIC.value == "traffic"
        assert ExtendedMonitorType.HTTP_STATUS.value == "http_status"
        assert ExtendedMonitorType.RESPONSE_TIME.value == "response_time"

    def test_is_str_enum(self):
        assert isinstance(ExtendedMonitorType.CONTENT_CHANGE, str)


class TestWebhookType:
    """Webhook类型枚举测试"""

    def test_values(self):
        assert WebhookType.FEISHU.value == "feishu"
        assert WebhookType.DINGTALK.value == "dingtalk"
        assert WebhookType.WECOM.value == "wecom"
        assert WebhookType.SLACK.value == "slack"
        assert WebhookType.GENERIC.value == "generic"

    def test_is_str_enum(self):
        assert isinstance(WebhookType.FEISHU, str)


class TestContentChangeResult:
    """内容变化结果数据类测试"""

    def test_defaults(self):
        result = ContentChangeResult(url="https://example.com", changed=False)
        assert result.similarity == 0.0
        assert result.old_hash == ""
        assert result.new_hash == ""
        assert result.message == ""
        assert result.timestamp > 0

    def test_full(self):
        result = ContentChangeResult(
            url="https://example.com",
            changed=True,
            similarity=0.85,
            old_hash="abc",
            new_hash="def",
            message="changed",
        )
        assert result.changed is True
        assert result.similarity == 0.85
        assert result.old_hash == "abc"


class TestKeywordRankingResult:
    """关键词排名结果数据类测试"""

    def test_defaults(self):
        result = KeywordRankingResult(keyword="test", url="https://example.com")
        assert result.position == 0
        assert result.previous_position is None
        assert result.change == 0
        assert result.search_engine == "google"

    def test_full(self):
        result = KeywordRankingResult(
            keyword="test", url="https://example.com", position=5, previous_position=10, change=5
        )
        assert result.position == 5
        assert result.previous_position == 10
        assert result.change == 5


class TestBacklinkResult:
    """外链结果数据类测试"""

    def test_defaults(self):
        result = BacklinkResult(url="https://example.com")
        assert result.backlink_count == 0
        assert result.previous_count is None
        assert result.change == 0
        assert result.referring_domains == 0

    def test_full(self):
        result = BacklinkResult(
            url="https://example.com",
            backlink_count=100,
            previous_count=80,
            change=20,
            referring_domains=50,
        )
        assert result.backlink_count == 100
        assert result.change == 20


class TestTrafficResult:
    """流量结果数据类测试"""

    def test_defaults(self):
        result = TrafficResult(url="https://example.com")
        assert result.visits == 0
        assert result.unique_visitors == 0
        assert result.page_views == 0
        assert result.bounce_rate == 0.0

    def test_full(self):
        result = TrafficResult(
            url="https://example.com",
            visits=1000,
            unique_visitors=800,
            page_views=2500,
            bounce_rate=0.35,
            avg_session_duration=300.5,
        )
        assert result.visits == 1000
        assert result.bounce_rate == 0.35


class TestAlertRule:
    """告警规则数据类测试"""

    def test_defaults(self):
        rule = AlertRule(name="test", monitor_type="uptime")
        assert rule.threshold == 0.0
        assert rule.comparison == ">"
        assert rule.consecutive_failures == 1
        assert rule.cooldown_period == 3600
        assert rule.escalation_after == 0
        assert rule.enabled is True

    def test_full(self):
        rule = AlertRule(
            name="test",
            monitor_type="uptime",
            threshold=1000.0,
            comparison=">=",
            consecutive_failures=3,
            cooldown_period=1800,
            escalation_after=5,
            escalation_level="critical",
        )
        assert rule.threshold == 1000.0
        assert rule.consecutive_failures == 3
        assert rule.escalation_after == 5


class TestContentChangeMonitor:
    """首页内容变化监控器测试"""

    def test_first_check_no_change(self):
        monitor = ContentChangeMonitor()
        result = monitor.check("https://example.com", content="page-content")
        assert result.changed is False
        assert result.similarity == 1.0
        assert result.new_hash != ""

    def test_second_check_same_content(self):
        monitor = ContentChangeMonitor()
        monitor.check("https://example.com", content="same-content")
        result = monitor.check("https://example.com", content="same-content")
        assert result.changed is False

    def test_second_check_different_content(self):
        monitor = ContentChangeMonitor()
        monitor.check("https://example.com", content="content-v1")
        result = monitor.check("https://example.com", content="content-v2")
        assert result.changed is True
        assert result.old_hash != result.new_hash

    def test_get_stored_hash(self):
        monitor = ContentChangeMonitor()
        monitor.check("https://example.com", content="content")
        h = monitor.get_stored_hash("https://example.com")
        assert h != ""
        assert monitor.get_stored_hash("https://nope.com") == ""

    def test_reset_specific_url(self):
        monitor = ContentChangeMonitor()
        monitor.check("https://example.com", content="content")
        monitor.reset("https://example.com")
        assert monitor.get_stored_hash("https://example.com") == ""

    def test_reset_all(self):
        monitor = ContentChangeMonitor()
        monitor.check("https://a.com", content="a")
        monitor.check("https://b.com", content="b")
        monitor.reset()
        assert monitor.get_stored_hash("https://a.com") == ""
        assert monitor.get_stored_hash("https://b.com") == ""

    def test_simulated_content_when_none(self):
        monitor = ContentChangeMonitor()
        result = monitor.check("https://example.com")
        assert result.new_hash != ""


class TestKeywordRankingMonitor:
    """关键词排名监控器测试"""

    def test_first_check(self):
        monitor = KeywordRankingMonitor()
        result = monitor.check("wordpress", "https://example.com")
        assert result.keyword == "wordpress"
        assert result.position > 0
        assert result.previous_position is None
        assert result.change == 0

    def test_second_check_tracks_change(self):
        monitor = KeywordRankingMonitor()
        first = monitor.check("wordpress", "https://example.com")
        second = monitor.check("wordpress", "https://example.com")
        assert second.previous_position == first.position
        assert second.change == first.position - second.position

    def test_get_history(self):
        monitor = KeywordRankingMonitor()
        monitor.check("wordpress", "https://example.com")
        monitor.check("wordpress", "https://example.com")
        history = monitor.get_history("wordpress", "https://example.com")
        assert len(history) == 2

    def test_get_history_empty(self):
        monitor = KeywordRankingMonitor()
        history = monitor.get_history("nope", "https://example.com")
        assert history == []

    def test_different_search_engines(self):
        monitor = KeywordRankingMonitor()
        monitor.check("wordpress", "https://example.com", "google")
        monitor.check("wordpress", "https://example.com", "bing")
        google_history = monitor.get_history("wordpress", "https://example.com", "google")
        bing_history = monitor.get_history("wordpress", "https://example.com", "bing")
        assert len(google_history) == 1
        assert len(bing_history) == 1


class TestBacklinkMonitor:
    """外链监控器测试"""

    def test_first_check(self):
        monitor = BacklinkMonitor()
        result = monitor.check("https://example.com")
        assert result.backlink_count > 0
        assert result.previous_count is None
        assert result.referring_domains > 0

    def test_second_check_tracks_change(self):
        monitor = BacklinkMonitor()
        first = monitor.check("https://example.com")
        second = monitor.check("https://example.com")
        assert second.previous_count == first.backlink_count

    def test_get_history(self):
        monitor = BacklinkMonitor()
        monitor.check("https://example.com")
        monitor.check("https://example.com")
        history = monitor.get_history("https://example.com")
        assert len(history) == 2

    def test_get_history_empty(self):
        monitor = BacklinkMonitor()
        assert monitor.get_history("https://nope.com") == []


class TestTrafficMonitor:
    """流量监控器测试"""

    def test_check(self):
        monitor = TrafficMonitor()
        result = monitor.check("https://example.com")
        assert result.visits > 0
        assert result.unique_visitors > 0
        assert result.page_views > 0
        assert 0 <= result.bounce_rate <= 1

    def test_get_history(self):
        monitor = TrafficMonitor()
        monitor.check("https://example.com")
        monitor.check("https://example.com")
        history = monitor.get_history("https://example.com")
        assert len(history) == 2

    def test_get_history_empty(self):
        monitor = TrafficMonitor()
        assert monitor.get_history("https://nope.com") == []


class TestWebhookAlertSender:
    """Webhook告警发送器测试"""

    def _make_alert(self):
        return Alert(
            id="test-alert-1",
            monitor_type=MonitorType.UPTIME,
            level=AlertLevel.CRITICAL,
            target="https://example.com",
            message="Site down",
        )

    def test_register_and_get_webhook(self):
        sender = WebhookAlertSender()
        sender.register_webhook(WebhookType.FEISHU, "https://open.feishu.cn/hook/xxx")
        assert sender.get_webhook(WebhookType.FEISHU) == "https://open.feishu.cn/hook/xxx"

    def test_remove_webhook(self):
        sender = WebhookAlertSender()
        sender.register_webhook(WebhookType.DINGTALK, "https://oapi.dingtalk.com/hook/xxx")
        assert sender.remove_webhook(WebhookType.DINGTALK) is True
        assert sender.get_webhook(WebhookType.DINGTALK) is None

    def test_remove_webhook_not_found(self):
        sender = WebhookAlertSender()
        assert sender.remove_webhook(WebhookType.FEISHU) is False

    def test_send_not_registered(self):
        sender = WebhookAlertSender()
        result = sender.send(WebhookType.FEISHU, self._make_alert())
        assert result["success"] is False
        assert result["error_code"] == "not_registered"

    def test_send_feishu(self):
        sender = WebhookAlertSender()
        sender.register_webhook(WebhookType.FEISHU, "https://open.feishu.cn/hook/xxx")
        result = sender.send(WebhookType.FEISHU, self._make_alert())
        assert result["success"] is True
        assert result["webhook_type"] == "feishu"

    def test_send_dingtalk(self):
        sender = WebhookAlertSender()
        sender.register_webhook(WebhookType.DINGTALK, "https://oapi.dingtalk.com/hook/xxx")
        result = sender.send(WebhookType.DINGTALK, self._make_alert())
        assert result["success"] is True

    def test_send_wecom(self):
        sender = WebhookAlertSender()
        sender.register_webhook(WebhookType.WECOM, "https://qyapi.weixin.qq.com/hook/xxx")
        result = sender.send(WebhookType.WECOM, self._make_alert())
        assert result["success"] is True

    def test_format_feishu_message(self):
        sender = WebhookAlertSender()
        msg = sender.format_message(WebhookType.FEISHU, self._make_alert())
        assert msg["msg_type"] == "text"
        assert "CRITICAL" in msg["content"]["text"]

    def test_format_dingtalk_message(self):
        sender = WebhookAlertSender()
        msg = sender.format_message(WebhookType.DINGTALK, self._make_alert())
        assert msg["msgtype"] == "text"
        assert "CRITICAL" in msg["text"]["content"]

    def test_format_generic_message(self):
        sender = WebhookAlertSender()
        msg = sender.format_message(WebhookType.GENERIC, self._make_alert())
        assert msg["level"] == "critical"
        assert msg["target"] == "https://example.com"

    def test_send_to_all(self):
        sender = WebhookAlertSender()
        sender.register_webhook(WebhookType.FEISHU, "https://open.feishu.cn/hook/xxx")
        sender.register_webhook(WebhookType.DINGTALK, "https://oapi.dingtalk.com/hook/xxx")
        results = sender.send_to_all(self._make_alert())
        assert len(results) == 2
        assert all(r["success"] for r in results.values())

    def test_get_send_history(self):
        sender = WebhookAlertSender()
        sender.register_webhook(WebhookType.FEISHU, "https://open.feishu.cn/hook/xxx")
        sender.send(WebhookType.FEISHU, self._make_alert())
        history = sender.get_send_history()
        assert len(history) == 1


class TestEmailAlertSender:
    """邮件告警发送器测试"""

    def _make_alert(self):
        return Alert(
            id="email-alert-1",
            monitor_type=MonitorType.SSL,
            level=AlertLevel.WARNING,
            target="example.com",
            message="SSL expiring",
        )

    def test_no_recipients(self):
        sender = EmailAlertSender()
        result = sender.send(self._make_alert())
        assert result["success"] is False
        assert result["error_code"] == "no_recipients"

    def test_configure_and_send(self):
        sender = EmailAlertSender()
        sender.configure(
            "smtp.example.com", 587, "user", "pass",
            "from@example.com", ["to@example.com"]
        )
        result = sender.send(self._make_alert())
        assert result["success"] is True
        assert "subject" in result

    def test_format_email(self):
        sender = EmailAlertSender()
        email = sender.format_email(self._make_alert())
        assert "WARNING" in email["subject"]
        assert "ssl" in email["subject"]
        assert "example.com" in email["body"]

    def test_get_send_history(self):
        sender = EmailAlertSender()
        sender.configure("smtp", 587, "u", "p", "f@e.com", ["t@e.com"])
        sender.send(self._make_alert())
        history = sender.get_send_history()
        assert len(history) == 1


class TestInAppAlertSender:
    """站内消息告警发送器测试"""

    def _make_alert(self):
        return Alert(
            id="inapp-alert-1",
            monitor_type=MonitorType.DISK,
            level=AlertLevel.ERROR,
            target="/",
            message="Disk full",
        )

    def test_send_broadcast(self):
        sender = InAppAlertSender()
        result = sender.send(self._make_alert())
        assert result["success"] is True
        assert "message_id" in result

    def test_send_to_user(self):
        sender = InAppAlertSender()
        result = sender.send(self._make_alert(), user_id=42)
        assert result["success"] is True

    def test_get_messages_all(self):
        sender = InAppAlertSender()
        sender.send(self._make_alert())
        messages = sender.get_messages()
        assert len(messages) == 1

    def test_get_messages_by_user(self):
        sender = InAppAlertSender()
        sender.send(self._make_alert(), user_id=42)
        sender.send(self._make_alert(), user_id=99)
        user_msgs = sender.get_messages(user_id=42)
        # 广播消息 + 用户42的消息
        assert all(m["user_id"] == 42 or m["user_id"] is None for m in user_msgs)

    def test_get_unread_only(self):
        sender = InAppAlertSender()
        sender.send(self._make_alert())
        sender.send(self._make_alert())
        unread = sender.get_messages(unread_only=True)
        assert len(unread) == 2

    def test_mark_as_read(self):
        sender = InAppAlertSender()
        result = sender.send(self._make_alert())
        msg_id = result["message_id"]
        assert sender.mark_as_read(msg_id) is True
        unread = sender.get_messages(unread_only=True)
        assert len(unread) == 0

    def test_mark_as_read_not_found(self):
        sender = InAppAlertSender()
        assert sender.mark_as_read("nonexistent") is False


class TestAlertRuleManager:
    """告警规则管理器测试"""

    def test_add_and_get_rule(self):
        mgr = AlertRuleManager()
        rule = AlertRule(name="high_response", monitor_type="uptime", threshold=2000.0, comparison=">")
        mgr.add_rule(rule)
        assert mgr.get_rule("high_response") is rule

    def test_remove_rule(self):
        mgr = AlertRuleManager()
        mgr.add_rule(AlertRule(name="r1", monitor_type="uptime"))
        assert mgr.remove_rule("r1") is True
        assert mgr.get_rule("r1") is None

    def test_remove_rule_not_found(self):
        mgr = AlertRuleManager()
        assert mgr.remove_rule("nonexistent") is False

    def test_get_all_rules(self):
        mgr = AlertRuleManager()
        mgr.add_rule(AlertRule(name="r1", monitor_type="uptime"))
        mgr.add_rule(AlertRule(name="r2", monitor_type="ssl"))
        rules = mgr.get_all_rules()
        assert len(rules) == 2

    def test_evaluate_threshold_not_met(self):
        mgr = AlertRuleManager()
        mgr.add_rule(AlertRule(name="r1", monitor_type="uptime", threshold=2000.0, comparison=">"))
        result = mgr.evaluate("r1", 500.0)
        assert result["should_alert"] is False
        assert result["reason"] == "threshold_not_met"

    def test_evaluate_threshold_met(self):
        mgr = AlertRuleManager()
        mgr.add_rule(AlertRule(name="r1", monitor_type="uptime", threshold=2000.0, comparison=">"))
        result = mgr.evaluate("r1", 3000.0)
        assert result["should_alert"] is True

    def test_evaluate_consecutive_failures(self):
        mgr = AlertRuleManager()
        mgr.add_rule(AlertRule(
            name="r1", monitor_type="uptime", threshold=2000.0,
            comparison=">", consecutive_failures=3
        ))
        # 第一次失败
        r1 = mgr.evaluate("r1", 3000.0)
        assert r1["should_alert"] is False
        assert r1["reason"] == "insufficient_consecutive_failures"
        # 第二次失败
        r2 = mgr.evaluate("r1", 3000.0)
        assert r2["should_alert"] is False
        # 第三次失败 -> 触发告警
        r3 = mgr.evaluate("r1", 3000.0)
        assert r3["should_alert"] is True

    def test_evaluate_resets_on_success(self):
        mgr = AlertRuleManager()
        mgr.add_rule(AlertRule(
            name="r1", monitor_type="uptime", threshold=2000.0,
            comparison=">", consecutive_failures=3
        ))
        mgr.evaluate("r1", 3000.0)
        mgr.evaluate("r1", 3000.0)
        # 恢复正常
        mgr.evaluate("r1", 500.0)
        assert mgr.get_failure_count("r1") == 0

    def test_evaluate_cooldown(self):
        mgr = AlertRuleManager()
        mgr.add_rule(AlertRule(
            name="r1", monitor_type="uptime", threshold=2000.0,
            comparison=">", cooldown_period=3600
        ))
        # 第一次告警
        r1 = mgr.evaluate("r1", 3000.0)
        assert r1["should_alert"] is True
        # 在冷却期内，不应再次告警
        r2 = mgr.evaluate("r1", 3000.0)
        assert r2["should_alert"] is False
        assert r2["reason"] == "in_cooldown"

    def test_evaluate_escalation(self):
        mgr = AlertRuleManager()
        mgr.add_rule(AlertRule(
            name="r1", monitor_type="uptime", threshold=2000.0,
            comparison=">", cooldown_period=0,
            escalation_after=2, escalation_level="critical"
        ))
        # 第一次告警（warning）
        r1 = mgr.evaluate("r1", 3000.0)
        assert r1["should_alert"] is True
        assert r1["escalated"] is False
        # 第二次告警 -> 升级
        r2 = mgr.evaluate("r1", 3000.0)
        assert r2["should_alert"] is True
        assert r2["escalated"] is True
        assert r2["level"] == "critical"

    def test_evaluate_disabled_rule(self):
        mgr = AlertRuleManager()
        mgr.add_rule(AlertRule(name="r1", monitor_type="uptime", threshold=2000.0, enabled=False))
        result = mgr.evaluate("r1", 3000.0)
        assert result["should_alert"] is False
        assert result["reason"] == "rule_not_found_or_disabled"

    def test_evaluate_rule_not_found(self):
        mgr = AlertRuleManager()
        result = mgr.evaluate("nonexistent", 100.0)
        assert result["should_alert"] is False

    def test_comparison_operators(self):
        mgr = AlertRuleManager()
        # 测试 < 操作符
        mgr.add_rule(AlertRule(name="low_ssl", monitor_type="ssl", threshold=30.0, comparison="<"))
        assert mgr.evaluate("low_ssl", 20.0)["should_alert"] is True
        assert mgr.evaluate("low_ssl", 40.0)["should_alert"] is False

    def test_get_alert_count(self):
        mgr = AlertRuleManager()
        mgr.add_rule(AlertRule(name="r1", monitor_type="uptime", threshold=2000.0, comparison=">", cooldown_period=0))
        mgr.evaluate("r1", 3000.0)
        mgr.evaluate("r1", 3000.0)
        assert mgr.get_alert_count("r1") == 2


class TestTrendChartService:
    """趋势图表数据服务测试"""

    def test_add_and_get_data_point(self):
        svc = TrendChartService()
        svc.add_data_point("uptime", time.time(), 99.9)
        data = svc.get_trend_data("uptime")
        assert len(data) == 1
        assert data[0]["value"] == 99.9

    def test_get_trend_data_with_time_range(self):
        svc = TrendChartService()
        now = time.time()
        svc.add_data_point("s1", now - 100, 1.0)
        svc.add_data_point("s1", now - 50, 2.0)
        svc.add_data_point("s1", now, 3.0)
        data = svc.get_trend_data("s1", start_time=now - 60)
        assert len(data) == 2

    def test_get_chart_data(self):
        svc = TrendChartService()
        for i in range(5):
            svc.add_data_point("s1", time.time() + i, float(i))
        chart = svc.get_chart_data("s1", points=3)
        assert chart["series"] == "s1"
        assert chart["point_count"] == 3
        assert len(chart["labels"]) == 3
        assert len(chart["values"]) == 3

    def test_get_summary_empty(self):
        svc = TrendChartService()
        summary = svc.get_summary("nonexistent")
        assert summary["count"] == 0
        assert summary["latest"] is None

    def test_get_summary_with_data(self):
        svc = TrendChartService()
        svc.add_data_point("s1", time.time(), 10.0)
        svc.add_data_point("s1", time.time(), 20.0)
        svc.add_data_point("s1", time.time(), 30.0)
        summary = svc.get_summary("s1")
        assert summary["count"] == 3
        assert summary["min"] == 10.0
        assert summary["max"] == 30.0
        assert summary["avg"] == 20.0
        assert summary["latest"] == 30.0

    def test_get_all_series(self):
        svc = TrendChartService()
        svc.add_data_point("s1", time.time(), 1.0)
        svc.add_data_point("s2", time.time(), 2.0)
        series = svc.get_all_series()
        assert "s1" in series
        assert "s2" in series

    def test_clear_series(self):
        svc = TrendChartService()
        svc.add_data_point("s1", time.time(), 1.0)
        assert svc.clear_series("s1") is True
        assert len(svc.get_trend_data("s1")) == 0

    def test_clear_series_not_found(self):
        svc = TrendChartService()
        assert svc.clear_series("nonexistent") is False

    def test_data_point_limit(self):
        svc = TrendChartService()
        for i in range(1100):
            svc.add_data_point("s1", time.time() + i, float(i))
        data = svc.get_trend_data("s1")
        # 应只保留最近1000条
        assert len(data) == 1000


class TestAsyncMonitoringMethods:
    """异步监控方法测试"""

    def test_async_check_uptime(self):
        mock_response = MagicMock()
        mock_response.getcode.return_value = 200
        with patch("urllib.request.urlopen", return_value=mock_response):
            result = asyncio.run(async_check_uptime("https://example.com", timeout=5))
        assert isinstance(result, MonitorResult)
        assert result.status == "ok"

    def test_async_check_ssl(self):
        future = datetime.datetime.utcnow() + datetime.timedelta(days=90)
        cert = {
            "notAfter": future.strftime("%b %d %H:%M:%S %Y GMT"),
            "issuer": ((("organizationName", "Test CA"),),),
            "subject": ((("commonName", "example.com"),),),
        }
        mock_ssock = MagicMock()
        mock_ssock.getpeercert.return_value = cert
        mock_context = MagicMock()
        mock_context.wrap_socket.return_value.__enter__.return_value = mock_ssock
        with patch("ssl.create_default_context", return_value=mock_context), \
             patch("socket.create_connection", return_value=MagicMock()):
            result = asyncio.run(async_check_ssl("example.com"))
        assert isinstance(result, MonitorResult)
        assert result.status == "ok"

    def test_async_check_site(self):
        mock_response = MagicMock()
        mock_response.getcode.return_value = 200
        config = MonitorConfig(uptime_enabled=True, ssl_enabled=False, performance_enabled=False)
        with patch("urllib.request.urlopen", return_value=mock_response):
            results = asyncio.run(async_check_site("https://example.com", config))
        assert "uptime" in results

    def test_async_check_content_change(self):
        result = asyncio.run(async_check_content_change("https://example.com", content="test"))
        assert isinstance(result, ContentChangeResult)
        assert result.changed is False

    def test_async_check_keyword_ranking(self):
        result = asyncio.run(async_check_keyword_ranking("wordpress", "https://example.com"))
        assert isinstance(result, KeywordRankingResult)
        assert result.keyword == "wordpress"

    def test_async_check_backlinks(self):
        result = asyncio.run(async_check_backlinks("https://example.com"))
        assert isinstance(result, BacklinkResult)
        assert result.backlink_count > 0

    def test_async_check_traffic(self):
        result = asyncio.run(async_check_traffic("https://example.com"))
        assert isinstance(result, TrafficResult)
        assert result.visits > 0

    def test_async_send_webhook_alert(self):
        sender = WebhookAlertSender()
        sender.register_webhook(WebhookType.FEISHU, "https://open.feishu.cn/hook/xxx")
        alert = Alert(
            id="async-alert-1",
            monitor_type=MonitorType.UPTIME,
            level=AlertLevel.CRITICAL,
            target="https://example.com",
            message="down",
        )
        result = asyncio.run(async_send_webhook_alert(WebhookType.FEISHU, alert, sender))
        assert result["success"] is True

    def test_async_monitor_site_full(self):
        mock_response = MagicMock()
        mock_response.getcode.return_value = 200
        with patch("urllib.request.urlopen", return_value=mock_response):
            results = asyncio.run(async_monitor_site_full("https://example.com"))
        assert "uptime" in results
        assert "content_change" in results
        assert "backlinks" in results
        assert "traffic" in results

    def test_async_monitor_site_full_http(self):
        mock_response = MagicMock()
        mock_response.getcode.return_value = 200
        # HTTP站点不应触发SSL检查
        with patch("urllib.request.urlopen", return_value=mock_response):
            results = asyncio.run(async_monitor_site_full("http://example.com"))
        assert "ssl" not in results
        assert "uptime" in results
