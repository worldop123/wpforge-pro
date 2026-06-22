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


class DeepLTranslationEngine(TranslationEngineBase):
    """DeepL翻译引擎"""
    
    def __init__(self, api_key: Optional[str] = None):
        super().__init__()
        self.api_key = api_key or settings.DEEPL_API_KEY
        self.base_url = "https://api.deepl.com/v2/translate"
        self.free_base_url = "https://api-free.deepl.com/v2/translate"
        self._is_free = False
    
    async def translate(
        self,
        text: str,
        source_lang: str = "auto",
        target_lang: str = "zh-CN",
        **kwargs
    ) -> TranslationResult:
        import httpx
        
        start_time = time.time()
        
        # DeepL语言代码转换
        deepl_target = self._convert_lang_code(target_lang)
        deepl_source = self._convert_lang_code(source_lang) if source_lang != "auto" else None
        
        data = {
            "text": text,
            "target_lang": deepl_target,
        }
        
        if deepl_source:
            data["source_lang"] = deepl_source
        
        # 表单ality参数（正式/非正式）
        if "formality" in kwargs:
            data["formality"] = kwargs["formality"]
        
        # 选择API端点
        url = self.free_base_url if self._is_free else self.base_url
        
        headers = {
            "Authorization": f"DeepL-Auth-Key {self.api_key}",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, data=data, headers=headers)
            response.raise_for_status()
            result_data = response.json()
        
        translations = result_data.get("translations", [])
        if not translations:
            raise Exception("No translation returned")
        
        translated_text = translations[0]["text"]
        detected_lang = translations[0].get("detected_source_language", source_lang)
        
        return TranslationResult(
            source_text=text,
            translated_text=translated_text,
            source_language=self._convert_lang_code_back(detected_lang),
            target_language=target_lang,
            engine=TranslationEngine.DEEPL,
            quality_score=0.92,
            translation_time=time.time() - start_time
        )
    
    def _convert_lang_code(self, lang: str) -> str:
        """转换语言代码为DeepL格式"""
        lang_map = {
            "zh-CN": "ZH",
            "zh-TW": "ZH",
            "en": "EN",
            "en-US": "EN",
            "en-GB": "EN",
            "de": "DE",
            "fr": "FR",
            "es": "ES",
            "it": "IT",
            "pt": "PT",
            "pt-BR": "PT-BR",
            "pt-PT": "PT-PT",
            "nl": "NL",
            "pl": "PL",
            "ru": "RU",
            "ja": "JA",
            "ko": "KO",
            "hu": "HU",
            "ro": "RO",
            "cs": "CS",
            "sk": "SK",
            "bg": "BG",
            "hr": "HR",
            "da": "DA",
            "fi": "FI",
            "el": "EL",
            "et": "ET",
            "lv": "LV",
            "lt": "LT",
            "mt": "MT",
            "sk": "SK",
            "sl": "SL",
            "sv": "SV",
            "tr": "TR",
            "uk": "UK",
        }
        return lang_map.get(lang, lang.upper())
    
    def _convert_lang_code_back(self, lang: str) -> str:
        """将DeepL语言代码转换回标准格式"""
        lang_map = {
            "ZH": "zh-CN",
            "EN": "en",
            "DE": "de",
            "FR": "fr",
            "ES": "es",
            "IT": "it",
            "PT": "pt",
            "NL": "nl",
            "PL": "pl",
            "RU": "ru",
            "JA": "ja",
            "KO": "ko",
            "HU": "hu",
            "RO": "ro",
        }
        return lang_map.get(lang, lang.lower())
    
    def is_available(self) -> bool:
        return bool(self.api_key)


