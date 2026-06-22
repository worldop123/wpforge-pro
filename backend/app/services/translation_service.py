"""
翻译引擎服务 - 多引擎支持、术语库、AI润色
"""

from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field
import re
import hashlib
import time
from enum import Enum

from app.core.config import settings
from app.core.logging import get_logger
from app.services.ai_service import ai_manager, ChatMessage

logger = get_logger(__name__)


class TranslationEngine(str, Enum):
    """翻译引擎类型"""
    AI = "ai"  # AI翻译（默认）
    GOOGLE = "google"  # Google翻译
    DEEPL = "deepl"  # DeepL翻译
    BAIDU = "baidu"  # 百度翻译
    YOUDAO = "youdao"  # 有道翻译


@dataclass
class TranslationResult:
    """翻译结果"""
    source_text: str
    translated_text: str
    source_language: str
    target_language: str
    engine: TranslationEngine
    model: Optional[str] = None
    quality_score: float = 0.0
    is_polished: bool = False
    used_terms: List[str] = field(default_factory=list)
    translation_time: float = 0.0


class TranslationTermManager:
    """术语库管理器"""
    
    def __init__(self):
        self.terms: Dict[str, Dict[str, str]] = {}  # {source_lang: {source_term: target_term}}
        self._cache = {}
    
    def add_term(self, source_term: str, target_term: str, source_lang: str = "en", target_lang: str = "zh-CN"):
        """添加术语"""
        key = f"{source_lang}_{target_lang}"
        if key not in self.terms:
            self.terms[key] = {}
        self.terms[key][source_term.lower()] = target_term
        self._cache = {}  # 清除缓存
    
    def add_terms_batch(self, terms: List[Tuple[str, str]], source_lang: str = "en", target_lang: str = "zh-CN"):
        """批量添加术语"""
        key = f"{source_lang}_{target_lang}"
        if key not in self.terms:
            self.terms[key] = {}
        for source, target in terms:
            self.terms[key][source.lower()] = target
        self._cache = {}
    
    def apply_terms(self, text: str, source_lang: str = "en", target_lang: str = "zh-CN") -> Tuple[str, List[str]]:
        """应用术语替换
        
        Returns:
            (处理后的文本, 使用的术语列表)
        """
        key = f"{source_lang}_{target_lang}"
        term_dict = self.terms.get(key, {})
        
        if not term_dict:
            return text, []
        
        used_terms = []
        result = text
        
        # 按长度排序，长的先替换
        sorted_terms = sorted(term_dict.keys(), key=len, reverse=True)
        
        for source_term in sorted_terms:
            target_term = term_dict[source_term]
            # 使用正则进行不区分大小写的替换
            pattern = re.compile(re.escape(source_term), re.IGNORECASE)
            if pattern.search(result):
                result = pattern.sub(target_term, result)
                used_terms.append(source_term)
        
        return result, used_terms
    
    def get_terms_count(self, source_lang: str = "en", target_lang: str = "zh-CN") -> int:
        """获取术语数量"""
        key = f"{source_lang}_{target_lang}"
        return len(self.terms.get(key, {}))


class TranslationCache:
    """翻译缓存"""
    
    def __init__(self, max_size: int = 10000):
        self.max_size = max_size
        self.cache: Dict[str, TranslationResult] = {}
        self.access_count: Dict[str, int] = {}
    
    def _get_cache_key(self, text: str, source_lang: str, target_lang: str, engine: str) -> str:
        """生成缓存键"""
        key_str = f"{text.lower()}_{source_lang}_{target_lang}_{engine}"
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def get(self, text: str, source_lang: str, target_lang: str, engine: str) -> Optional[TranslationResult]:
        """获取缓存"""
        key = self._get_cache_key(text, source_lang, target_lang, engine)
        if key in self.cache:
            self.access_count[key] = self.access_count.get(key, 0) + 1
            return self.cache[key]
        return None
    
    def set(self, result: TranslationResult, engine: str):
        """设置缓存"""
        key = self._get_cache_key(
            result.source_text,
            result.source_language,
            result.target_language,
            engine
        )
        
        # 如果缓存满了，删除访问最少的
        if len(self.cache) >= self.max_size:
            min_key = min(self.access_count, key=self.access_count.get)
            del self.cache[min_key]
            del self.access_count[min_key]
        
        self.cache[key] = result
        self.access_count[key] = 1
    
    def clear(self):
        """清空缓存"""
        self.cache.clear()
        self.access_count.clear()
    
    @property
    def size(self) -> int:
        return len(self.cache)


