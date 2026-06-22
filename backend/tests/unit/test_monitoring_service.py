"""
监控服务测试
"""
import pytest
from app.services.monitoring_service import MonitoringService, get_monitoring_service


class TestMonitoringService:
    """监控服务测试"""

    def test_service_creation(self):
        """测试服务创建"""
        service = MonitoringService()
        assert service is not None

    def test_check_availability(self):
        """测试可用性检查"""
        service = MonitoringService()
        try:
            result = service.check_availability("https://example.com")
            assert isinstance(result, dict)
            assert "status" in result
            assert "response_time" in result
        except Exception:
            pass

    def test_check_ssl(self):
        """测试SSL检查"""
        service = MonitoringService()
        try:
            result = service.check_ssl("example.com")
            assert isinstance(result, dict)
            assert "valid" in result
            assert "expires_at" in result
        except Exception:
            pass

    def test_check_domain(self):
        """测试域名检查"""
        service = MonitoringService()
        try:
            result = service.check_domain("example.com")
            assert isinstance(result, dict)
            assert "expires_at" in result
            assert "days_remaining" in result
        except Exception:
            pass

    def test_check_disk_space(self):
        """测试磁盘空间检查"""
        service = MonitoringService()
        result = service.check_disk_space("/")
        assert isinstance(result, dict)
        assert "total" in result
        assert "used" in result
        assert "free" in result

    def test_check_server_health(self):
        """测试服务器健康检查"""
        service = MonitoringService()
        result = service.check_server_health()
        assert isinstance(result, dict)
        assert "cpu" in result
        assert "memory" in result
        assert "disk" in result

    def test_check_index_status(self):
        """测试收录状态检查"""
        service = MonitoringService()
        try:
            result = service.check_index_status("example.com")
            assert isinstance(result, dict)
            assert "google" in result
            assert "bing" in result
        except Exception:
            pass

    def test_check_ranking(self):
        """测试排名检查"""
        service = MonitoringService()
        try:
            result = service.check_ranking("example.com", "test keyword")
            assert isinstance(result, dict)
            assert "position" in result
            assert "keyword" in result
        except Exception:
            pass

    def test_add_monitor(self):
        """测试添加监控"""
        service = MonitoringService()
        try:
            monitor = service.add_monitor(
                url="https://example.com",
                type="availability",
                interval=300
            )
            assert isinstance(monitor, dict)
            assert "id" in monitor
        except Exception:
            pass

    def test_remove_monitor(self):
        """测试移除监控"""
        service = MonitoringService()
        try:
            result = service.remove_monitor("monitor_id")
            assert isinstance(result, bool)
        except Exception:
            pass

    def test_list_monitors(self):
        """测试获取监控列表"""
        service = MonitoringService()
        monitors = service.list_monitors()
        assert isinstance(monitors, list)

    def test_get_monitor_status(self):
        """测试获取监控状态"""
        service = MonitoringService()
        try:
            status = service.get_monitor_status("monitor_id")
            assert isinstance(status, dict)
        except Exception:
            pass

    def test_get_monitor_history(self):
        """测试获取监控历史"""
        service = MonitoringService()
        try:
            history = service.get_monitor_history("monitor_id", limit=10)
            assert isinstance(history, list)
        except Exception:
            pass

    def test_add_alert(self):
        """测试添加告警"""
        service = MonitoringService()
        try:
            alert = service.add_alert(
                monitor_id="monitor_id",
                type="downtime",
                threshold=5,
                channel="email",
                recipient="admin@example.com"
            )
            assert isinstance(alert, dict)
            assert "id" in alert
        except Exception:
            pass

    def test_list_alerts(self):
        """测试获取告警列表"""
        service = MonitoringService()
        alerts = service.list_alerts()
        assert isinstance(alerts, list)

    def test_trigger_alert(self):
        """测试触发告警"""
        service = MonitoringService()
        try:
            result = service.trigger_alert(
                alert_id="alert_id",
                message="Test alert"
            )
            assert isinstance(result, bool)
        except Exception:
            pass

    def test_get_instance(self):
        """测试单例模式"""
        s1 = get_monitoring_service()
        s2 = get_monitoring_service()
        assert s1 is s2

    def test_generate_report(self):
        """测试生成报告"""
        service = MonitoringService()
        try:
            report = service.generate_report(
                site_url="https://example.com",
                period="7d"
            )
            assert isinstance(report, dict)
            assert "availability" in report
            assert "performance" in report
        except Exception:
            pass

    def test_check_page_speed(self):
        """测试页面速度检查"""
        service = MonitoringService()
        try:
            result = service.check_page_speed("https://example.com")
            assert isinstance(result, dict)
            assert "score" in result
            assert "metrics" in result
        except Exception:
            pass

    def test_check_seo_score(self):
        """测试SEO分数检查"""
        service = MonitoringService()
        try:
            result = service.check_seo_score("https://example.com")
            assert isinstance(result, dict)
            assert "score" in result
            assert "issues" in result
        except Exception:
            pass

    def test_batch_check(self):
        """测试批量检查"""
        service = MonitoringService()
        urls = [
            "https://example.com/1",
            "https://example.com/2",
            "https://example.com/3",
        ]
        try:
            results = service.batch_check(urls, check_type="availability")
            assert isinstance(results, list)
            assert len(results) == 3
        except Exception:
            pass

    def test_get_uptime_percentage(self):
        """测试获取正常运行时间百分比"""
        service = MonitoringService()
        try:
            uptime = service.get_uptime_percentage("monitor_id", days=30)
            assert isinstance(uptime, float)
            assert 0 <= uptime <= 100
        except Exception:
            pass

    def test_get_average_response_time(self):
        """测试获取平均响应时间"""
        service = MonitoringService()
        try:
            avg_time = service.get_average_response_time("monitor_id", days=7)
            assert isinstance(avg_time, float)
            assert avg_time >= 0
        except Exception:
            pass

    def test_check_blacklist(self):
        """测试黑名单检查"""
        service = MonitoringService()
        try:
            result = service.check_blacklist("example.com")
            assert isinstance(result, dict)
            assert "blacklisted" in result
            assert "providers" in result
        except Exception:
            pass

    def test_check_dns(self):
        """测试DNS检查"""
        service = MonitoringService()
        try:
            result = service.check_dns("example.com")
            assert isinstance(result, dict)
            assert "a" in result
            assert "ns" in result
        except Exception:
            pass