class TranslationMemory:
    """翻译记忆库"""
    
    def __init__(self, max_entries: int = 100000):
        self.max_entries = max_entries
        self.entries: Dict[str, Dict] = {}  # {hash: {source, target, source_lang, target_lang, count, last_used}}
    
    def _get_key(self, source_text: str, source_lang: str, target_lang: str) -> str:
        """生成记忆键"""
        key_str = f"{source_text.strip().lower()}_{source_lang}_{target_lang}"
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def lookup(self, text: str, source_lang: str, target_lang: str) -> Optional[str]:
        """查找翻译记忆
        
        Returns:
            匹配的翻译文本，未找到返回None
        """
        key = self._get_key(text, source_lang, target_lang)
        if key in self.entries:
            entry = self.entries[key]
            entry["count"] += 1
            entry["last_used"] = time.time()
            return entry["target"]
        return None
    
    def add(self, source_text: str, target_text: str, source_lang: str, target_lang: str):
        """添加翻译记忆"""
        key = self._get_key(source_text, source_lang, target_lang)
        
        if key in self.entries:
            self.entries[key]["count"] += 1
            self.entries[key]["last_used"] = time.time()
        else:
            # 如果超过最大条目数，删除最久未使用的
            if len(self.entries) >= self.max_entries:
                oldest_key = min(self.entries, key=lambda k: self.entries[k]["last_used"])
                del self.entries[oldest_key]
            
            self.entries[key] = {
                "source": source_text,
                "target": target_text,
                "source_lang": source_lang,
                "target_lang": target_lang,
                "count": 1,
                "last_used": time.time()
            }
    
    def add_batch(self, entries: List[Tuple[str, str]], source_lang: str, target_lang: str):
        """批量添加翻译记忆"""
        for source, target in entries:
            self.add(source, target, source_lang, target_lang)
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        return {
            "total_entries": len(self.entries),
            "max_entries": self.max_entries
        }


class TranslationQualityEvaluator:
    """翻译质量评估器"""
    
    def __init__(self):
        pass
    
    def evaluate(self, source_text: str, translated_text: str, 
                 source_lang: str, target_lang: str) -> float:
        """评估翻译质量
        
        Returns:
            质量分数 0.0 - 1.0
        """
        score = 0.5  # 基础分
        
        # 1. 长度合理性检查
        source_len = len(source_text)
        target_len = len(translated_text)
        
        if source_len > 0 and target_len > 0:
            ratio = target_len / source_len
            # 合理的长度比例范围 0.5 - 2.0
            if 0.5 <= ratio <= 2.0:
                score += 0.15
            elif 0.3 <= ratio <= 3.0:
                score += 0.05
        
        # 2. 完整性检查（关键词保留）
        # 检查数字是否保留
        import re
        source_numbers = set(re.findall(r'\d+', source_text))
        target_numbers = set(re.findall(r'\d+', translated_text))
        if source_numbers.issubset(target_numbers):
            score += 0.1
        
        # 3. 格式保持检查
        # 检查标点符号
        source_punct = len(re.findall(r'[.,!?;:]', source_text))
        target_punct = len(re.findall(r'[.,!?;:]', translated_text))
        if abs(source_punct - target_punct) <= 2:
            score += 0.1
        
        # 4. 无空翻译
        if translated_text.strip():
            score += 0.1
        
        # 5. 无乱码检测
        if not self._has_garbled_chars(translated_text):
            score += 0.05
        
        return min(1.0, max(0.0, score))
    
    def _has_garbled_chars(self, text: str) -> bool:
        """检测是否有乱码字符"""
        # 检查是否有替换字符或控制字符
        garbled_patterns = ['�', '□', '?', '\ufffd']
        for pattern in garbled_patterns:
            if pattern in text:
                return True
        return False