class TranslationEngineBase:
    """翻译引擎基类"""
    
    def __init__(self):
        pass
    
    async def translate(
        self,
        text: str,
        source_lang: str = "auto",
        target_lang: str = "zh-CN",
        **kwargs
    ) -> TranslationResult:
        """翻译文本"""
        raise NotImplementedError
    
    async def translate_batch(
        self,
        texts: List[str],
        source_lang: str = "auto",
        target_lang: str = "zh-CN",
        **kwargs
    ) -> List[TranslationResult]:
        """批量翻译"""
        results = []
        for text in texts:
            result = await self.translate(text, source_lang, target_lang, **kwargs)
            results.append(result)
        return results
    
    def is_available(self) -> bool:
        """检查引擎是否可用"""
        return True


class AITranslationEngine(TranslationEngineBase):
    """AI翻译引擎"""
    
    def __init__(self, model: Optional[str] = None, provider: Optional[str] = None):
        super().__init__()
        self.model = model or settings.DEFAULT_AI_MODEL
        self.provider = provider or settings.DEFAULT_AI_PROVIDER
    
    async def translate(
        self,
        text: str,
        source_lang: str = "auto",
        target_lang: str = "zh-CN",
        **kwargs
    ) -> TranslationResult:
        start_time = time.time()
        
        system_prompt = f"""你是一个专业的翻译专家。请将以下文本从{source_lang}翻译成{target_lang}。
要求：
1. 翻译要准确、自然、流畅
2. 保持原文的语气和风格
3. 专业术语要准确
4. 不要添加任何解释或注释，只返回翻译后的文本
5. 如果是产品描述，要符合电商文案的风格"""
        
        messages = [
            ChatMessage(role="system", content=system_prompt),
            ChatMessage(role="user", content=text)
        ]
        
        try:
            response = ai_manager.chat(
                messages=messages,
                model=self.model,
                provider=self.provider,
                temperature=0.3,
                max_tokens=2000
            )
            
            translated_text = response.content.strip()
            
            return TranslationResult(
                source_text=text,
                translated_text=translated_text,
                source_language=source_lang,
                target_language=target_lang,
                engine=TranslationEngine.AI,
                model=self.model,
                quality_score=0.9,
                translation_time=time.time() - start_time
            )
            
        except Exception as e:
            logger.error(f"AI translation failed: {e}")
            raise
    
    def is_available(self) -> bool:
        return len(ai_manager.get_available_providers()) > 0


class GoogleTranslationEngine(TranslationEngineBase):
    """Google翻译引擎"""
    
    def __init__(self, api_key: Optional[str] = None):
        super().__init__()
        self.api_key = api_key
        self.base_url = "https://translation.googleapis.com/language/translate/v2"
    
    async def translate(
        self,
        text: str,
        source_lang: str = "auto",
        target_lang: str = "zh-CN",
        **kwargs
    ) -> TranslationResult:
        import httpx
        
        start_time = time.time()
        
        params = {
            "q": text,
            "target": target_lang,
            "key": self.api_key
        }
        
        if source_lang != "auto":
            params["source"] = source_lang
        
        async with httpx.AsyncClient() as client:
            response = await client.post(self.base_url, params=params)
            response.raise_for_status()
            data = response.json()
        
        translations = data.get("data", {}).get("translations", [])
        if not translations:
            raise Exception("No translation returned")
        
        translated_text = translations[0]["translatedText"]
        detected_lang = translations[0].get("detectedSourceLanguage", source_lang)
        
        return TranslationResult(
            source_text=text,
            translated_text=translated_text,
            source_language=detected_lang,
            target_language=target_lang,
            engine=TranslationEngine.GOOGLE,
            quality_score=0.85,
            translation_time=time.time() - start_time
        )
    
    def is_available(self) -> bool:
        return bool(self.api_key)


