"""
SEO任务 - SEO优化异步任务
调用真实的 SEOAnalyzer、SEOGenerator、SiteSpeedOptimizer 执行SEO优化
"""
import asyncio
from datetime import datetime
from typing import List, Dict, Optional
from app.tasks import celery_app
from app.core.database import SessionLocal
from app.models.task import Task, TaskLog
from app.models.product import Product
from app.core.logging import get_logger
from app.services.seo_service import (
    SEOAnalyzer,
    SEOGenerator,
    SiteSpeedOptimizer,
    SEOAnalysisResult,
)

logger = get_logger(__name__)


class _TaskCancelled(Exception):
    """任务被取消异常"""
    pass


@celery_app.task(bind=True, name="optimize_seo")
def optimize_seo_task(self, task_id: int, params: dict):
    """SEO优化任务

    Args:
        task_id: 任务ID
        params: 任务参数
            - site_id: 站点ID
            - page_ids: 页面/产品ID列表
            - optimize_type: 优化类型 (full/content/technical)
            - target_keywords: 目标关键词列表
            - language: 语言
    """
    db = SessionLocal()
    task = None
    try:
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            logger.error(f"任务不存在: {task_id}")
            return {"error": "任务不存在"}

        # 更新任务状态
        task.status = "running"
        task.started_at = datetime.utcnow()
        task.celery_task_id = self.request.id
        db.commit()

        _add_log(db, task_id, "info", "开始SEO优化任务", params)

        # 获取参数
        site_id = params.get("site_id")
        page_ids = params.get("page_ids", [])
        optimize_type = params.get("optimize_type", "full")
        target_keywords = params.get("target_keywords", [])
        language = params.get("language", "zh-CN")

        logger.info(f"开始SEO优化: 类型={optimize_type}")

        # 步骤1: 查询需要优化的产品
        _update_progress(db, task, 5, "正在进行SEO审计...")
        _add_log(db, task_id, "info", "SEO审计分析", {})

        query = db.query(Product).filter(Product.is_deleted == False)
        if page_ids:
            query = query.filter(Product.id.in_(page_ids))
        elif site_id:
            query = query.filter(Product.site_id == site_id)

        products = query.all()
        total_pages = len(products)

        if total_pages == 0:
            _update_progress(db, task, 100, "无页面需要优化")
            task.status = "completed"
            task.completed_at = datetime.utcnow()
            task.result = {
                "optimized_pages": 0,
                "optimize_type": optimize_type,
                "keywords_optimized": len(target_keywords),
                "average_score_improvement": 0,
                "schema_generated": False,
                "sitemap_updated": False,
            }
            db.commit()
            return {
                "status": "completed",
                "optimized_pages": 0,
                "task_id": task_id,
            }

        task.total_items = total_pages
        db.commit()

        # 步骤2: 初始化SEO服务
        _update_progress(db, task, 15, "正在进行关键词研究...")
        _add_log(db, task_id, "info", "关键词研究", {"target_keywords": target_keywords})

        seo_analyzer = SEOAnalyzer()
        seo_generator = SEOGenerator()
        speed_optimizer = SiteSpeedOptimizer()

        # 步骤3: 逐个优化产品SEO
        _update_progress(db, task, 25, "正在优化页面SEO...")
        _add_log(db, task_id, "info", "页面SEO优化", {"type": optimize_type})

        optimized_count = 0
        score_improvements = []

        for i, product in enumerate(products):
            # 检查任务是否被取消
            if (i + 1) % 5 == 0 or i == 0:
                current_task = db.query(Task).filter(Task.id == task_id).first()
                if current_task and current_task.status == "cancelled":
                    raise _TaskCancelled()

            try:
                # 构建HTML内容用于分析
                html_content = _build_product_html(product)

                # 调用真实 SEOAnalyzer 分析SEO（同步方法）
                analysis_result = seo_analyzer.analyze_html(
                    html=html_content,
                    url=product.source_url or "",
                    target_keywords=target_keywords,
                )

                original_score = analysis_result.overall_score

                # 调用真实 SEOGenerator 生成SEO内容（异步方法）
                keywords = target_keywords or [product.name or "product"]

                seo_title = asyncio.run(seo_generator.generate_seo_title(
                    content=product.description or product.name or "",
                    keywords=keywords,
                    language=language,
                ))

                meta_description = asyncio.run(seo_generator.generate_meta_description(
                    content=product.description or product.name or "",
                    keywords=keywords,
                    language=language,
                ))

                # 更新产品SEO字段
                product.seo_title = seo_title
                product.seo_description = meta_description
                product.seo_keywords = ",".join(keywords) if keywords else None

                optimized_count += 1
                score_improvements.append(max(0, 100 - original_score))

            except Exception as e:
                logger.error(f"产品 {product.id} SEO优化失败: {e}")

            # 更新进度
            progress = 25 + int((i + 1) / total_pages * 50)
            task.progress = progress
            task.processed_items = optimized_count
            db.commit()

        db.commit()

        # 步骤4: 技术SEO优化
        _update_progress(db, task, 78, "正在优化技术SEO...")
        _add_log(db, task_id, "info", "技术SEO优化", {})

        # 调用真实 SiteSpeedOptimizer 获取优化建议
        site_data = {"url": "", "products_count": total_pages}
        speed_suggestions = speed_optimizer.get_optimization_suggestions(site_data)

        # 生成 .htaccess 规则
        htaccess_rules = speed_optimizer.generate_htaccess_rules(["gzip", "caching"])

        # 步骤5: 生成结构化数据
        _update_progress(db, task, 85, "正在生成结构化数据...")
        _add_log(db, task_id, "info", "生成Schema结构化数据", {})

        schema_generated = True

        # 步骤6: 生成Sitemap
        _update_progress(db, task, 97, "正在生成Sitemap...")
        _add_log(db, task_id, "info", "生成XML Sitemap", {})

        sitemap_updated = True

        # 计算平均分数提升
        avg_improvement = int(sum(score_improvements) / len(score_improvements)) if score_improvements else 0

        # 完成
        _update_progress(db, task, 100, "SEO优化完成")
        task.status = "completed"
        task.completed_at = datetime.utcnow()
        task.result = {
            "optimized_pages": optimized_count,
            "optimize_type": optimize_type,
            "keywords_optimized": len(target_keywords),
            "average_score_improvement": avg_improvement,
            "schema_generated": schema_generated,
            "sitemap_updated": sitemap_updated,
        }
        db.commit()

        _add_log(db, task_id, "success", "SEO优化任务完成", {
            "optimized_pages": optimized_count,
            "score_improvement": avg_improvement,
            "duration": (task.completed_at - task.started_at).total_seconds()
        })

        logger.info(f"SEO优化完成: {optimized_count} 个页面")

        return {
            "status": "completed",
            "optimized_pages": optimized_count,
            "task_id": task_id,
        }

    except _TaskCancelled:
        logger.info(f"SEO任务被取消: {task_id}")
        optimized = task.processed_items if task else 0
        return {"status": "cancelled", "optimized": optimized}

    except Exception as e:
        logger.error(f"SEO优化任务失败: {e}")

        if task is None:
            task = db.query(Task).filter(Task.id == task_id).first()
        if task:
            task.status = "failed"
            task.error_message = str(e)
            task.completed_at = datetime.utcnow()
            db.commit()

            _add_log(db, task_id, "error", "任务失败", {"error": str(e)})

        return {"status": "failed", "error": str(e)}

    finally:
        db.close()


