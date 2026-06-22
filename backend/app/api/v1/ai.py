"""
AI API - AI决策与智能分析
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas import (
    AIChatRequest,
    AIChatResponse,
    AISiteAnalyzeRequest,
    AISiteAnalyzeResponse,
    SuccessResponse,
)

router = APIRouter(prefix="/ai", tags=["AI智能"])


@router.post("/chat", response_model=AIChatResponse)
async def ai_chat(
    request: AIChatRequest,
    current_user: User = Depends(get_current_user),
):
    """AI对话"""
    try:
        from app.services.ai_service import ai_manager, ChatMessage
        
        messages = [
            ChatMessage(role="system", content="你是WPForge的AI助手，帮助用户进行WordPress建站、产品采集、翻译、SEO优化等工作。"),
        ]
        
        # 添加历史消息
        if request.history:
            for msg in request.history:
                messages.append(ChatMessage(role=msg["role"], content=msg["content"]))
        
        # 添加当前消息
        messages.append(ChatMessage(role="user", content=request.message))
        
        response = ai_manager.chat(
            messages=messages,
            model=request.model,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
        )
        
        return AIChatResponse(
            response=response.content,
            model=response.model,
            usage=response.usage,
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI对话失败: {str(e)}"
        )


@router.post("/analyze-site", response_model=SuccessResponse)
async def ai_analyze_site(
    request: AISiteAnalyzeRequest,
    current_user: User = Depends(get_current_user),
):
    """AI分析网站"""
    try:
        from app.services.ai_scraper_service import AIScraperAnalyzer
        import httpx
        
        # 获取页面HTML
        async with httpx.AsyncClient(
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"},
            timeout=30,
            follow_redirects=True
        ) as client:
            response = await client.get(str(request.url))
            html = response.text
        
        # AI分析
        analyzer = AIScraperAnalyzer()
        result = analyzer.analyze_site(html, str(request.url))
        
        return SuccessResponse(
            message="网站分析完成",
            data={
                "site_type": result.site_type.value,
                "confidence": result.confidence,
                "pagination_type": result.pagination_type.value,
                "pagination_selector": result.pagination_selector,
                "product_list_selector": result.product_list_selector,
                "product_detail_url_pattern": result.product_detail_url_pattern,
                "currency": result.currency,
                "language": result.language,
                "has_anti_detection": result.has_anti_detection,
                "detected_fields": [
                    {
                        "name": f.name,
                        "selector": f.selector,
                        "confidence": f.confidence,
                        "needs_translation": f.needs_translation,
                    }
                    for f in result.detected_fields
                ],
                "recommendations": result.recommendations,
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"分析失败: {str(e)}"
        )


@router.get("/models", response_model=SuccessResponse)
async def get_available_models(
    current_user: User = Depends(get_current_user),
):
    """获取可用的AI模型"""
    try:
        from app.services.ai_service import ai_manager
        
        models = ai_manager.get_available_models()
        
        return SuccessResponse(
            message="获取成功",
            data={"models": models}
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取失败: {str(e)}"
        )


@router.post("/generate-content", response_model=SuccessResponse)
async def ai_generate_content(
    prompt: str,
    content_type: str = "article",
    language: str = "zh-CN",
    length: str = "medium",
    current_user: User = Depends(get_current_user),
):
    """AI生成内容"""
    try:
        from app.services.ai_service import ai_manager, ChatMessage
        
        length_map = {
            "short": 500,
            "medium": 1000,
            "long": 2000,
        }
        
        max_tokens = length_map.get(length, 1000)
        
        system_prompt = f"""你是一个专业的内容创作者。请根据用户的要求生成高质量的{content_type}内容。
