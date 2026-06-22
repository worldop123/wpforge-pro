"""
SEO增强插件 - 示例插件
提供SEO分析与优化建议功能，演示插件系统的完整生命周期与事件机制
"""
from typing import Dict, Any, List
from app.services.plugin_system import (
    PluginBase,
    PluginInfo,
    PluginConfigField,
    PluginConfigManager,
    Hooks,
)
from app.core.logging import get_logger

logger = get_logger(__name__)


class SEOEnhancerPlugin(PluginBase):
    """SEO增强插件

    功能：
    - 注册内容过滤钩子，自动优化页面标题与描述
    - 提供 SEO 评分接口
    - 演示插件配置管理
    """

    name = "SEO增强"
    version = "1.0.0"
    description = "提供SEO分析与自动优化建议，增强站点搜索引擎表现"
    author = "WPForge Team"

    def __init__(self, hook_manager):
        super().__init__(hook_manager)
        self.name = "SEO增强"
        self.version = "1.0.0"
        self.description = "提供SEO分析与自动优化建议，增强站点搜索引擎表现"
        self.author = "WPForge Team"
        self.installed = False
        self.enabled = False
        self.optimized_count = 0
        self._config_manager: PluginConfigManager = None

    def install(self) -> None:
        """安装钩子：初始化插件"""
        self.installed = True
        logger.info("SEO增强插件已安装")

    def uninstall(self) -> None:
        """卸载钩子：清理插件数据"""
        self.installed = False
        self.enabled = False
        self.optimized_count = 0
        logger.info("SEO增强插件已卸载")

    def enable(self) -> None:
        """启用钩子"""
        self.enabled = True
        logger.info("SEO增强插件已启用")

    def disable(self) -> None:
        """禁用钩子"""
        self.enabled = False
        logger.info("SEO增强插件已禁用")

    def upgrade(self, old_version: str, new_version: str) -> None:
        """升级钩子"""
        logger.info(f"SEO增强插件升级: {old_version} -> {new_version}")

    def register_hooks(self) -> None:
        """注册SEO相关钩子"""
        self.hook_manager.add_filter(Hooks.THE_TITLE, self.optimize_title)
        self.hook_manager.add_filter(Hooks.THE_CONTENT, self.optimize_content)
        self.hook_manager.add_action(Hooks.SEO_OPTIMIZED, self.on_seo_optimized)

    def optimize_title(self, title: str) -> str:
        """优化标题：确保长度适中"""
        if not self.enabled:
            return title
        if len(title) > 60:
            return title[:57] + "..."
        return title

    def optimize_content(self, content: str) -> str:
        """优化内容：添加基本SEO元素"""
        if not self.enabled:
            return content
        # 简单示例：移除多余空行
        lines = [line.strip() for line in content.split("\n") if line.strip()]
        return "\n".join(lines)

    def on_seo_optimized(self, *args, **kwargs) -> None:
        """SEO优化完成回调"""
        self.optimized_count += 1

    def get_seo_score(self, content: str, title: str, meta_description: str = "") -> Dict[str, Any]:
        """计算SEO评分

        Args:
            content: 页面内容
            title: 页面标题
            meta_description: 元描述

        Returns:
            评分详情
        """
        score = 0
        checks: List[Dict[str, Any]] = []

        # 标题长度检查
        title_len = len(title)
        if 30 <= title_len <= 60:
            score += 20
            checks.append({"item": "标题长度", "status": "ok", "message": f"标题长度合适 ({title_len}字符)"})
        else:
            checks.append({"item": "标题长度", "status": "warning", "message": f"标题长度不理想 ({title_len}字符)"})

        # 内容长度检查
        content_len = len(content)
        if content_len >= 300:
            score += 30
            checks.append({"item": "内容长度", "status": "ok", "message": f"内容充足 ({content_len}字符)"})
        else:
            checks.append({"item": "内容长度", "status": "warning", "message": f"内容过少 ({content_len}字符)"})

        # 元描述检查
        if meta_description:
            if 70 <= len(meta_description) <= 160:
                score += 25
                checks.append({"item": "元描述", "status": "ok", "message": "元描述长度合适"})
            else:
                score += 10
                checks.append({"item": "元描述", "status": "warning", "message": "元描述长度不理想"})
        else:
            checks.append({"item": "元描述", "status": "error", "message": "缺少元描述"})

        # 关键词密度（简化）
        if content_len > 0 and title:
            keyword_in_content = title.split()[0].lower() in content.lower() if title.split() else False
            if keyword_in_content:
                score += 25
                checks.append({"item": "关键词出现", "status": "ok", "message": "标题关键词出现在内容中"})
            else:
                checks.append({"item": "关键词出现", "status": "warning", "message": "标题关键词未出现在内容中"})

        return {
            "score": min(score, 100),
            "checks": checks,
            "level": "优秀" if score >= 80 else ("良好" if score >= 60 else "需改进"),
        }

    def get_config_schema(self) -> List[PluginConfigField]:
        """获取配置字段定义"""
        return [
            PluginConfigField(
                key="auto_optimize",
                label="自动优化",
                field_type="bool",
                default=True,
                description="是否自动优化标题与内容",
            ),
            PluginConfigField(
                key="max_title_length",
                label="标题最大长度",
                field_type="int",
                default=60,
                min_value=10,
                max_value=120,
                description="标题最大字符数",
            ),
            PluginConfigField(
                key="min_content_length",
                label="内容最小长度",
                field_type="int",
                default=300,
                min_value=50,
                description="内容最小字符数",
            ),
            PluginConfigField(
                key="optimization_level",
                label="优化级别",
                field_type="select",
                default="standard",
                options=["basic", "standard", "aggressive"],
                description="SEO优化级别",
            ),
        ]

    def get_info(self) -> PluginInfo:
        """获取插件信息"""
        info = super().get_info()
        info.hooks = [Hooks.THE_TITLE, Hooks.THE_CONTENT]
        info.filters = [Hooks.THE_TITLE, Hooks.THE_CONTENT]
        return info
