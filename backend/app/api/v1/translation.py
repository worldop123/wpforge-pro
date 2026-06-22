"""
翻译API - 智能翻译引擎
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas import (
    TranslateRequest,
    TranslateResponse,
    BatchTranslateRequest,
    BatchTranslateResponse,
    SuccessResponse,
)

router = APIRouter(prefix="/translation", tags=["智能翻译"])


@router.post("/translate", response_model=TranslateResponse)
async def translate_text(
    request: TranslateRequest,
    current_user: User = Depends(get_current_user),
):
    """翻译文本"""
    try:
        from app.services.translation_service import translation_service
        
        result = await translation_service.translate(
            text=request.text,
            source_lang=request.source_language,
            target_lang=request.target_language,
            engine=request.engine,
            polish=request.polish,
        )
        
        return TranslateResponse(
            translated_text=result.translated_text,
            source_language=result.source_language,
            target_language=result.target_language,
            engine=result.engine.value,
            quality_score=int(result.quality_score * 100),
            is_polished=result.is_polished,
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"翻译失败: {str(e)}"
        )


@router.post("/batch-translate", response_model=BatchTranslateResponse)
async def batch_translate(
    request: BatchTranslateRequest,
    current_user: User = Depends(get_current_user),
):
    """批量翻译"""
    try:
        from app.services.translation_service import translation_service
        
        results = await translation_service.translate_batch(
            texts=request.texts,
            source_lang=request.source_language,
            target_lang=request.target_language,
            engine=request.engine,
        )
        
        translations = [
            {
                "source": r.source_text,
                "translated": r.translated_text,
                "quality_score": int(r.quality_score * 100),
            }
            for r in results
        ]
        
        return BatchTranslateResponse(
            translations=translations,
            total=len(results),
            success_count=len([r for r in results if r.translated_text]),
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"批量翻译失败: {str(e)}"
        )


@router.get("/engines", response_model=SuccessResponse)
async def get_available_engines(
    current_user: User = Depends(get_current_user),
):
    """获取可用的翻译引擎"""
    try:
        from app.services.translation_service import translation_service
        
        engines = translation_service.get_available_engines()
        
        return SuccessResponse(
            message="获取成功",
            data={
                "engines": engines,
                "default": "ai",
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取失败: {str(e)}"
        )


@router.get("/languages", response_model=SuccessResponse)
async def get_supported_languages(
    current_user: User = Depends(get_current_user),
):
    """获取支持的语言列表"""
    languages = [
        {"code": "auto", "name": "自动检测", "native_name": "Auto Detect"},
        {"code": "zh-CN", "name": "简体中文", "native_name": "简体中文"},
        {"code": "zh-TW", "name": "繁体中文", "native_name": "繁體中文"},
        {"code": "en", "name": "英语", "native_name": "English"},
        {"code": "ja", "name": "日语", "native_name": "日本語"},
        {"code": "ko", "name": "韩语", "native_name": "한국어"},
        {"code": "de", "name": "德语", "native_name": "Deutsch"},
        {"code": "fr", "name": "法语", "native_name": "Français"},
        {"code": "es", "name": "西班牙语", "native_name": "Español"},
        {"code": "it", "name": "意大利语", "native_name": "Italiano"},
        {"code": "pt", "name": "葡萄牙语", "native_name": "Português"},
        {"code": "ru", "name": "俄语", "native_name": "Русский"},
        {"code": "ar", "name": "阿拉伯语", "native_name": "العربية"},
        {"code": "hi", "name": "印地语", "native_name": "हिन्दी"},
        {"code": "th", "name": "泰语", "native_name": "ไทย"},
        {"code": "vi", "name": "越南语", "native_name": "Tiếng Việt"},
        {"code": "id", "name": "印尼语", "native_name": "Bahasa Indonesia"},
        {"code": "ms", "name": "马来语", "native_name": "Bahasa Melayu"},
        {"code": "tr", "name": "土耳其语", "native_name": "Türkçe"},
        {"code": "pl", "name": "波兰语", "native_name": "Polski"},
        {"code": "nl", "name": "荷兰语", "native_name": "Nederlands"},
        {"code": "sv", "name": "瑞典语", "native_name": "Svenska"},
        {"code": "da", "name": "丹麦语", "native_name": "Dansk"},
        {"code": "no", "name": "挪威语", "native_name": "Norsk"},
        {"code": "fi", "name": "芬兰语", "native_name": "Suomi"},
        {"code": "cs", "name": "捷克语", "native_name": "Čeština"},
        {"code": "hu", "name": "匈牙利语", "native_name": "Magyar"},
        {"code": "ro", "name": "罗马尼亚语", "native_name": "Română"},
        {"code": "bg", "name": "保加利亚语", "native_name": "Български"},
        {"code": "uk", "name": "乌克兰语", "native_name": "Українська"},
        {"code": "he", "name": "希伯来语", "native_name": "עברית"},
        {"code": "el", "name": "希腊语", "native_name": "Ελληνικά"},
        {"code": "th", "name": "泰语", "native_name": "ไทย"},
    ]
    
    return SuccessResponse(
        message="获取成功",
        data={"languages": languages}
    )


@router.post("/polish", response_model=TranslateResponse)
async def polish_text(
    text: str,
    language: str = "zh-CN",
    current_user: User = Depends(get_current_user),
):
    """AI润色文本"""
    try:
        from app.services.translation_service import translation_service
        from app.services.translation_service import TranslationResult, TranslationEngine
        
        # 创建一个翻译结果对象用于润色
        result = TranslationResult(
            source_text=text,
            translated_text=text,
            source_language=language,
            target_language=language,
            engine=TranslationEngine.AI,
        )
        
        polished = await translation_service.polish_translation(result)
        
        return TranslateResponse(
            translated_text=polished.translated_text,
            source_language=polished.source_language,
            target_language=polished.target_language,
            engine=polished.engine.value,
            quality_score=int(polished.quality_score * 100),
            is_polished=polished.is_polished,
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"润色失败: {str(e)}"
        )


@router.get("/terms", response_model=SuccessResponse)
async def get_terms(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取术语库"""
    from app.models.translation import TranslationTerm
    
    terms = db.query(TranslationTerm).filter(
        TranslationTerm.user_id == current_user.id,
        TranslationTerm.is_active == True
    ).all()
    
    return SuccessResponse(
        message="获取成功",
        data=[
            {
                "id": t.id,
                "source_term": t.source_term,
                "target_term": t.target_term,
                "source_language": t.source_language,
                "target_language": t.target_language,
                "category": t.category,
                "context": t.context,
            }
            for t in terms
        ]
    )


@router.post("/terms", response_model=SuccessResponse)
async def add_term(
    source_term: str,
    target_term: str,
    source_language: str = "en",
    target_language: str = "zh-CN",
    category: str = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """添加术语"""
    from app.models.translation import TranslationTerm
    
    term = TranslationTerm(
        source_term=source_term,
        target_term=target_term,
        source_language=source_language,
        target_language=target_language,
        category=category,
        user_id=current_user.id,
        is_active=True,
    )
    
    db.add(term)
    db.commit()
    
    return SuccessResponse(message="术语添加成功")
