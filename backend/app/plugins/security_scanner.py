"""
安全扫描插件 - 示例插件
提供站点安全扫描功能，演示插件系统的钩子注册与事件触发
"""
from typing import Dict, Any, List
from app.services.plugin_system import (
    PluginBase,
    PluginInfo,
    PluginConfigField,
    PluginEvent,
    Hooks,
)
from app.core.logging import get_logger

logger = get_logger(__name__)


class SecurityScannerPlugin(PluginBase):
    """安全扫描插件

    功能：
    - 扫描内容中的可疑脚本与敏感信息泄露
    - 注册站点创建/更新钩子，自动触发安全检查
    - 发布安全告警事件
    """

    name = "安全扫描"
    version = "1.0.0"
    description = "扫描站点内容安全，检测XSS、敏感信息泄露等风险"
    author = "WPForge Team"

    # 常见敏感模式
    SUSPICIOUS_PATTERNS = [
        "<script",
        "javascript:",
        "eval(",
        "onerror=",
        "onload=",
        "<iframe",
        "document.cookie",
        "vbscript:",
    ]

    SENSITIVE_KEYWORDS = [
        "password",
        "passwd",
        "secret",
        "api_key",
        "access_token",
        "private_key",
    ]

    def __init__(self, hook_manager):
        super().__init__(hook_manager)
        self.name = "安全扫描"
        self.version = "1.0.0"
        self.description = "扫描站点内容安全，检测XSS、敏感信息泄露等风险"
        self.author = "WPForge Team"
        self.installed = False
        self.enabled = False
        self.scan_count = 0
        self.last_scan_results: List[Dict[str, Any]] = []

    def install(self) -> None:
        """安装钩子"""
        self.installed = True
        logger.info("安全扫描插件已安装")

    def uninstall(self) -> None:
        """卸载钩子"""
        self.installed = False
        self.enabled = False
        self.scan_count = 0
        self.last_scan_results.clear()
        logger.info("安全扫描插件已卸载")

    def enable(self) -> None:
        """启用钩子"""
        self.enabled = True
        logger.info("安全扫描插件已启用")

    def disable(self) -> None:
        """禁用钩子"""
        self.enabled = False
        logger.info("安全扫描插件已禁用")

    def upgrade(self, old_version: str, new_version: str) -> None:
        """升级钩子"""
        logger.info(f"安全扫描插件升级: {old_version} -> {new_version}")

    def register_hooks(self) -> None:
        """注册安全相关钩子"""
        self.hook_manager.add_action(Hooks.SITE_CREATED, self.on_site_created)
        self.hook_manager.add_action(Hooks.SITE_UPDATED, self.on_site_updated)
        self.hook_manager.add_filter(Hooks.THE_CONTENT, self.sanitize_content)

    def on_site_created(self, *args, **kwargs) -> None:
        """站点创建回调：触发安全扫描"""
        if self.enabled and args:
            self.scan_content(args[0] if isinstance(args[0], str) else str(args[0]))

    def on_site_updated(self, *args, **kwargs) -> None:
        """站点更新回调：触发安全扫描"""
        if self.enabled and args:
            self.scan_content(args[0] if isinstance(args[0], str) else str(args[0]))

    def sanitize_content(self, content: str) -> str:
        """过滤内容中的可疑脚本"""
        if not self.enabled:
            return content
        sanitized = content
        for pattern in self.SUSPICIOUS_PATTERNS:
            sanitized = sanitized.replace(pattern, "")
        return sanitized

    def scan_content(self, content: str) -> Dict[str, Any]:
        """扫描内容安全

        Args:
            content: 待扫描内容

        Returns:
            扫描结果
        """
        self.scan_count += 1
        issues: List[Dict[str, Any]] = []
        content_lower = content.lower()

        # 检测XSS风险
        for pattern in self.SUSPICIOUS_PATTERNS:
            if pattern.lower() in content_lower:
                issues.append({
                    "type": "xss",
                    "severity": "high",
                    "pattern": pattern,
                    "message": f"检测到可疑脚本: {pattern}",
                })

        # 检测敏感信息泄露
        for keyword in self.SENSITIVE_KEYWORDS:
            if keyword.lower() in content_lower:
                issues.append({
                    "type": "sensitive_info",
                    "severity": "medium",
                    "pattern": keyword,
                    "message": f"检测到敏感关键词: {keyword}",
                })

        # 计算风险等级
        high_count = sum(1 for i in issues if i["severity"] == "high")
        medium_count = sum(1 for i in issues if i["severity"] == "medium")

        if high_count > 0:
            risk_level = "high"
        elif medium_count > 0:
            risk_level = "medium"
        else:
            risk_level = "low"

        result = {
            "scan_id": self.scan_count,
            "risk_level": risk_level,
            "issues": issues,
            "issue_count": len(issues),
            "content_length": len(content),
            "passed": len(issues) == 0,
        }

        self.last_scan_results.append(result)
        # 保留最近100条
        if len(self.last_scan_results) > 100:
            self.last_scan_results = self.last_scan_results[-100:]

        # 发布安全告警事件（如果有问题）
        if issues:
            self.hook_manager.do_action(Hooks.MONITOR_ALERT, result)

        return result

    def scan_batch(self, contents: List[str]) -> List[Dict[str, Any]]:
        """批量扫描内容

        Args:
            contents: 内容列表

        Returns:
            扫描结果列表
        """
        return [self.scan_content(c) for c in contents]

    def get_scan_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """获取扫描历史

        Args:
            limit: 返回数量上限

        Returns:
            扫描历史列表
        """
        return list(self.last_scan_results[-limit:])

    def get_security_summary(self) -> Dict[str, Any]:
        """获取安全摘要"""
        total = len(self.last_scan_results)
        passed = sum(1 for r in self.last_scan_results if r["passed"])
        high_risk = sum(1 for r in self.last_scan_results if r["risk_level"] == "high")
        return {
            "total_scans": total,
            "passed_scans": passed,
            "failed_scans": total - passed,
            "high_risk_count": high_risk,
            "pass_rate": (passed / total * 100) if total > 0 else 0.0,
        }

    def get_config_schema(self) -> List[PluginConfigField]:
        """获取配置字段定义"""
        return [
            PluginConfigField(
                key="auto_scan",
                label="自动扫描",
                field_type="bool",
                default=True,
                description="站点更新时自动扫描",
            ),
            PluginConfigField(
                key="block_xss",
                label="拦截XSS",
                field_type="bool",
                default=True,
                description="自动过滤内容中的可疑脚本",
            ),
            PluginConfigField(
                key="scan_depth",
                label="扫描深度",
                field_type="select",
                default="standard",
                options=["quick", "standard", "deep"],
                description="扫描深度级别",
            ),
            PluginConfigField(
                key="max_issues",
                label="最大问题数",
                field_type="int",
                default=100,
                min_value=1,
                max_value=1000,
                description="单次扫描最大记录问题数",
            ),
        ]

    def get_info(self) -> PluginInfo:
        """获取插件信息"""
        info = super().get_info()
        info.hooks = [Hooks.SITE_CREATED, Hooks.SITE_UPDATED, Hooks.MONITOR_ALERT]
        info.filters = [Hooks.THE_CONTENT]
        return info
