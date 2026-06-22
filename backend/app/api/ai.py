"""
API路由 - AI配置相关接口
"""

from fastapi import APIRouter, HTTPException
from typing import List, Dict, Optional
from pydantic import BaseModel, Field

from app.core.logging import get_logger
from app.services.ai_service import ai_manager, ChatMessage

logger = get_logger(__name__)

router = APIRouter(prefix="/api/ai", tags=["AI配置"])


class ChatRequest(BaseModel):
    """聊天请求"""
    messages: List[Dict]
    model: Optional[str] = None
    provider: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 2000
    stream: bool = False


class ProviderConfig(BaseModel):
    """提供商配置"""
    name: str
    api_key: str
    base_url: Optional[str] = None
    models: Optional[List[str]] = None


@router.get("/providers")
async def get_ai_providers():
    """获取可用的AI提供商"""
    providers = ai_manager.get_available_providers()
    return {
        "providers": providers,
        "default_provider": ai_manager.default_provider,
        "default_model": ai_manager.default_model
    }


@router.get("/models")
async def get_ai_models(provider: Optional[str] = None):
    """获取可用的AI模型"""
    if provider:
        models = ai_manager.get_models(provider)
    else:
        models = ai_manager.get_all_models()
    
    return {
        "models": models,
        "provider": provider or "all"
    }


@router.post("/providers")
async def add_ai_provider(config: ProviderConfig):
    """添加AI提供商"""
    try:
        from app.services.ai_service import AIProviderConfig
        
        provider_config = AIProviderConfig(
            name=config.name,
            api_key=config.api_key,
            base_url=config.base_url,
            models=config.models or []
        )
        
        ai_manager.add_provider(provider_config)
        
        return {
            "success": True,
            "provider": config.name,
            "models": config.models or []
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"添加提供商失败: {str(e)}")


@router.post("/chat")
async def chat_completion(request: ChatRequest):
    """聊天补全"""
    try:
        messages = [
            ChatMessage(role=m["role"], content=m["content"])
            for m in request.messages
        ]
        
        response = ai_manager.chat(
            messages=messages,
            model=request.model,
            provider=request.provider,
            temperature=request.temperature,
            max_tokens=request.max_tokens
        )
        
        return {
            "role": response.role,
            "content": response.content,
            "model": response.model,
            "provider": response.provider,
            "usage": response.usage,
            "finish_reason": response.finish_reason
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"聊天失败: {str(e)}")


@router.get("/config")
async def get_ai_config():
    """获取AI配置"""
    return {
        "default_provider": ai_manager.default_provider,
        "default_model": ai_manager.default_model,
        "available_providers": ai_manager.get_available_providers(),
        "total_providers": len(ai_manager.providers)
    }


@router.post("/test")
async def test_ai_connection(provider: Optional[str] = None, model: Optional[str] = None):
    """测试AI连接"""
    try:
        messages = [
            ChatMessage(role="system", content="你是一个测试助手。"),
            ChatMessage(role="user", content="请回复'连接成功'")
        ]
        
        response = ai_manager.chat(
            messages=messages,
            model=model,
            provider=provider,
            max_tokens=50
        )
        
        return {
            "success": True,
            "provider": response.provider,
            "model": response.model,
            "response": response.content
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"连接测试失败: {str(e)}")
