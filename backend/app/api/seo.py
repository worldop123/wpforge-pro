"""
API路由 - SEO优化相关接口
"""

from fastapi import APIRouter, HTTPException
from typing import List, Dict, Optional
from pydantic import BaseModel, Field

from app.core.logging import get_logger
from app.services.seo_service import (
    seo_analyzer,
    seo_generator,
    site_speed_optimizer
)

logger = get_logger(__name__)

router = APIRouter(prefix="/api/seo", tags=["SEO优化"])


class SEOScoreRequest(BaseModel):
    """SEO评分请求"""
    html: str
    url: str
    target_keywords: Optional[List[str]] = None


class SEOGenerateRequest(BaseModel):
    """SEO生成请求"""
    content: str
    keywords: List[str]
    language: str = "zh-CN"
    max_title_length: int = 60
    max_description_length: int = 160


class SEOOptimizeRequest(BaseModel):
    """SEO优化请求"""
    content: str
    keywords: List[str]
    language: str = "zh-CN"
    optimization_type: str = "balanced"


class SpeedOptimizeRequest(BaseModel):
    """速度优化请求"""
    site_data: Dict = Field(default_factory=dict)
    optimizations: Optional[List[str]] = None


@router.post("/analyze")
async def analyze_seo(request: SEOScoreRequest):
    """分析页面SEO"""
    try:
        result = seo_analyzer.analyze_html(
            html=request.html,
            url=request.url,
            target_keywords=request.target_keywords
        )
        
        return {
            "url": result.url,
            "overall_score": result.overall_score,
            "content_score": result.content_score,
            "technical_score": result.technical_score,
            "performance_score": result.performance_score,
            "title": result.title,
            "description": result.description,
            "keywords": result.keywords,
            "issues": result.issues,
            "recommendations": result.recommendations,
            "headings": result.headings,
            "images_count": len(result.images),
            "links_count": len(result.links),
            "word_count": result.word_count,
            "keyword_density": result.keyword_density
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"SEO分析失败: {str(e)}")


@router.post("/generate/title")
async def generate_seo_title(request: SEOGenerateRequest):
    """生成SEO标题"""
    try:
        title = await seo_generator.generate_seo_title(
            content=request.content,
            keywords=request.keywords,
            language=request.language,
            max_length=request.max_title_length
        )
        
        return {
            "title": title,
            "length": len(title),
            "max_length": request.max_title_length,
            "keywords": request.keywords
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"标题生成失败: {str(e)}")


@router.post("/generate/description")
async def generate_meta_description(request: SEOGenerateRequest):
    """生成meta描述"""
    try:
        description = await seo_generator.generate_meta_description(
            content=request.content,
            keywords=request.keywords,
            language=request.language,
            max_length=request.max_description_length
        )
        
        return {
            "description": description,
            "length": len(description),
            "max_length": request.max_description_length,
            "keywords": request.keywords
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"描述生成失败: {str(e)}")


@router.post("/optimize/content")
async def optimize_content(request: SEOOptimizeRequest):
    """优化内容SEO"""
    try:
        optimized = await seo_generator.optimize_content(
            content=request.content,
            keywords=request.keywords,
            language=request.language,
            optimization_type=request.optimization_type
        )
        
        return {
            "original": request.content,
            "optimized": optimized,
            "keywords": request.keywords,
            "optimization_type": request.optimization_type
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"内容优化失败: {str(e)}")


@router.get("/speed/suggestions")
async def get_speed_optimization_suggestions():
    """获取速度优化建议"""
    try:
        suggestions = site_speed_optimizer.get_optimization_suggestions({})
        
        return {
            "total": len(suggestions),
            "suggestions": suggestions
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取优化建议失败: {str(e)}")


@router.post("/speed/htaccess")
async def generate_htaccess_rules(request: SpeedOptimizeRequest):
    """生成.htaccess优化规则"""
    try:
        optimizations = request.optimizations or ["gzip", "caching", "compression"]
        rules = site_speed_optimizer.generate_htaccess_rules(optimizations)
        
        return {
            "optimizations": optimizations,
            "rules": rules
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"规则生成失败: {str(e)}")


@router.get("/checklist")
async def get_seo_checklist():
    """获取SEO检查清单"""
    checklist = {
        "on_page": [
            {"item": "标题标签（Title Tag）", "description": "每个页面有唯一的、包含关键词的标题，30-60字符", "priority": "high"},
            {"item": "Meta描述", "description": "每个页面有吸引人的meta描述，70-160字符", "priority": "high"},
            {"item": "H1标题", "description": "每个页面只有一个H1，包含主要关键词", "priority": "high"},
            {"item": "标题层级", "description": "H1-H6层级清晰，不跳级", "priority": "medium"},
            {"item": "图片Alt属性", "description": "所有图片有描述性的alt属性", "priority": "medium"},
            {"item": "内容质量", "description": "内容有价值、全面，至少300字以上", "priority": "high"},
            {"item": "关键词密度", "description": "主要关键词密度1%-2%，自然融入", "priority": "medium"},
            {"item": "内部链接", "description": "有相关的内部链接，锚文本描述性", "priority": "medium"},
            {"item": "外部链接", "description": "有权威的外部链接", "priority": "low"},
            {"item": "URL结构", "description": "URL简洁、包含关键词、静态化", "priority": "high"},
        ],
        "technical": [
            {"item": "页面加载速度", "description": "页面加载时间<3秒，Core Web Vitals达标", "priority": "high"},
            {"item": "移动端友好", "description": "响应式设计，移动端体验良好", "priority": "high"},
            {"item": "HTTPS", "description": "全站启用HTTPS", "priority": "high"},
            {"item": "XML Sitemap", "description": "有XML网站地图并提交给搜索引擎", "priority": "medium"},
            {"item": "robots.txt", "description": "正确配置robots.txt", "priority": "medium"},
            {"item": "Canonical标签", "description": "避免重复内容问题", "priority": "medium"},
            {"item": "结构化数据", "description": "添加Schema.org结构化数据", "priority": "medium"},
            {"item": "404页面", "description": "自定义404页面，有导航链接", "priority": "low"},
            {"item": "面包屑导航", "description": "有面包屑导航，便于用户和搜索引擎", "priority": "low"},
        ],
        "performance": [
            {"item": "图片优化", "description": "图片压缩、WebP格式、懒加载", "priority": "high"},
            {"item": "缓存配置", "description": "页面缓存、浏览器缓存", "priority": "high"},
            {"item": "CDN加速", "description": "使用CDN分发静态资源", "priority": "high"},
            {"item": "GZIP/Brotli压缩", "description": "启用文本资源压缩", "priority": "medium"},
            {"item": "数据库优化", "description": "清理冗余数据，优化查询", "priority": "medium"},
            {"item": "字体优化", "description": "字体预加载、子集化", "priority": "low"},
            {"item": "Heartbeat控制", "description": "控制WordPress Heartbeat频率", "priority": "low"},
            {"item": "修订版本控制", "description": "限制文章修订版本数量", "priority": "low"},
        ]
    }
    
    return checklist