要求：
1. 内容要原创、有价值
2. 结构清晰，逻辑严谨
3. 符合{language}语言的表达习惯
4. 适合SEO优化
5. 只返回内容本身，不要添加任何解释"""
        
        messages = [
            ChatMessage(role="system", content=system_prompt),
            ChatMessage(role="user", content=prompt),
        ]
        
        response = ai_manager.chat(
            messages=messages,
            temperature=0.7,
            max_tokens=max_tokens,
        )
        
        return SuccessResponse(
            message="内容生成成功",
            data={
                "content": response.content,
                "type": content_type,
                "language": language,
                "length": length,
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"生成失败: {str(e)}"
        )


@router.post("/rewrite-content", response_model=SuccessResponse)
async def ai_rewrite_content(
    content: str,
    style: str = "professional",
    language: str = "zh-CN",
    current_user: User = Depends(get_current_user),
):
    """AI改写内容（伪原创）"""
    try:
        from app.services.ai_service import ai_manager, ChatMessage
        
        style_prompts = {
            "professional": "专业、正式的商务风格",
            "casual": "轻松、口语化的风格",
            "creative": "创意、有吸引力的营销风格",
            "academic": "学术、严谨的风格",
            "seo": "SEO优化风格，关键词自然分布",
        }
        
        style_prompt = style_prompts.get(style, style_prompts["professional"])
        
        system_prompt = f"""你是一个专业的内容改写专家。请将用户提供的内容进行改写，使其成为原创内容。
要求：
1. 保持原意不变，但表达方式完全不同
2. {style_prompt}
3. 符合{language}语言的表达习惯
4. 避免AI检测
5. 只返回改写后的内容，不要添加任何解释"""
        
        messages = [
            ChatMessage(role="system", content=system_prompt),
            ChatMessage(role="user", content=content),
        ]
        
        response = ai_manager.chat(
            messages=messages,
            temperature=0.8,
            max_tokens=2000,
        )
        
        return SuccessResponse(
            message="内容改写成功",
            data={
                "original_length": len(content),
                "rewritten_length": len(response.content),
                "rewritten_content": response.content,
                "style": style,
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"改写失败: {str(e)}"
        )


@router.post("/analyze-content", response_model=SuccessResponse)
async def ai_analyze_content(
    content: str,
    analysis_type: str = "quality",
    current_user: User = Depends(get_current_user),
):
    """AI分析内容质量"""
    try:
        from app.services.ai_service import ai_manager, ChatMessage
        
        system_prompt = """你是一个内容质量分析专家。请分析用户提供的内容，从多个维度进行评估。
要求：
1. 评估内容质量、原创性、可读性、SEO友好度
2. 给出具体的改进建议
3. 以JSON格式返回结果，包含以下字段：
   - overall_score: 总体评分（0-100）
   - quality_score: 内容质量评分
   - originality_score: 原创性评分
   - readability_score: 可读性评分
   - seo_score: SEO友好度评分
   - strengths: 优点列表
   - weaknesses: 缺点列表
   - suggestions: 改进建议列表
4. 只返回JSON，不要添加任何解释"""
        
        messages = [
            ChatMessage(role="system", content=system_prompt),
            ChatMessage(role="user", content=content),
        ]
        
        response = ai_manager.chat(
            messages=messages,
            temperature=0.3,
            max_tokens=1000,
        )
        
        # 尝试解析JSON
        import json
        try:
            result = json.loads(response.content)
        except json.JSONDecodeError:
            # 如果解析失败，返回原始内容
            result = {"raw_response": response.content}
        
        return SuccessResponse(
            message="内容分析完成",
            data=result
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"分析失败: {str(e)}"
        )


@router.get("/providers", response_model=SuccessResponse)
async def get_ai_providers(
    current_user: User = Depends(get_current_user),
):
    """获取AI服务提供商列表"""
    providers = [
        {
            "id": "openai",
            "name": "OpenAI",
            "description": "GPT-4、GPT-3.5等模型",
            "models": ["gpt-4", "gpt-4-turbo", "gpt-3.5-turbo"],
            "status": "available",
        },
        {
            "id": "anthropic",
            "name": "Anthropic",
            "description": "Claude系列模型",
            "models": ["claude-3-opus", "claude-3-sonnet", "claude-3-haiku"],
            "status": "available",
        },
        {
            "id": "google",
            "name": "Google Gemini",
            "description": "Gemini系列模型",
            "models": ["gemini-pro", "gemini-ultra"],
            "status": "available",
        },
        {
            "id": "ollama",
            "name": "Ollama (本地)",
            "description": "本地部署的开源模型",
            "models": ["llama2", "mistral", "codellama"],
            "status": "available",
        },
    ]
    
    return SuccessResponse(
        message="获取成功",
        data={"providers": providers}
    )
