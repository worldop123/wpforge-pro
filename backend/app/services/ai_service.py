"""
AI模型抽象层 - 统一接口
支持OpenAI、Anthropic、Google Gemini、Ollama本地模型
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Any, Generator
from dataclasses import dataclass, field
import time
import random
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


@dataclass
class ChatMessage:
    """聊天消息"""
    role: str  # system, user, assistant
    content: str
    name: Optional[str] = None


@dataclass
class ChatResponse:
    """聊天响应"""
    content: str
    model: str
    provider: str
    usage: Dict[str, int] = field(default_factory=dict)
    finish_reason: Optional[str] = None
    raw_response: Any = None


@dataclass
class ModelInfo:
    """模型信息"""
    name: str
    provider: str
    max_tokens: int = 4096
    supports_streaming: bool = True
    supports_vision: bool = False
    cost_per_1k_input: float = 0.0
    cost_per_1k_output: float = 0.0


class BaseAIProvider(ABC):
    """AI提供者基类"""
    
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        self.api_key = api_key
        self.base_url = base_url
        self._client = None
    
    @abstractmethod
    def chat_completion(
        self,
        messages: List[ChatMessage],
        model: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stream: bool = False,
        **kwargs
    ) -> ChatResponse:
        """聊天补全"""
        pass
    
    @abstractmethod
    def chat_completion_stream(
        self,
        messages: List[ChatMessage],
        model: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> Generator[str, None, None]:
        """流式聊天补全"""
        pass
    
    @abstractmethod
    def get_available_models(self) -> List[ModelInfo]:
        """获取可用模型列表"""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """检查提供者是否可用"""
        pass


class OpenAIProvider(BaseAIProvider):
    """OpenAI 提供者"""
    
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        super().__init__(
            api_key or settings.OPENAI_API_KEY,
            base_url or settings.OPENAI_BASE_URL
        )
    
    def _get_client(self):
        if self._client is None:
            from openai import OpenAI
            self._client = OpenAI(
                api_key=self.api_key,
                base_url=self.base_url
            )
        return self._client
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(Exception)
    )
    def chat_completion(
        self,
        messages: List[ChatMessage],
        model: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stream: bool = False,
        **kwargs
    ) -> ChatResponse:
        client = self._get_client()
        
        openai_messages = [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]
        
        response = client.chat.completions.create(
            model=model,
            messages=openai_messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=stream,
            **kwargs
        )
        
        if stream:
            # 流式模式需要特殊处理
            full_content = ""
            for chunk in response:
                if chunk.choices[0].delta.content:
                    full_content += chunk.choices[0].delta.content
            
            return ChatResponse(
                content=full_content,
                model=model,
                provider="openai"
            )
        
        return ChatResponse(
            content=response.choices[0].message.content,
            model=model,
            provider="openai",
            usage={
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            },
            finish_reason=response.choices[0].finish_reason,
            raw_response=response
        )
    
    def chat_completion_stream(
        self,
        messages: List[ChatMessage],
        model: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> Generator[str, None, None]:
        client = self._get_client()
        
        openai_messages = [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]
        
        stream = client.chat.completions.create(
            model=model,
            messages=openai_messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True,
            **kwargs
        )
        
        for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
    
    def get_available_models(self) -> List[ModelInfo]:
        return [
            ModelInfo(name="gpt-4o", provider="openai", max_tokens=128000, supports_vision=True, cost_per_1k_input=0.005, cost_per_1k_output=0.015),
            ModelInfo(name="gpt-4o-mini", provider="openai", max_tokens=128000, cost_per_1k_input=0.00015, cost_per_1k_output=0.0006),
            ModelInfo(name="gpt-4-turbo", provider="openai", max_tokens=128000, cost_per_1k_input=0.01, cost_per_1k_output=0.03),
            ModelInfo(name="gpt-3.5-turbo", provider="openai", max_tokens=16385, cost_per_1k_input=0.0005, cost_per_1k_output=0.0015),
        ]
    
    def is_available(self) -> bool:
        return bool(self.api_key)


class AnthropicProvider(BaseAIProvider):
    """Anthropic Claude 提供者"""
    
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        super().__init__(api_key or settings.ANTHROPIC_API_KEY, base_url)
    
    def _get_client(self):
        if self._client is None:
            from anthropic import Anthropic
            self._client = Anthropic(api_key=self.api_key)
        return self._client
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(Exception)
    )
    def chat_completion(
        self,
        messages: List[ChatMessage],
        model: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stream: bool = False,
        **kwargs
    ) -> ChatResponse:
        client = self._get_client()
        
        # 分离system消息
        system_message = ""
        anthropic_messages = []
        for msg in messages:
            if msg.role == "system":
                system_message = msg.content
            else:
                anthropic_messages.append({
                    "role": msg.role,
                    "content": msg.content
                })
        
        response = client.messages.create(
            model=model,
            system=system_message if system_message else None,
            messages=anthropic_messages,
            temperature=temperature,
            max_tokens=max_tokens or 4096,
            stream=stream,
            **kwargs
        )
        
        if stream:
            full_content = ""
            for event in response:
                if event.type == "content_block_delta":
                    full_content += event.delta.text
            return ChatResponse(
                content=full_content,
                model=model,
                provider="anthropic"
            )
        
        content = "".join(block.text for block in response.content)
        
        return ChatResponse(
            content=content,
            model=model,
            provider="anthropic",
            usage={
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens,
                "total_tokens": response.usage.input_tokens + response.usage.output_tokens
            },
            finish_reason=response.stop_reason,
            raw_response=response
        )
    
    def chat_completion_stream(
        self,
        messages: List[ChatMessage],
        model: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> Generator[str, None, None]:
        client = self._get_client()
        
        system_message = ""
        anthropic_messages = []
        for msg in messages:
            if msg.role == "system":
                system_message = msg.content
            else:
                anthropic_messages.append({
                    "role": msg.role,
                    "content": msg.content
                })
        
        with client.messages.stream(
            model=model,
            system=system_message if system_message else None,
            messages=anthropic_messages,
            temperature=temperature,
            max_tokens=max_tokens or 4096,
            **kwargs
        ) as stream:
            for text in stream.text_stream:
                yield text
    
    def get_available_models(self) -> List[ModelInfo]:
        return [
            ModelInfo(name="claude-3-5-sonnet-20240620", provider="anthropic", max_tokens=200000, cost_per_1k_input=0.003, cost_per_1k_output=0.015),
            ModelInfo(name="claude-3-opus-20240229", provider="anthropic", max_tokens=200000, cost_per_1k_input=0.015, cost_per_1k_output=0.075),
            ModelInfo(name="claude-3-haiku-20240307", provider="anthropic", max_tokens=200000, cost_per_1k_input=0.00025, cost_per_1k_output=0.00125),
        ]
    
    def is_available(self) -> bool:
        return bool(self.api_key)


class GoogleGeminiProvider(BaseAIProvider):
    """Google Gemini 提供者"""
    
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        super().__init__(api_key or settings.GOOGLE_API_KEY, base_url)
    
    def _get_client(self):
        if self._client is None:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            self._client = genai
        return self._client
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(Exception)
    )
    def chat_completion(
        self,
        messages: List[ChatMessage],
        model: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stream: bool = False,
        **kwargs
    ) -> ChatResponse:
        genai = self._get_client()
        
        generation_config = {
            "temperature": temperature,
            "max_output_tokens": max_tokens,
        }
        
        # 转换消息格式
        gemini_messages = []
        for msg in messages:
            if msg.role == "system":
                # Gemini不支持system角色，合并到第一条user消息
                continue
            role = "user" if msg.role == "user" else "model"
            gemini_messages.append({
                "role": role,
                "parts": [msg.content]
            })
        
        model_instance = genai.GenerativeModel(model_name=model)
        
        if stream:
            response = model_instance.generate_content(
                gemini_messages,
                generation_config=generation_config,
                stream=True
            )
            full_content = ""
            for chunk in response:
                full_content += chunk.text
            return ChatResponse(
                content=full_content,
                model=model,
                provider="google"
            )
        
        response = model_instance.generate_content(
            gemini_messages,
            generation_config=generation_config
        )
        
        return ChatResponse(
            content=response.text,
            model=model,
            provider="google",
            usage={},
            raw_response=response
        )
    
    def chat_completion_stream(
        self,
        messages: List[ChatMessage],
        model: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> Generator[str, None, None]:
        genai = self._get_client()
        
        generation_config = {
            "temperature": temperature,
            "max_output_tokens": max_tokens,
        }
        
        gemini_messages = []
        for msg in messages:
            if msg.role == "system":
                continue
            role = "user" if msg.role == "user" else "model"
            gemini_messages.append({
                "role": role,
                "parts": [msg.content]
            })
        
        model_instance = genai.GenerativeModel(model_name=model)
        response = model_instance.generate_content(
            gemini_messages,
            generation_config=generation_config,
            stream=True
        )
        
        for chunk in response:
            yield chunk.text
    
    def get_available_models(self) -> List[ModelInfo]:
        return [
            ModelInfo(name="gemini-1.5-pro", provider="google", max_tokens=1048576, supports_vision=True),
            ModelInfo(name="gemini-1.5-flash", provider="google", max_tokens=1048576, supports_vision=True),
            ModelInfo(name="gemini-pro", provider="google", max_tokens=32768),
        ]
    
    def is_available(self) -> bool:
        return bool(self.api_key)


class OllamaProvider(BaseAIProvider):
    """Ollama 本地模型提供者"""
    
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        super().__init__(api_key, base_url or settings.OLLAMA_BASE_URL)
    
    def _get_client(self):
        if self._client is None:
            import httpx
            self._client = httpx.Client(base_url=self.base_url, timeout=300.0)
        return self._client
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(Exception)
    )
    def chat_completion(
        self,
        messages: List[ChatMessage],
        model: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stream: bool = False,
        **kwargs
    ) -> ChatResponse:
        client = self._get_client()
        
        ollama_messages = [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]
        
        response = client.post(
            "/api/chat",
            json={
                "model": model,
                "messages": ollama_messages,
                "stream": stream,
                "options": {
                    "temperature": temperature,
                    "num_predict": max_tokens,
                }
            }
        )
        response.raise_for_status()
        
        if stream:
            full_content = ""
            for line in response.iter_lines():
                if line:
                    import json
                    data = json.loads(line)
                    if "message" in data and "content" in data["message"]:
                        full_content += data["message"]["content"]
            return ChatResponse(
                content=full_content,
                model=model,
                provider="ollama"
            )
        
        data = response.json()
        
        return ChatResponse(
            content=data["message"]["content"],
            model=model,
            provider="ollama",
            usage={
                "prompt_eval_count": data.get("prompt_eval_count", 0),
                "eval_count": data.get("eval_count", 0),
            },
            raw_response=data
        )
    
    def chat_completion_stream(
        self,
        messages: List[ChatMessage],
        model: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> Generator[str, None, None]:
        import httpx
        
        with httpx.stream(
            "POST",
            f"{self.base_url}/api/chat",
            json={
                "model": model,
                "messages": [{"role": msg.role, "content": msg.content} for msg in messages],
                "stream": True,
                "options": {
                    "temperature": temperature,
                    "num_predict": max_tokens,
                }
            },
            timeout=300.0
        ) as response:
            import json
            for line in response.iter_lines():
                if line:
                    data = json.loads(line)
                    if "message" in data and "content" in data["message"]:
                        yield data["message"]["content"]
    
    def get_available_models(self) -> List[ModelInfo]:
        try:
            client = self._get_client()
            response = client.get("/api/tags")
            response.raise_for_status()
            data = response.json()
            
            models = []
            for model in data.get("models", []):
                models.append(ModelInfo(
                    name=model["name"],
                    provider="ollama",
                    max_tokens=4096,  # 默认值
                    supports_streaming=True
                ))
            return models
        except Exception:
            return [
                ModelInfo(name="llama3", provider="ollama", max_tokens=8192),
                ModelInfo(name="mistral", provider="ollama", max_tokens=8192),
                ModelInfo(name="codellama", provider="ollama", max_tokens=16384),
            ]
    
    def is_available(self) -> bool:
        try:
            client = self._get_client()
            response = client.get("/api/tags", timeout=5.0)
            return response.status_code == 200
        except Exception:
            return False


class AIManager:
    """AI管理器 - 统一接口、Key池轮换、自动降级"""
    
    def __init__(self):
        self.providers: Dict[str, BaseAIProvider] = {}
        self.api_key_pools: Dict[str, List[str]] = {}
        self.current_key_index: Dict[str, int] = {}
        self.fallback_chain: List[str] = []
        self._init_providers()
    
    def _init_providers(self):
        """初始化提供者"""
        # 注册所有提供者
        self.providers["openai"] = OpenAIProvider()
        self.providers["anthropic"] = AnthropicProvider()
        self.providers["google"] = GoogleGeminiProvider()
        self.providers["ollama"] = OllamaProvider()
        
        # 设置降级链
        self.fallback_chain = ["openai", "anthropic", "google", "ollama"]
    
    def add_api_key(self, provider: str, api_key: str):
        """添加API Key到池"""
        if provider not in self.api_key_pools:
            self.api_key_pools[provider] = []
            self.current_key_index[provider] = 0
        self.api_key_pools[provider].append(api_key)
    
    def get_next_api_key(self, provider: str) -> Optional[str]:
        """获取下一个API Key（轮询）"""
        keys = self.api_key_pools.get(provider, [])
        if not keys:
            return None
        
        idx = self.current_key_index.get(provider, 0)
        key = keys[idx % len(keys)]
        self.current_key_index[provider] = (idx + 1) % len(keys)
        return key
    
    def get_provider(self, provider_name: str) -> Optional[BaseAIProvider]:
        """获取提供者实例"""
        return self.providers.get(provider_name)
    
    def chat(
        self,
        messages: List[ChatMessage],
        model: Optional[str] = None,
        provider: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stream: bool = False,
        auto_fallback: bool = True,
        **kwargs
    ) -> ChatResponse:
        """统一聊天接口，支持自动降级"""
        provider = provider or settings.DEFAULT_AI_PROVIDER
        model = model or settings.DEFAULT_AI_MODEL
        
        providers_to_try = [provider]
        if auto_fallback:
            # 添加降级链中的其他提供者
            for p in self.fallback_chain:
                if p not in providers_to_try:
                    providers_to_try.append(p)
        
        last_error = None
        for prov in providers_to_try:
            provider_instance = self.get_provider(prov)
            if not provider_instance or not provider_instance.is_available():
                continue
            
            try:
                # 如果有key池，轮换key
                if self.api_key_pools.get(prov):
                    api_key = self.get_next_api_key(prov)
                    if api_key:
                        provider_instance.api_key = api_key
                
                response = provider_instance.chat_completion(
                    messages=messages,
                    model=model,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    stream=stream,
                    **kwargs
                )
                logger.info(f"AI chat completed with provider: {prov}, model: {model}")
                return response
                
            except Exception as e:
                last_error = e
                logger.warning(f"Provider {prov} failed: {e}, trying fallback...")
                continue
        
        raise Exception(f"All AI providers failed. Last error: {last_error}")
    
    def chat_stream(
        self,
        messages: List[ChatMessage],
        model: Optional[str] = None,
        provider: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> Generator[str, None, None]:
        """流式聊天接口"""
        provider = provider or settings.DEFAULT_AI_PROVIDER
        model = model or settings.DEFAULT_AI_MODEL
        
        provider_instance = self.get_provider(provider)
        if not provider_instance:
            raise ValueError(f"Unknown provider: {provider}")
        
        return provider_instance.chat_completion_stream(
            messages=messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )
    
    def get_available_providers(self) -> List[str]:
        """获取可用的提供者列表"""
        return [name for name, prov in self.providers.items() if prov.is_available()]
    
    def get_all_models(self) -> List[ModelInfo]:
        """获取所有可用模型"""
        all_models = []
        for name, provider in self.providers.items():
            if provider.is_available():
                all_models.extend(provider.get_available_models())
        return all_models
    
    def get_provider_models(self, provider_name: str) -> List[ModelInfo]:
        """获取指定提供者的模型"""
        provider = self.get_provider(provider_name)
        if provider:
            return provider.get_available_models()
        return []


# 全局AI管理器实例
ai_manager = AIManager()


# 便捷函数
def ai_chat(
    prompt: str,
    system_prompt: Optional[str] = None,
    model: Optional[str] = None,
    provider: Optional[str] = None,
    temperature: float = 0.7,
    max_tokens: Optional[int] = None,
    **kwargs
) -> str:
    """便捷的AI聊天函数"""
    messages = []
    if system_prompt:
        messages.append(ChatMessage(role="system", content=system_prompt))
    messages.append(ChatMessage(role="user", content=prompt))
    
    response = ai_manager.chat(
        messages=messages,
        model=model,
        provider=provider,
        temperature=temperature,
        max_tokens=max_tokens,
        **kwargs
    )
    return response.content