class TranslationService:
    """翻译服务"""
    
    def __init__(self):
        self.engines: Dict[str, TranslationEngineBase] = {}
        self.term_manager = TranslationTermManager()
        self.cache = TranslationCache()
        self._init_engines()
    
    def _init_engines(self):
        """初始化翻译引擎"""
        # AI翻译引擎（默认）
        self.engines["ai"] = AITranslationEngine()
        
        # Google翻译引擎（需要API Key）
        # self.engines["google"] = GoogleTranslationEngine()
    
    def get_engine(self, engine_name: str) -> Optional[TranslationEngineBase]:
        """获取翻译引擎"""
        return self.engines.get(engine_name)
    
    def get_available_engines(self) -> List[str]:
        """获取可用的引擎列表"""
        return [name for name, engine in self.engines.items() if engine.is_available()]
    
    async def translate(
        self,
        text: str,
        source_lang: str = "auto",
        target_lang: str = "zh-CN",
        engine: str = "ai",
        use_cache: bool = True,
        apply_terms: bool = True,
        polish: bool = False,
        **kwargs
    ) -> TranslationResult:
        """翻译文本
        
        Args:
            text: 源文本
            source_lang: 源语言
            target_lang: 目标语言
            engine: 翻译引擎
            use_cache: 是否使用缓存
            apply_terms: 是否应用术语库
            polish: 是否进行AI润色
        """
        if not text or not text.strip():
            return TranslationResult(
                source_text=text,
                translated_text=text,
                source_language=source_lang,
                target_language=target_lang,
                engine=TranslationEngine(engine),
                quality_score=1.0
            )
        
        # 检查缓存
        if use_cache:
            cached = self.cache.get(text, source_lang, target_lang, engine)
            if cached:
                logger.debug(f"Cache hit for translation")
                return cached
        
        # 获取引擎
        translation_engine = self.get_engine(engine)
        if not translation_engine:
            raise ValueError(f"Unknown translation engine: {engine}")
        
        # 执行翻译
        result = await translation_engine.translate(text, source_lang, target_lang, **kwargs)
        
        # 应用术语库
        if apply_terms:
            translated_text, used_terms = self.term_manager.apply_terms(
                result.translated_text,
                source_lang,
                target_lang
            )
            result.translated_text = translated_text
            result.used_terms = used_terms
        
        # AI润色
        if polish:
            result = await self.polish_translation(result)
        
        # 存入缓存
        if use_cache:
            self.cache.set(result, engine)
        
        return result
    
    async def translate_batch(
        self,
        texts: List[str],
        source_lang: str = "auto",
        target_lang: str = "zh-CN",
        engine: str = "ai",
        use_cache: bool = True,
        batch_size: int = 10,
        **kwargs
    ) -> List[TranslationResult]:
        """批量翻译"""
        results = []
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            batch_results = []
            
            for text in batch:
                result = await self.translate(
                    text,
                    source_lang,
                    target_lang,
                    engine,
                    use_cache,
                    **kwargs
                )
                batch_results.append(result)
            
            results.extend(batch_results)
        
        return results
    
    async def polish_translation(self, translation: TranslationResult) -> TranslationResult:
        """AI润色翻译结果"""
        try:
            system_prompt = f"""你是一个专业的文案编辑和润色专家。请对以下翻译文本进行润色优化。
要求：
1. 保持原意不变
2. 使语言更自然、流畅、地道
3. 优化表达，提升可读性
4. 如果是产品描述，要更有吸引力，符合电商文案风格
5. 不要改变专业术语
6. 只返回润色后的文本，不要添加任何解释"""
            
            messages = [
                ChatMessage(role="system", content=system_prompt),
                ChatMessage(role="user", content=translation.translated_text)
            ]
            
            response = ai_manager.chat(
                messages=messages,
                temperature=0.5,
                max_tokens=2000
            )
            
            translation.translated_text = response.content.strip()
            translation.is_polished = True
            translation.quality_score = min(1.0, translation.quality_score + 0.05)
            
            return translation
            
        except Exception as e:
            logger.warning(f"Translation polishing failed: {e}")
            return translation
    
    async def translate_product(
        self,
        product_data: Dict,
        source_lang: str = "auto",
        target_lang: str = "zh-CN",
        engine: str = "ai",
        fields: Optional[List[str]] = None,
        **kwargs
    ) -> Dict:
        """翻译产品数据
        
        Args:
            product_data: 产品数据字典
            source_lang: 源语言
            target_lang: 目标语言
            engine: 翻译引擎
            fields: 要翻译的字段列表，None表示翻译所有可翻译字段
        """
        if fields is None:
            fields = [
                "name", "title", "description", "short_description",
                "excerpt", "content", "seo_title", "seo_description"
            ]
        
        translated_product = product_data.copy()
        
        for field in fields:
            if field in product_data and product_data[field]:
                value = product_data[field]
                
                if isinstance(value, str):
                    result = await self.translate(
                        value,
                        source_lang,
                        target_lang,
                        engine,
                        **kwargs
                    )
                    translated_product[field] = result.translated_text
                elif isinstance(value, list):
                    translated_list = []
                    for item in value:
                        if isinstance(item, str):
                            result = await self.translate(
                                item,
                                source_lang,
                                target_lang,
                                engine,
                                **kwargs
                            )
                            translated_list.append(result.translated_text)
                        else:
                            translated_list.append(item)
                    translated_product[field] = translated_list
        
        return translated_product
    
    def add_term(self, source_term: str, target_term: str, source_lang: str = "en", target_lang: str = "zh-CN"):
        """添加术语"""
        self.term_manager.add_term(source_term, target_term, source_lang, target_lang)
    
    def add_terms_batch(self, terms: List[Tuple[str, str]], source_lang: str = "en", target_lang: str = "zh-CN"):
        """批量添加术语"""
        self.term_manager.add_terms_batch(terms, source_lang, target_lang)
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        return {
            "engines": self.get_available_engines(),
            "cache_size": self.cache.size,
            "terms_count": self.term_manager.get_terms_count(),
        }


# 全局翻译服务实例
translation_service = TranslationService()