class TranslationService:
    """翻译服务"""
    
    def __init__(self):
        self.engines: Dict[str, TranslationEngineBase] = {}
        self.term_manager = TranslationTermManager()
        self.cache = TranslationCache()
        self.translation_memory = TranslationMemory()
        self.quality_evaluator = TranslationQualityEvaluator()
        self._engine_priority = ["deepl", "google", "ai"]  # 引擎优先级
        self._init_engines()
    
    def _init_engines(self):
        """初始化翻译引擎"""
        # AI翻译引擎（默认，总是可用）
        self.engines["ai"] = AITranslationEngine()
        
        # DeepL翻译引擎（需要API Key）
        if hasattr(settings, 'DEEPL_API_KEY') and settings.DEEPL_API_KEY:
            self.engines["deepl"] = DeepLTranslationEngine()
        
        # Google翻译引擎（需要API Key）
        if hasattr(settings, 'GOOGLE_TRANSLATE_API_KEY') and settings.GOOGLE_TRANSLATE_API_KEY:
            self.engines["google"] = GoogleTranslationEngine(settings.GOOGLE_TRANSLATE_API_KEY)
    
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
        engine: str = "auto",
        use_cache: bool = True,
        use_memory: bool = True,
        apply_terms: bool = True,
        polish: bool = False,
        auto_fallback: bool = True,
        evaluate_quality: bool = False,
        **kwargs
    ) -> TranslationResult:
        """翻译文本
        
        Args:
            text: 源文本
            source_lang: 源语言
            target_lang: 目标语言
            engine: 翻译引擎，"auto"表示自动选择最优引擎
            use_cache: 是否使用缓存
            use_memory: 是否使用翻译记忆库
            apply_terms: 是否应用术语库
            polish: 是否进行AI润色
            auto_fallback: 是否自动降级
            evaluate_quality: 是否评估翻译质量
        """
        if not text or not text.strip():
            return TranslationResult(
                source_text=text,
                translated_text=text,
                source_language=source_lang,
                target_language=target_lang,
                engine=TranslationEngine.AI,
                quality_score=1.0
            )
        
        # 检查缓存
        if use_cache:
            cached = self.cache.get(text, source_lang, target_lang, engine)
            if cached:
                logger.debug(f"Cache hit for translation")
                return cached
        
        # 检查翻译记忆库
        if use_memory and source_lang != "auto":
            memory_result = self.translation_memory.lookup(text, source_lang, target_lang)
            if memory_result:
                logger.debug(f"Translation memory hit")
                result = TranslationResult(
                    source_text=text,
                    translated_text=memory_result,
                    source_language=source_lang,
                    target_language=target_lang,
                    engine=TranslationEngine.AI,
                    quality_score=0.95
                )
                if use_cache:
                    self.cache.set(result, engine)
                return result
        
        # 确定要使用的引擎列表
        if engine == "auto":
            # 按优先级选择可用引擎
            engines_to_try = [e for e in self._engine_priority if e in self.engines and self.engines[e].is_available()]
            if not engines_to_try:
                engines_to_try = ["ai"]  # 兜底用AI
        else:
            engines_to_try = [engine]
            if auto_fallback:
                # 添加降级引擎
                for e in self._engine_priority:
                    if e not in engines_to_try and e in self.engines and self.engines[e].is_available():
                        engines_to_try.append(e)
        
        # 尝试翻译，支持自动降级
        result = None
        last_error = None
        
        for engine_name in engines_to_try:
            try:
                translation_engine = self.engines[engine_name]
                result = await translation_engine.translate(text, source_lang, target_lang, **kwargs)
                logger.debug(f"Translation successful with engine: {engine_name}")
                break
            except Exception as e:
                last_error = e
                logger.warning(f"Translation engine {engine_name} failed: {e}")
                if not auto_fallback:
                    raise
        
        if result is None:
            # 所有引擎都失败了，使用简单的文本复制作为最后兜底
            logger.error(f"All translation engines failed, using fallback: {last_error}")
            result = TranslationResult(
                source_text=text,
                translated_text=text,
                source_language=source_lang,
                target_language=target_lang,
                engine=TranslationEngine.AI,
                quality_score=0.0
            )
        
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
        
        # 质量评估
        if evaluate_quality and source_lang != "auto":
            quality_score = self.quality_evaluator.evaluate(
                text, result.translated_text, source_lang, target_lang
            )
            result.quality_score = quality_score
        
        # 添加到翻译记忆库
        if use_memory and source_lang != "auto" and result.quality_score >= 0.7:
            self.translation_memory.add(text, result.translated_text, source_lang, target_lang)
        
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
            "translation_memory": self.translation_memory.get_stats(),
        }


# 全局翻译服务实例
translation_service = TranslationService()
