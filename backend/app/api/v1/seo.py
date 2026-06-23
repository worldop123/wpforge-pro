"""
SEO API - 全自动SEO优化
"""
from typing import List, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.site import Site
from app.models.task import Task
from app.schemas import (
    SEOAuditRequest,
    SEOAuditResponse,
    SEOOptimizeRequest,
    SuccessResponse,
)

router = APIRouter(prefix="/seo", tags=["SEO优化"])


@router.get("/overview", response_model=SuccessResponse)
async def get_seo_overview(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取SEO概览统计（聚合用户所有站点的SEO数据）"""
    # 获取用户站点
    sites = db.query(Site).filter(
        Site.user_id == current_user.id,
        Site.is_deleted == False
    ).all()

    total_sites = len(sites)

    # 统计 SEO 相关任务，按状态聚合
    seo_task_stats = db.query(
        Task.status,
        func.count(Task.id)
    ).filter(
        Task.user_id == current_user.id,
        Task.task_type == "seo"
    ).group_by(Task.status).all()

    seo_tasks = {"total": 0, "completed": 0, "running": 0, "failed": 0, "pending": 0}
    for st, cnt in seo_task_stats:
        if st in seo_tasks:
            seo_tasks[st] = cnt
        seo_tasks["total"] += cnt

    # 基于已完成的 SEO 任务计算平均分
    completed_seo_tasks = db.query(Task).filter(
        Task.user_id == current_user.id,
        Task.task_type == "seo",
        Task.status == "completed"
    ).all()

    scores = []
    good_pages = 0
    warning_pages = 0
    bad_pages = 0
    for t in completed_seo_tasks:
        result = t.result or {}
        score = result.get("overall_score") if isinstance(result, dict) else None
        if score is not None:
            scores.append(score)
            if score >= 80:
                good_pages += 1
            elif score >= 60:
                warning_pages += 1
            else:
                bad_pages += 1

    avg_score = round(sum(scores) / len(scores)) if scores else 0

    # 收录页面数：从已完成 SEO 任务的 result 中聚合 indexed 字段
    indexed_pages = 0
    for t in completed_seo_tasks:
        result = t.result or {}
        if isinstance(result, dict):
            indexed_pages += result.get("indexed_pages", 0) or 0

    return SuccessResponse(
        message="获取成功",
        data={
            "avgScore": avg_score,
            "goodPages": good_pages,
            "warningPages": warning_pages,
            "badPages": bad_pages,
            "indexedPages": indexed_pages,
            "totalSites": total_sites,
            "seoTasks": seo_tasks,
        }
    )


@router.get("/indexing", response_model=SuccessResponse)
async def get_indexing_data(
    site_id: Optional[int] = Query(None, description="站点ID过滤"),
    limit: int = Query(50, ge=1, le=200, description="返回数量"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取页面收录数据（基于搜索引擎提交服务）"""
    from app.services.search_console_service import (
        search_submission_service,
        SearchEngine,
    )

    # 获取用户站点
    site_query = db.query(Site).filter(
        Site.user_id == current_user.id,
        Site.is_deleted == False
    )
    if site_id:
        site_query = site_query.filter(Site.id == site_id)

    sites = site_query.limit(limit).all()

    # 指定要检查的搜索引擎
    engines = [SearchEngine.GOOGLE, SearchEngine.BING, SearchEngine.BAIDU]

    indexing_rows = []
    for site in sites:
        try:
            # 检查站点首页在各搜索引擎的收录状态
            results = search_submission_service.check_indexing_status(
                url=site.wp_url,
                search_engines=engines,
            )
            row = {
                "url": site.wp_url,
                "site_id": site.id,
                "site_name": site.name,
                "google": False,
                "bing": False,
                "baidu": False,
                "last_check": datetime.now().strftime("%Y-%m-%d %H:%M"),
            }
            for engine, result in results.items():
                if engine == SearchEngine.GOOGLE.value:
                    row["google"] = bool(result.indexed)
                elif engine == SearchEngine.BING.value:
                    row["bing"] = bool(result.indexed)
                elif engine == SearchEngine.BAIDU.value:
                    row["baidu"] = bool(result.indexed)
            indexing_rows.append(row)
        except Exception as e:
            # 单个站点失败不影响整体返回
            indexing_rows.append({
                "url": site.wp_url,
                "site_id": site.id,
                "site_name": site.name,
                "google": False,
                "bing": False,
                "baidu": False,
                "last_check": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "error": str(e),
            })

    return SuccessResponse(
        message="获取成功",
        data={
            "total": len(indexing_rows),
            "items": indexing_rows,
        }
    )


@router.post("/audit", response_model=SuccessResponse)
async def audit_seo(
    request: SEOAuditRequest,
    current_user: User = Depends(get_current_user),
):
    """SEO审计分析"""
    try:
        from app.services.seo_service import SEOAnalyzer
        
        analyzer = SEOAnalyzer()
        
        # 如果提供了HTML，直接分析
        if request.html_content:
            result = analyzer.analyze_html(
                html=request.html_content,
                url=request.url,
                target_keywords=request.target_keywords,
            )
        else:
            # 否则获取页面HTML
            import httpx
            async with httpx.AsyncClient(
                headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"},
                timeout=30,
                follow_redirects=True
            ) as client:
                response = await client.get(request.url)
                html = response.text
            
            result = analyzer.analyze_html(
                html=html,
                url=request.url,
                target_keywords=request.target_keywords,
            )
        
        return SuccessResponse(
            message="SEO审计完成",
            data={
                "url": result.url,
                "overall_score": result.overall_score,
                "content_score": result.content_score,
                "technical_score": result.technical_score,
                "performance_score": result.performance_score,
                "title": result.title,
                "description": result.description,
                "keywords": result.keywords,
                "word_count": result.word_count,
                "keyword_density": result.keyword_density,
                "issues": result.issues,
                "recommendations": result.recommendations,
                "headings_count": len(result.headings),
                "images_count": len(result.images),
                "links_count": len(result.links),
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"SEO审计失败: {str(e)}"
        )


@router.post("/optimize", response_model=SuccessResponse)
async def optimize_seo(
    request: SEOOptimizeRequest,
    current_user: User = Depends(get_current_user),
):
    """SEO内容优化"""
    try:
        from app.services.seo_service import SEOGenerator
        
        generator = SEOGenerator()
        
        results = {}
        
        # 生成优化后的标题
        if request.content and request.target_keywords:
            optimized_title = await generator.generate_seo_title(
                content=request.content,
                keywords=request.target_keywords,
                language=request.language or "zh-CN",
            )
            results["optimized_title"] = optimized_title
        
        # 生成优化后的描述
        if request.content and request.target_keywords:
            optimized_description = await generator.generate_meta_description(
                content=request.content,
                keywords=request.target_keywords,
                language=request.language or "zh-CN",
            )
            results["optimized_description"] = optimized_description
        
        # 生成关键词建议
        if request.content:
            keywords = await generator.suggest_keywords(
                content=request.content,
                language=request.language or "zh-CN",
            )
            results["suggested_keywords"] = keywords
        
        return SuccessResponse(
            message="SEO优化完成",
            data=results
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"SEO优化失败: {str(e)}"
        )


@router.post("/generate-title", response_model=SuccessResponse)
async def generate_seo_title(
    content: str,
    keywords: str,
    language: str = "zh-CN",
    max_length: int = 60,
    current_user: User = Depends(get_current_user),
):
    """生成SEO标题"""
    try:
        from app.services.seo_service import SEOGenerator
        
        generator = SEOGenerator()
        title = await generator.generate_seo_title(
            content=content,
            keywords=keywords.split(","),
            language=language,
            max_length=max_length,
        )
        
        return SuccessResponse(
            message="标题生成成功",
            data={"title": title, "length": len(title)}
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"生成失败: {str(e)}"
        )


@router.post("/generate-description", response_model=SuccessResponse)
async def generate_meta_description(
    content: str,
    keywords: str,
    language: str = "zh-CN",
    max_length: int = 160,
    current_user: User = Depends(get_current_user),
):
    """生成Meta描述"""
    try:
        from app.services.seo_service import SEOGenerator
        
        generator = SEOGenerator()
        description = await generator.generate_meta_description(
            content=content,
            keywords=keywords.split(","),
            language=language,
            max_length=max_length,
        )
        
        return SuccessResponse(
            message="描述生成成功",
            data={"description": description, "length": len(description)}
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"生成失败: {str(e)}"
        )


@router.get("/schema-types", response_model=SuccessResponse)
async def get_schema_types(
    current_user: User = Depends(get_current_user),
):
    """获取支持的Schema类型"""
    schema_types = [
        {"type": "Article", "name": "文章", "description": "新闻文章、博客文章等"},
        {"type": "Product", "name": "产品", "description": "商品产品信息"},
        {"type": "Organization", "name": "组织", "description": "公司、机构等组织信息"},
        {"type": "Person", "name": "人物", "description": "个人信息"},
        {"type": "Place", "name": "地点", "description": "地理位置信息"},
        {"type": "Event", "name": "事件", "description": "活动、事件信息"},
        {"type": "Recipe", "name": "食谱", "description": "烹饪食谱"},
        {"type": "FAQPage", "name": "FAQ页面", "description": "常见问题页面"},
        {"type": "HowTo", "name": "教程", "description": "操作指南、教程"},
        {"type": "BreadcrumbList", "name": "面包屑导航", "description": "面包屑导航结构"},
        {"type": "LocalBusiness", "name": "本地商家", "description": "本地商业信息"},
        {"type": "Service", "name": "服务", "description": "服务信息"},
        {"type": "Review", "name": "评论", "description": "评价、评论"},
        {"type": "AggregateRating", "name": "综合评分", "description": "综合评分信息"},
        {"type": "Offer", "name": "报价", "description": "商品报价信息"},
        {"type": "ImageObject", "name": "图片", "description": "图片信息"},
        {"type": "VideoObject", "name": "视频", "description": "视频信息"},
        {"type": "WebSite", "name": "网站", "description": "网站信息"},
        {"type": "WebPage", "name": "网页", "description": "网页信息"},
        {"type": "SearchAction", "name": "搜索动作", "description": "网站搜索功能"},
    ]
    
    return SuccessResponse(
        message="获取成功",
        data={"schema_types": schema_types}
    )


@router.post("/generate-schema", response_model=SuccessResponse)
async def generate_schema(
    schema_type: str,
    data: dict,
    current_user: User = Depends(get_current_user),
):
    """生成Schema结构化数据"""
    try:
        from app.services.seo_service import SEOGenerator
        
        generator = SEOGenerator()
        schema = await generator.generate_schema_markup(
            schema_type=schema_type,
            data=data,
        )
        
        return SuccessResponse(
            message="Schema生成成功",
            data={"schema": schema}
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"生成失败: {str(e)}"
        )


@router.get("/checklist", response_model=SuccessResponse)
async def get_seo_checklist(
    current_user: User = Depends(get_current_user),
):
    """获取SEO检查清单"""
    checklist = {
        "on_page": [
            {"item": "页面标题（Title）", "importance": "high", "description": "包含关键词，30-60字符"},
            {"item": "Meta描述", "importance": "high", "description": "吸引人，包含关键词，70-160字符"},
            {"item": "H1标题", "importance": "high", "description": "每页一个，包含主关键词"},
            {"item": "标题层级", "importance": "medium", "description": "H1-H6合理使用，不跳级"},
            {"item": "关键词密度", "importance": "medium", "description": "0.5%-2%，自然分布"},
            {"item": "内容长度", "importance": "medium", "description": "建议1000字以上"},
            {"item": "图片ALT属性", "importance": "medium", "description": "所有图片都有描述性ALT"},
            {"item": "内链建设", "importance": "medium", "description": "合理的内部链接结构"},
            {"item": "外链质量", "importance": "high", "description": "高质量的外部链接"},
            {"item": "URL结构", "importance": "medium", "description": "简洁，包含关键词"},
        ],
        "technical": [
            {"item": "页面加载速度", "importance": "high", "description": "Core Web Vitals达标"},
            {"item": "移动端适配", "importance": "high", "description": "响应式设计"},
            {"item": "HTTPS", "importance": "high", "description": "SSL证书配置"},
            {"item": "XML Sitemap", "importance": "medium", "description": "提交到搜索引擎"},
            {"item": "robots.txt", "importance": "medium", "description": "正确配置"},
            {"item": "Canonical标签", "importance": "medium", "description": "避免重复内容"},
            {"item": "结构化数据", "importance": "medium", "description": "Schema标记"},
            {"item": "面包屑导航", "importance": "low", "description": "提升用户体验和SEO"},
            {"item": "404页面", "importance": "low", "description": "友好的错误页面"},
            {"item": "301重定向", "importance": "medium", "description": "正确处理URL变更"},
        ],
        "content": [
            {"item": "原创性", "importance": "high", "description": "高质量原创内容"},
            {"item": "价值性", "importance": "high", "description": "对用户有实际价值"},
            {"item": "时效性", "importance": "medium", "description": "内容及时更新"},
            {"item": "可读性", "importance": "medium", "description": "排版清晰，易于阅读"},
            {"item": "多媒体", "importance": "low", "description": "图片、视频等丰富内容"},
            {"item": "互动性", "importance": "low", "description": "评论、分享等互动功能"},
        ],
    }
    
    return SuccessResponse(
        message="获取成功",
        data=checklist
    )
