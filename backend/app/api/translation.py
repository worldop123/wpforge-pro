"""
API路由 - 翻译相关接口
"""

from fastapi import APIRouter, HTTPException
from typing import List, Dict, Optional
from pydantic import BaseModel, Field

from app.core.logging import get_logger
from app.services.translation_service import translation_service

logger = get_logger(__name__)

router = APIRouter(prefix="/api/translation", tags=["翻译管理"])


class TranslateRequest(BaseModel):
    """翻译请求"""
    text: str
    source_lang: str = "auto"
    target_lang: str = "zh-CN"
    engine: str = "ai"
    use_cache: bool = True
    apply_terms: bool = True
    polish: bool = False


class TranslateBatchRequest(BaseModel):
    """批量翻译请求"""
    texts: List[str]
    source_lang: str = "auto"
    target_lang: str = "zh-CN"
    engine: str = "ai"
    use_cache: bool = True


class TermRequest(BaseModel):
    """术语请求"""
    source_term: str
    target_term: str
    source_lang: str = "en"
    target_lang: str = "zh-CN"


class TermsBatchRequest(BaseModel):
    """批量术语请求"""
    terms: List[Dict[str, str]]  # [{"source": "...", "target": "..."}]
    source_lang: str = "en"
    target_lang: str = "zh-CN"


@router.post("/translate")
async def translate_text(request: TranslateRequest):
    """翻译文本"""
    try:
        result = await translation_service.translate(
            text=request.text,
            source_lang=request.source_lang,
            target_lang=request.target_lang,
            engine=request.engine,
            use_cache=request.use_cache,
            apply_terms=request.apply_terms,
            polish=request.polish
        )
        
        return {
            "source_text": result.source_text,
            "translated_text": result.translated_text,
            "source_language": result.source_language,
            "target_language": result.target_language,
            "engine": result.engine.value,
            "quality_score": result.quality_score,
            "is_polished": result.is_polished,
            "used_terms": result.used_terms,
            "translation_time": result.translation_time
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"翻译失败: {str(e)}")


@router.post("/translate/batch")
async def translate_batch(request: TranslateBatchRequest):
    """批量翻译"""
    try:
        results = await translation_service.translate_batch(
            texts=request.texts,
            source_lang=request.source_lang,
            target_lang=request.target_lang,
            engine=request.engine,
            use_cache=request.use_cache
        )
        
        return {
            "total": len(results),
            "translations": [
                {
                    "source_text": r.source_text,
                    "translated_text": r.translated_text,
                    "quality_score": r.quality_score
                }
                for r in results
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"批量翻译失败: {str(e)}")


@router.get("/engines")
async def get_available_engines():
    """获取可用的翻译引擎"""
    engines = translation_service.get_available_engines()
    return {
        "engines": engines,
        "default": "ai"
    }


@router.post("/terms")
async def add_term(request: TermRequest):
    """添加术语"""
    try:
        translation_service.add_term(
            source_term=request.source_term,
            target_term=request.target_term,
            source_lang=request.source_lang,
            target_lang=request.target_lang
        )
        
        return {
            "success": True,
            "source_term": request.source_term,
            "target_term": request.target_term
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"添加术语失败: {str(e)}")


@router.post("/terms/batch")
async def add_terms_batch(request: TermsBatchRequest):
    """批量添加术语"""
    try:
        terms_list = [(t["source"], t["target"]) for t in request.terms]
        translation_service.add_terms_batch(
            terms=terms_list,
            source_lang=request.source_lang,
            target_lang=request.target_lang
        )
        
        return {
            "success": True,
            "added_count": len(terms_list)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"批量添加术语失败: {str(e)}")


@router.get("/stats")
async def get_translation_stats():
    """获取翻译服务统计"""
    stats = translation_service.get_stats()
    return stats


@router.post("/product")
async def translate_product(
    product: Dict,
    source_lang: str = "auto",
    target_lang: str = "zh-CN",
    engine: str = "ai"
):
    """翻译产品数据"""
    try:
        translated = await translation_service.translate_product(
            product_data=product,
            source_lang=source_lang,
            target_lang=target_lang,
            engine=engine
        )
        
        return {
            "original": product,
            "translated": translated,
            "source_lang": source_lang,
            "target_lang": target_lang
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"产品翻译失败: {str(e)}")