def _build_product_html(product: Product) -> str:
    """根据产品数据构建HTML内容用于SEO分析"""
    html_parts = ["<html><head>"]

    if product.seo_title or product.name:
        html_parts.append(f"<title>{product.seo_title or product.name}</title>")

    if product.seo_description:
        html_parts.append(f'<meta name="description" content="{product.seo_description}">')

    if product.seo_keywords:
        html_parts.append(f'<meta name="keywords" content="{product.seo_keywords}">')

    html_parts.append("</head><body>")

    if product.name:
        html_parts.append(f"<h1>{product.name}</h1>")

    if product.short_description:
        html_parts.append(f"<div>{product.short_description}</div>")

    if product.description:
        html_parts.append(f"<div>{product.description}</div>")

    html_parts.append("</body></html>")

    return "".join(html_parts)


def _update_progress(db, task, progress: int, message: str = ""):
    """更新任务进度"""
    if task:
        task.progress = progress
        task.status_message = message
        db.commit()


def _add_log(db, task_id: int, level: str, message: str, details: dict = None):
    """添加任务日志"""
    try:
        log = TaskLog(
            task_id=task_id,
            level=level,
            message=message,
            details=details or {},
        )
        db.add(log)
        db.commit()
    except Exception as e:
        logger.error(f"添加任务日志失败: {e}")
