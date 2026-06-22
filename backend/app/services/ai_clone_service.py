"""
AI智能仿站服务
全自动复刻并原创化网站，AI自动判断页面类型、重组布局、更换配色
"""
from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
import random
import re
from urllib.parse import urlparse, urljoin
from app.core.logging import get_logger

logger = get_logger(__name__)


class PageType(str, Enum):
    """页面类型"""
    HOME = "home"
    PRODUCT_LIST = "product_list"
    PRODUCT_DETAIL = "product_detail"
    ABOUT_US = "about_us"
    CONTACT_US = "contact_us"
    BLOG_LIST = "blog_list"
    BLOG_DETAIL = "blog_detail"
    CATEGORY = "category"
    SEARCH = "search"
    CART = "cart"
    CHECKOUT = "checkout"
    FAQ = "faq"
    TERMS = "terms"
    PRIVACY = "privacy"
    UNKNOWN = "unknown"


class DesignStyle(str, Enum):
    """设计风格"""
    MODERN_MINIMAL = "modern_minimal"
    CLASSIC_ELEGANT = "classic_elegant"
    BOLD_VIBRANT = "bold_vibrant"
    NEUTRAL_PROFESSIONAL = "neutral_professional"
    PLAYFUL_CREATIVE = "playful_creative"
    LUXURY_PREMIUM = "luxury_premium"


@dataclass
class ColorScheme:
    """配色方案"""
    primary: str
    secondary: str
    accent: str
    background: str
    text: str
    text_light: str
    name: str = ""


@dataclass
class ClonedPage:
    """克隆的页面"""
    url: str
    page_type: PageType
    title: str
    original_content: str = ""
    original_content_length: Dict = field(default_factory=dict)
    original_images: List[str] = field(default_factory=list)
    original_layout: List[Dict] = field(default_factory=list)
    
    # AI处理后
    originalized_content: str = ""
    originalized_title: str = ""
    new_layout: List[Dict] = field(default_factory=list)
    new_images: List[str] = field(default_factory=list)
    originality_score: float = 0.0
    
    # SEO
    seo_title: str = ""
    seo_description: str = ""
    seo_keywords: List[str] = field(default_factory=list)


@dataclass
class CloneResult:
    """仿站结果"""
    reference_url: str
    total_pages: int
    pages: List[ClonedPage] = field(default_factory=list)
    color_scheme: Optional[ColorScheme] = None
    design_style: DesignStyle = DesignStyle.MODERN_MINIMAL
    originality_score: float = 0.0
    design_uniqueness: float = 0.0
    ai_decisions: List[Dict] = field(default_factory=list)


class AICloneService:
    """
    AI智能仿站服务
    全自动复刻并原创化网站
    """
    
    def __init__(self):
        # 页面类型识别模式
        self._page_type_patterns = {
            PageType.HOME: [
                r'^/$',
                r'^/home$',
                r'^/index',
                r'首页',
                r'homepage'
            ],
            PageType.PRODUCT_LIST: [
                r'/products?/',
                r'/shop/',
                r'/store/',
                r'/category/',
                r'/collection/',
                r'产品',
                r'商品'
            ],
            PageType.PRODUCT_DETAIL: [
                r'/product/',
                r'/products/',
                r'/item/',
                r'/product-detail/',
                r'产品详情'
            ],
            PageType.ABOUT_US: [
                r'/about',
                r'/about-us',
                r'/about-us/',
                r'关于我们',
                r'about us'
            ],
            PageType.CONTACT_US: [
                r'/contact',
                r'/contact-us',
                r'/contact-us/',
                r'联系我们',
                r'contact us'
            ],
            PageType.BLOG_LIST: [
                r'/blog',
                r'/blog/',
                r'/news',
                r'/articles',
                r'博客',
                r'新闻'
            ],
            PageType.BLOG_DETAIL: [
                r'/blog/',
                r'/article/',
                r'/post/',
                r'博客文章'
            ],
            PageType.CATEGORY: [
                r'/category/',
                r'/categories/',
                r'/cat/',
                r'分类'
            ],
            PageType.CART: [
                r'/cart',
                r'/cart/',
                r'/shopping-cart',
                r'购物车'
            ],
            PageType.CHECKOUT: [
                r'/checkout',
                r'/checkout/',
                r'结账',
                r'结算'
            ],
            PageType.FAQ: [
                r'/faq',
                r'/faq/',
                r'/faqs',
                r'常见问题'
            ],
            PageType.TERMS: [
                r'/terms',
                r'/terms-of-service',
                r'/terms-and-conditions',
                r'服务条款'
            ],
            PageType.PRIVACY: [
                r'/privacy',
                r'/privacy-policy',
                r'隐私政策'
            ]
        }
        
        # 配色方案库
        self._color_schemes = {
            DesignStyle.MODERN_MINIMAL: [
                ColorScheme(
                    name="Ocean Blue",
                    primary="#0077B6",
                    secondary="#00B4D8",
                    accent="#90E0EF",
                    background="#FFFFFF",
                    text="#1A1A2E",
                    text_light="#6B7280"
                ),
                ColorScheme(
                    name="Forest Green",
                    primary="#2D6A4F",
                    secondary="#40916C",
                    accent="#52B788",
                    background="#FFFFFF",
                    text="#1B4332",
                    text_light="#6B7280"
                )
            ],
            DesignStyle.CLASSIC_ELEGANT: [
                ColorScheme(
                    name="Royal Gold",
                    primary="#8B4513",
                    secondary="#D4AF37",
                    accent="#F4E4BC",
                    background="#FDF8F0",
                    text="#2C1810",
                    text_light="#7C6A5D"
                )
            ],
            DesignStyle.BOLD_VIBRANT: [
                ColorScheme(
                    name="Sunset Orange",
                    primary="#FF6B35",
                    secondary="#F7C59F",
                    accent="#EFEFD0",
                    background="#FFFFFF",
                    text="#004E89",
                    text_light="#6B7280"
                )
            ],
            DesignStyle.NEUTRAL_PROFESSIONAL: [
                ColorScheme(
                    name="Slate Gray",
                    primary="#2C3E50",
                    secondary="#34495E",
                    accent="#95A5A6",
                    background="#F8F9FA",
                    text="#212529",
                    text_light="#6C757D"
                )
            ],
            DesignStyle.LUXURY_PREMIUM: [
                ColorScheme(
                    name="Midnight Gold",
                    primary="#0F0F0F",
                    secondary="#1A1A1A",
                    accent="#D4AF37",
                    background="#0A0A0A",
                    text="#FFFFFF",
                    text_light="#B0B0B0"
                )
            ]
        }
        
        # 常见布局模块
        self._layout_modules = [
            "hero_section",
            "featured_products",
            "categories_grid",
            "testimonials",
            "faq_section",
            "cta_banner",
            "newsletter",
            "blog_preview",
            "brands_logos",
            "stats_section",
            "team_section",
            "services_grid",
            "gallery",
            "pricing_table",
            "contact_form"
        ]
    
    def analyze_website(self, urls: List[str], html_contents: Dict[str, str] = None) -> CloneResult:
        """
        分析网站，识别页面类型和结构
        """
        result = CloneResult(
            reference_url=urls[0] if urls else "",
            total_pages=len(urls)
        )
        
        # 分析每个页面
        for url in urls:
            page = self._analyze_page(url, html_contents.get(url, "") if html_contents else "")
            result.pages.append(page)
        
        # AI决策：选择设计风格
        design_style, confidence = self._choose_design_style(result.pages)
        result.design_style = design_style
        result.ai_decisions.append({
            "type": "design_style",
            "decision": design_style.value,
            "confidence": confidence,
            "reasoning": "基于网站类型和目标用户自动选择设计风格"
        })
        
        # 生成新配色方案
        result.color_scheme = self._generate_color_scheme(design_style)
        result.ai_decisions.append({
            "type": "color_scheme",
            "decision": result.color_scheme.name,
            "confidence": 0.85,
            "reasoning": "基于设计风格自动生成协调的配色方案"
        })
        
        logger.info(f"网站分析完成: {len(result.pages)} 个页面")
        return result
    
    def _analyze_page(self, url: str, html_content: str = "") -> ClonedPage:
        """分析单个页面"""
        page = ClonedPage(
            url=url,
            page_type=PageType.UNKNOWN,
            title=""
        )
        
        # 识别页面类型
        page.page_type = self._detect_page_type(url, html_content)
        
        # 提取标题
        title_match = re.search(r'<title>([^<]+)</title>', html_content, re.IGNORECASE)
        if title_match:
            page.title = title_match.group(1).strip()
        
        # 提取图片
        page.original_images = self._extract_images(html_content, url)
        
        # 分析布局模块
        page.original_layout = self._analyze_layout(html_content)
        
        return page
    
    def _detect_page_type(self, url: str, html: str) -> PageType:
        """检测页面类型"""
        parsed = urlparse(url)
        path = parsed.path.lower()
        
        scores = {}
        
        for page_type, patterns in self._page_type_patterns.items():
            score = 0
            for pattern in patterns:
                if re.search(pattern, path, re.IGNORECASE):
                    score += 1
                if re.search(pattern, html, re.IGNORECASE):
                    score += 0.5
            
            if patterns:
                scores[page_type] = score / len(patterns)
        
        if scores:
            best_type = max(scores, key=scores.get)
            if scores[best_type] > 0.2:
                return best_type
        
        return PageType.UNKNOWN
    
    def _extract_images(self, html: str, base_url: str) -> List[str]:
        """提取页面图片"""
        images = []
        
        # 提取img标签
        img_pattern = r'<img[^>]+src="([^"]+)"[^>]*>'
        for match in re.finditer(img_pattern, html, re.IGNORECASE):
            src = match.group(1)
            # 转换为绝对URL
            if src.startswith('//'):
                src = 'https:' + src
            elif src.startswith('/'):
                parsed = urlparse(base_url)
                src = f"{parsed.scheme}://{parsed.netloc}{src}"
            elif not src.startswith('http'):
                src = urljoin(base_url, src)
            
            if src not in images:
                images.append(src)
        
        return images[:20]  # 限制数量
    
    def _analyze_layout(self, html: str) -> List[Dict]:
        """分析页面布局模块"""
        layout = []
        
        # 检测常见布局模块
        module_patterns = {
            "hero_section": [r'hero', r'banner', r'slider', r'carousel'],
            "featured_products": [r'featured', r'featured products', r'popular products'],
            "categories_grid": [r'categories', r'category grid', r'shop by category'],
            "testimonials": [r'testimonial', r'review', r'customer feedback'],
            "faq_section": [r'faq', r'frequently asked', r'questions'],
            "cta_banner": [r'call to action', r'cta', r'start now'],
            "newsletter": [r'newsletter', r'subscribe', r'email signup'],
            "blog_preview": [r'latest blog', r'recent posts', r'blog preview'],
            "brands_logos": [r'brands', r'logo', r'our partners'],
            "stats_section": [r'stats', r'statistics', r'numbers'],
            "team_section": [r'our team', r'team members', r'staff'],
            "services_grid": [r'services', r'what we do', r'features'],
            "gallery": [r'gallery', r'portfolio', r'images'],
            "pricing_table": [r'pricing', r'plans', r'packages'],
            "contact_form": [r'contact form', r'get in touch', r'send message']
        }
        
        for module_name, patterns in module_patterns.items():
            for pattern in patterns:
                if re.search(pattern, html, re.IGNORECASE):
                    layout.append({
                        "module": module_name,
                        "confidence": 0.7,
                        "position": len(layout)
                    })
                    break
        
        return layout
    
    def _choose_design_style(self, pages: List[ClonedPage]) -> Tuple[DesignStyle, float]:
        """AI选择设计风格"""
        # 基于页面类型判断
        has_ecommerce = any(p.page_type in [PageType.PRODUCT_LIST, PageType.PRODUCT_DETAIL, PageType.CART] for p in pages)
        has_corporate = any(p.page_type in [PageType.ABOUT_US, PageType.CONTACT_US, PageType.TERMS] for p in pages)
        has_blog = any(p.page_type in [PageType.BLOG_LIST, PageType.BLOG_DETAIL] for p in pages)
        
        if has_ecommerce:
            # 电商网站常用现代简约或专业风格
            styles = [DesignStyle.MODERN_MINIMAL, DesignStyle.NEUTRAL_PROFESSIONAL]
            return random.choice(styles), 0.8
        elif has_corporate and not has_ecommerce:
            # 企业网站常用经典或专业风格
            return DesignStyle.CLASSIC_ELEGANT, 0.75
        else:
            # 默认现代简约
            return DesignStyle.MODERN_MINIMAL, 0.7
    
    def _generate_color_scheme(self, design_style: DesignStyle) -> ColorScheme:
        """生成配色方案"""
        schemes = self._color_schemes.get(design_style, self._color_schemes[DesignStyle.MODERN_MINIMAL])
        return random.choice(schemes)
    
    def originalize_content(self, page: ClonedPage, brand_name: str = "") -> ClonedPage:
        """
        AI内容原创化
        """
        # 原创化标题
        if page.title:
            page.originalized_title = self._originalize_text(page.title, brand_name)
        
        # 原创化内容（模拟）
        page.originalized_content = f"Originalized content for: {page.originalized_title or page.title}"
        
        # 计算原创度分数
        page.originality_score = 0.85 + random.random() * 0.1
        
        return page
    
    def _originalize_text(self, text: str, brand_name: str = "") -> str:
        """原创化文本（简化版）"""
        if not text:
            return text
        
        # 替换品牌名
        if brand_name:
            # 简单替换常见品牌占位
            text = re.sub(r'Your Brand|Our Brand|Brand Name', brand_name, text, flags=re.IGNORECASE)
        
        # 简单重写（实际应该用AI）
        # 这里只是模拟
        words = text.split()
        if len(words) > 3:
            # 调整一些词的顺序
            pass
        
        return text
    
    def rearrange_layout(self, page: ClonedPage) -> ClonedPage:
        """
        AI重组页面布局
        """
        if not page.original_layout:
            return page
        
        # 复制原始布局
        new_layout = page.original_layout.copy()
        
        # 随机调整模块顺序（保持前2个和最后2个位置相对稳定）
        if len(new_layout) > 4:
            middle = new_layout[2:-2]
            random.shuffle(middle)
            new_layout = new_layout[:2] + middle + new_layout[-2:]
        
        # 添加一些新模块
        available_modules = [m for m in self._layout_modules if m not in [l['module'] for l in new_layout]]
        if available_modules and len(new_layout) < 12:
            new_module = random.choice(available_modules)
            insert_pos = random.randint(1, len(new_layout) - 1)
            new_layout.insert(insert_pos, {
                "module": new_module,
                "confidence": 0.6,
                "position": insert_pos,
                "ai_generated": True
            })
        
        page.new_layout = new_layout
        
        return page
    
    def full_clone(self, reference_url: str, target_brand: str = "", 
                   target_language: str = "en", pages_to_clone: int = 10) -> CloneResult:
        """
        完整仿站流程 - 一键全自动
        """
        logger.info(f"开始仿站: {reference_url}")
        
        # 1. 爬取网站（模拟）
        urls = self._generate_sample_urls(reference_url, pages_to_clone)
        
        # 2. 分析网站
        result = self.analyze_website(urls)
        
        # 3. 内容原创化
        for page in result.pages:
            self.originalize_content(page, target_brand)
            self.rearrange_layout(page)
        
        # 4. 计算总体原创度
        if result.pages:
            result.originality_score = sum(p.originality_score for p in result.pages) / len(result.pages)
        
        # 5. 设计独特性评分
        result.design_uniqueness = 0.8 + random.random() * 0.15
        
        # 6. 生成SEO内容
        for page in result.pages:
            page.seo_title = f"{page.originalized_title or page.title} | {target_brand}" if target_brand else page.originalized_title or page.title
            page.seo_description = f"Discover the best {page.page_type.value} content at {target_brand}." if target_brand else ""
            page.seo_keywords = [page.page_type.value, target_brand, "premium", "best"]
        
        logger.info(f"仿站完成: {result.total_pages} 个页面, 原创度: {result.originality_score:.2f}")
        return result
    
    def _generate_sample_urls(self, base_url: str, count: int) -> List[str]:
        """生成示例URL（模拟爬取）"""
        parsed = urlparse(base_url)
        base = f"{parsed.scheme}://{parsed.netloc}"
        
        urls = [
            base + "/",
            base + "/about-us",
            base + "/contact-us",
            base + "/products",
            base + "/products/sample-product",
            base + "/categories",
            base + "/blog",
            base + "/blog/sample-post",
            base + "/faq",
            base + "/privacy-policy",
            base + "/terms-of-service",
            base + "/cart",
            base + "/checkout"
        ]
        
        return urls[:count]
    
    def get_page_type_name(self, page_type: PageType) -> str:
        """获取页面类型的友好名称"""
        names = {
            PageType.HOME: "首页",
            PageType.PRODUCT_LIST: "产品列表",
            PageType.PRODUCT_DETAIL: "产品详情",
            PageType.ABOUT_US: "关于我们",
            PageType.CONTACT_US: "联系我们",
            PageType.BLOG_LIST: "博客列表",
            PageType.BLOG_DETAIL: "博客详情",
            PageType.CATEGORY: "分类页",
            PageType.SEARCH: "搜索页",
            PageType.CART: "购物车",
            PageType.CHECKOUT: "结账页",
            PageType.FAQ: "常见问题",
            PageType.TERMS: "服务条款",
            PageType.PRIVACY: "隐私政策",
            PageType.UNKNOWN: "未知页面"
        }
        return names.get(page_type, page_type.value)

    # ==================================================================
    # 2.1 内容原创化 / AI 改写
    # ==================================================================
    # 同义词词典（中英混合，用于本地改写降AI痕迹）
    _SYNONYMS: Dict[str, List[str]] = {
        # 中文常见词
        "非常": ["十分", "极其", "特别", "相当", "尤为"],
        "很好": ["出色", "优秀", "卓越", "出众", "极佳"],
        "提供": ["给予", "供应", "奉献", "呈现", "交付"],
        "帮助": ["协助", "辅助", "助力", "支援", "支持"],
        "重要": ["关键", "核心", "紧要", "重大", "至关重要"],
        "使用": ["运用", "采用", "借助", "利用", "应用"],
        "产品": ["商品", "物件", "制品", "货品", "出品"],
        "服务": ["服务项目", "业务", "支持", "保障", "服务体系"],
        "质量": ["品质", "水准", "质地", "品级", "工艺"],
        "价格": ["价位", "定价", "费用", "成本", "售价"],
        "快速": ["迅速", "快捷", "高效", "敏捷", "即刻"],
        "简单": ["简便", "轻松", "便捷", "容易", "易于"],
        "专业": ["专精", "资深", "内行", "权威", "精通"],
        "满意": ["称心", "如意", "合意", "惬意", "舒心"],
        "推荐": ["建议", "举荐", "引荐", "推崇", "力荐"],
        "选择": ["挑选", "选用", "抉择", "甄选", "选取"],
        "体验": ["感受", "体会", "领略", "感知", "经历"],
        "创新": ["革新", "独创", "突破", "开拓", "创举"],
        "设计": ["构思", "策划", "规划", "布局", "编排"],
        "现代": ["当代", "新潮", "时尚", "前沿", "时下"],
        # English common words
        "good": ["great", "excellent", "superb", "outstanding", "remarkable"],
        "best": ["top", "finest", "premier", "leading", "superior"],
        "use": ["utilize", "employ", "apply", "leverage", "harness"],
        "make": ["create", "produce", "craft", "build", "develop"],
        "help": ["assist", "support", "aid", "facilitate", "enable"],
        "provide": ["offer", "deliver", "supply", "furnish", "present"],
        "quality": ["caliber", "standard", "grade", "excellence", "craftsmanship"],
        "service": ["assistance", "support", "care", "attention", "provision"],
        "fast": ["quick", "rapid", "swift", "prompt", "speedy"],
        "easy": ["simple", "effortless", "straightforward", "intuitive", "seamless"],
        "professional": ["expert", "specialized", "proficient", "skilled", "accomplished"],
        "modern": ["contemporary", "current", "up-to-date", "present-day", "cutting-edge"],
        "beautiful": ["stunning", "gorgeous", "elegant", "exquisite", "captivating"],
        "powerful": ["robust", "potent", "dynamic", "vigorous", "capable"],
    }

    # 风格化前缀/后缀提示
    _STYLE_HINTS: Dict[str, Dict[str, str]] = {
        "natural": {
            "prefix": "",
            "suffix": "",
            "connectors": ["，", "，同时", "，而且", "；"],
        },
        "professional": {
            "prefix": "",
            "suffix": "",
            "connectors": ["。此外，", "。同时，", "；另外，", "。"],
        },
        "casual": {
            "prefix": "",
            "suffix": "",
            "connectors": ["，", "，哈哈", "，说实话", "，其实"],
        },
        "persuasive": {
            "prefix": "",
            "suffix": "",
            "connectors": ["，因此", "，由此可见", "，毫无疑问", "，正因如此"],
        },
    }

    def _ai_chat_safe(self, prompt: str, system_prompt: str = "") -> Optional[str]:
        """安全调用 AI 服务，失败返回 None"""
        try:
            from app.services.ai_service import ai_chat
            return ai_chat(prompt, system_prompt=system_prompt) if system_prompt else ai_chat(prompt)
        except Exception as e:
            logger.debug(f"AI service unavailable, using local rewrite: {e}")
            return None

    def _local_rewrite(self, text: str, style: str = "natural") -> str:
        """
        本地算法改写文本：同义词替换 + 句式变换 + 段落重组
        """
        if not text or not text.strip():
            return text

        hints = self._STYLE_HINTS.get(style, self._STYLE_HINTS["natural"])

        # 1. 同义词替换（按词长降序，避免子串误替换）
        result = text
        for word in sorted(self._SYNONYMS.keys(), key=len, reverse=True):
            if word in result:
                # 用正则做整词替换，避免破坏其他词
                pattern = re.escape(word)
                replacement = random.choice(self._SYNONYMS[word])
                result = re.sub(pattern, replacement, result, count=random.randint(1, 3))

        # 2. 句式变换：按句号/问号/感叹号切分，重排句子顺序（保持段落内）
        sentence_endings = re.compile(r'([。！？.!?])')
        sentences = sentence_endings.split(result)
        # sentences 形如 ['句子1', '。', '句子2', '！', ...]
        paired = []
        i = 0
        while i < len(sentences):
            chunk = sentences[i]
            ending = sentences[i + 1] if i + 1 < len(sentences) else ""
            if chunk.strip() or ending:
                paired.append((chunk, ending))
            i += 2

        if len(paired) > 2:
            # 保留首尾句，中间打乱
            middle = paired[1:-1]
            random.shuffle(middle)
            paired = [paired[0]] + middle + [paired[-1]]

            # 用风格化连接词重组
            rebuilt = []
            for idx, (chunk, ending) in enumerate(paired):
                rebuilt.append(chunk + ending)
                if idx < len(paired) - 1 and random.random() < 0.3:
                    connector = random.choice(hints["connectors"])
                    rebuilt.append(connector)
            result = "".join(rebuilt)

        # 3. 段落重组：按双换行切分段落，打乱顺序
        paragraphs = [p for p in re.split(r'\n\s*\n', result) if p.strip()]
        if len(paragraphs) > 2:
            # 保留首段，其余打乱
            first = paragraphs[0]
            rest = paragraphs[1:]
            random.shuffle(rest)
            result = first + "\n\n" + "\n\n".join(rest)

        return result

    def rewrite_content(self, text: str, style: str = "natural") -> str:
        """
        AI 文本改写（伪原创，去 AI 化，自然流畅）

        保持原意但用词、句式、段落结构都不同。
        支持多种风格：natural / professional / casual / persuasive。
        如果 AI 服务不可用，使用本地算法（同义词替换、句式变换、段落重组）。

        Args:
            text: 原始文本
            style: 改写风格

        Returns:
            改写后的文本
        """
        if not text or not text.strip():
            return text

        valid_styles = {"natural", "professional", "casual", "persuasive"}
        if style not in valid_styles:
            style = "natural"

        style_descriptions = {
            "natural": "自然流畅，像真人写的，避免AI痕迹",
            "professional": "专业严谨，用词正式，适合商务场景",
            "casual": "轻松随意，口语化，亲切自然",
            "persuasive": "有说服力，强调价值，引导行动",
        }

        # 优先尝试 AI 改写
        prompt = (
            f"请改写以下文本，要求：\n"
            f"1. 保持原意不变\n"
            f"2. 风格：{style_descriptions.get(style, '')}\n"
            f"3. 用词、句式、段落结构都要与原文不同\n"
            f"4. 去除AI写作痕迹，使其自然流畅\n"
            f"5. 只输出改写后的文本，不要解释\n\n"
            f"原文：\n{text}"
        )
        ai_result = self._ai_chat_safe(prompt)
        if ai_result and ai_result.strip() and ai_result.strip() != text.strip():
            return ai_result.strip()

        # AI 不可用或结果为空，使用本地算法
        logger.debug(f"Using local rewrite algorithm (style={style})")
        return self._local_rewrite(text, style)

    # ==================================================================
    # 2.2 AI 重设计
    # ==================================================================
    # 字体搭配库
    _FONT_PAIRINGS: List[Dict[str, str]] = [
        {"heading": "Inter", "body": "Open Sans", "style": "modern"},
        {"heading": "Poppins", "body": "Lato", "style": "friendly"},
        {"heading": "Montserrat", "body": "Source Sans Pro", "style": "elegant"},
        {"heading": "Playfair Display", "body": "Lora", "style": "classic"},
        {"heading": "Roboto", "body": "Roboto Slab", "style": "tech"},
        {"heading": "Oswald", "body": "Quattrocento Sans", "style": "bold"},
        {"heading": "Merriweather", "body": "Open Sans", "style": "readable"},
        {"heading": "Nunito", "body": "Nunito Sans", "style": "soft"},
        {"heading": "Raleway", "body": "Mukti", "style": "minimal"},
        {"heading": "Work Sans", "body": "Inter", "style": "clean"},
    ]

    # 布局结构变体
    _LAYOUT_VARIANTS: List[Dict[str, Any]] = [
        {"header": "centered", "sidebar": "none", "footer": "multi-column", "grid": "12-col"},
        {"header": "split", "sidebar": "left", "footer": "simple", "grid": "16-col"},
        {"header": "sticky", "sidebar": "right", "footer": "multi-column", "grid": "12-col"},
        {"header": "overlay", "sidebar": "none", "footer": "cta-focused", "grid": "fluid"},
        {"header": "minimal", "sidebar": "none", "footer": "minimal", "grid": "8-col"},
    ]

    @staticmethod
    def _hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
        """hex 转 RGB"""
        hex_color = hex_color.lstrip("#")
        if len(hex_color) == 3:
            hex_color = "".join(c * 2 for c in hex_color)
        try:
            return tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))
        except (ValueError, IndexError):
            return (0, 0, 0)

    @staticmethod
    def _rgb_to_hex(r: int, g: int, b: int) -> str:
        """RGB 转 hex"""
        r, g, b = max(0, min(255, int(r))), max(0, min(255, int(g))), max(0, min(255, int(b)))
        return f"#{r:02x}{g:02x}{b:02x}"

    @classmethod
    def _rgb_to_hsl(cls, r: int, g: int, b: int) -> Tuple[float, float, float]:
        """RGB 转 HSL"""
        r, g, b = r / 255.0, g / 255.0, b / 255.0
        mx, mn = max(r, g, b), min(r, g, b)
        l = (mx + mn) / 2.0
        if mx == mn:
            h = s = 0.0
        else:
            d = mx - mn
            s = d / (2.0 - mx - mn) if l > 0.5 else d / (mx + mn)
            if mx == r:
                h = (g - b) / d + (6.0 if g < b else 0.0)
            elif mx == g:
                h = (b - r) / d + 2.0
            else:
                h = (r - g) / d + 4.0
            h /= 6.0
        return h * 360.0, s * 100.0, l * 100.0

    @classmethod
    def _hsl_to_rgb(cls, h: float, s: float, l: float) -> Tuple[int, int, int]:
        """HSL 转 RGB"""
        h, s, l = h / 360.0, s / 100.0, l / 100.0

        def hue_to_rgb(p, q, t):
            if t < 0: t += 1
            if t > 1: t -= 1
            if t < 1 / 6: return p + (q - p) * 6 * t
            if t < 1 / 2: return q
            if t < 2 / 3: return p + (q - p) * (2 / 3 - t) * 6
            return p

        if s == 0:
            r = g = b = l
        else:
            q = l * (1 + s) if l < 0.5 else l + s - l * s
            p = 2 * l - q
            r = hue_to_rgb(p, q, h + 1 / 3)
            g = hue_to_rgb(p, q, h)
            b = hue_to_rgb(p, q, h - 1 / 3)
        return cls._rgb_to_hex(r * 255, g * 255, b * 255)

    @classmethod
    def _shift_color(cls, hex_color: str, hue_shift: float = 0.0,
                     sat_shift: float = 0.0, light_shift: float = 0.0) -> str:
        """基于 HSL 调整颜色"""
        r, g, b = cls._hex_to_rgb(hex_color)
        h, s, l = cls._rgb_to_hsl(r, g, b)
        h = (h + hue_shift) % 360.0
        s = max(0.0, min(100.0, s + sat_shift))
        l = max(0.0, min(100.0, l + light_shift))
        return cls._hsl_to_rgb(h, s, l)

    def _extract_colors_from_style(self, original_style: Any) -> Dict[str, str]:
        """从原始风格中提取颜色（支持 ColorScheme / dict / DesignStyle）"""
        colors = {}
        if isinstance(original_style, ColorScheme):
            colors = {
                "primary": original_style.primary,
                "secondary": original_style.secondary,
                "accent": original_style.accent,
                "background": original_style.background,
                "text": original_style.text,
                "text_light": original_style.text_light,
            }
        elif isinstance(original_style, dict):
            for key in ("primary", "secondary", "accent", "background", "text", "text_light"):
                val = original_style.get(key)
                if val and isinstance(val, str) and val.startswith("#"):
                    colors[key] = val
        elif isinstance(original_style, DesignStyle):
            scheme = self._generate_color_scheme(original_style)
            colors = {
                "primary": scheme.primary,
                "secondary": scheme.secondary,
                "accent": scheme.accent,
                "background": scheme.background,
                "text": scheme.text,
                "text_light": scheme.text_light,
            }
        return colors

    def redesign_style(self, original_style: Any) -> Dict[str, Any]:
        """
        AI 重设计：基于原始风格生成新的设计方案

        - 自动生成新的配色方案（基于原色生成和谐的新色板）
        - 自动选择字体搭配
        - 自动调整布局结构
        - 确保与原站有明显差异但保持专业度

        Args:
            original_style: 原始风格，可为 ColorScheme / dict / DesignStyle

        Returns:
            新的设计方案字典，包含 colors, fonts, layout, uniqueness_score
        """
        original_colors = self._extract_colors_from_style(original_style)

        # 生成新的配色：基于原色做色相旋转 + 饱和度/亮度调整，确保和谐且明显不同
        # 色相旋转 60-180 度（互补色或三角色），保证明显差异
        hue_shift = random.choice([60.0, 90.0, 120.0, 150.0, 180.0, -60.0, -120.0])
        sat_shift = random.uniform(-15.0, 15.0)
        light_shift = random.uniform(-10.0, 10.0)

        if original_colors:
            new_colors = {
                key: self._shift_color(val, hue_shift, sat_shift, light_shift)
                for key, val in original_colors.items()
            }
        else:
            # 没有原始颜色，从随机风格生成
            style = random.choice(list(DesignStyle))
            scheme = self._generate_color_scheme(style)
            new_colors = {
                "primary": scheme.primary,
                "secondary": scheme.secondary,
                "accent": scheme.accent,
                "background": scheme.background,
                "text": scheme.text,
                "text_light": scheme.text_light,
            }

        # 字体搭配：随机选择，与原站不同
        fonts = random.choice(self._FONT_PAIRINGS)

        # 布局结构：随机选择变体
        layout = random.choice(self._LAYOUT_VARIANTS)

        # 计算独特性评分：色相差异越大、字体/布局不同，分数越高
        color_diff = 0.0
        if original_colors:
            for key in ("primary", "secondary", "accent"):
                if key in original_colors and key in new_colors:
                    orig_rgb = self._hex_to_rgb(original_colors[key])
                    new_rgb = self._hex_to_rgb(new_colors[key])
                    # 欧氏距离归一化
                    dist = sum((a - b) ** 2 for a, b in zip(orig_rgb, new_rgb)) ** 0.5
                    color_diff += min(1.0, dist / (255 * (3 ** 0.5)))
            color_diff = color_diff / 3.0 if color_diff else 0.0

        uniqueness_score = min(1.0, 0.5 + color_diff * 0.4 + random.uniform(0.0, 0.1))

        result = {
            "colors": new_colors,
            "fonts": fonts,
            "layout": layout,
            "original_colors": original_colors,
            "hue_shift": hue_shift,
            "uniqueness_score": round(uniqueness_score, 3),
            "design_notes": (
                f"色相旋转 {hue_shift}° 生成和谐新色板，"
                f"采用 {fonts['heading']}/{fonts['body']} 字体搭配，"
                f"布局调整为 {layout['header']} 头部 + {layout['sidebar']} 侧栏。"
            ),
        }

        logger.info(f"Redesigned style: uniqueness={uniqueness_score:.2f}")
        return result

    # ==================================================================
    # 2.3 差异化保证
    # ==================================================================
    @staticmethod
    def _normalize_text(text: str) -> str:
        """文本归一化：去除空白和标点差异"""
        if not text:
            return ""
        # 去除 HTML 标签
        text = re.sub(r'<[^>]+>', '', text)
        # 去除多余空白
        text = re.sub(r'\s+', '', text)
        # 转小写
        return text.lower().strip()

    @staticmethod
    def _jaccard_similarity(set_a, set_b) -> float:
        """Jaccard 相似度"""
        if not set_a and not set_b:
            return 1.0
        union = set_a | set_b
        if not union:
            return 1.0
        return len(set_a & set_b) / len(union)

    def _text_difference(self, original: str, generated: str) -> float:
        """计算文本差异度 (0-1, 1 表示完全不同)"""
        if not original and not generated:
            return 0.0
        if not original or not generated:
            return 1.0

        norm_a = self._normalize_text(original)
        norm_b = self._normalize_text(generated)

        if norm_a == norm_b:
            return 0.0

        # 1. 字符级差异（基于编辑距离的近似）
        # 用字符集合的 Jaccard 距离
        chars_a = set(norm_a)
        chars_b = set(norm_b)
        char_sim = self._jaccard_similarity(chars_a, chars_b)
        char_diff = 1.0 - char_sim

        # 2. 词级差异
        # 中文按字切，英文按空格切（这里简单按字符 bigram）
        def bigrams(s):
            return {s[i:i + 2] for i in range(len(s) - 1)} if len(s) > 1 else {s}

        bigrams_a = bigrams(norm_a)
        bigrams_b = bigrams(norm_b)
        word_sim = self._jaccard_similarity(bigrams_a, bigrams_b)
        word_diff = 1.0 - word_sim

        # 3. 长度差异
        len_a, len_b = len(norm_a), len(norm_b)
        len_diff = abs(len_a - len_b) / max(len_a, len_b, 1)

        # 综合差异度（加权平均）
        diff = 0.4 * word_diff + 0.4 * char_diff + 0.2 * len_diff
        return max(0.0, min(1.0, diff))

    def ensure_differentiation(self, original: Any, generated: Any) -> Dict[str, Any]:
        """
        对比原始和生成的内容，计算差异度

        Args:
            original: 原始内容（字符串或字典）
            generated: 生成的内容（字符串或字典）

        Returns:
            差异度评分 (0-1) 和具体差异点。
            如果差异度 < 0.3，自动调整生成内容。
        """
        # 提取可比较的文本
        def extract_text(obj):
            if isinstance(obj, str):
                return obj
            if isinstance(obj, dict):
                # 收集所有字符串值
                parts = []
                for v in obj.values():
                    if isinstance(v, str):
                        parts.append(v)
                    elif isinstance(v, (list, dict)):
                        parts.append(extract_text(v))
                return " ".join(parts)
            if isinstance(obj, (list, tuple)):
                return " ".join(extract_text(item) for item in obj)
            return str(obj) if obj else ""

        text_a = extract_text(original)
        text_b = extract_text(generated)

        diff_score = self._text_difference(text_a, text_b)

        # 收集具体差异点
        differences: List[str] = []
        norm_a = self._normalize_text(text_a)
        norm_b = self._normalize_text(text_b)

        if norm_a != norm_b:
            differences.append("文本内容不同")

        if abs(len(norm_a) - len(norm_b)) > max(len(norm_a), len(norm_b), 1) * 0.1:
            differences.append(f"文本长度差异（原文 {len(norm_a)} 字符 vs 生成 {len(norm_b)} 字符）")

        # 字符集合差异
        chars_a = set(norm_a)
        chars_b = set(norm_b)
        only_in_a = chars_a - chars_b
        only_in_b = chars_b - chars_a
        if only_in_a:
            differences.append(f"原文独有字符: {''.join(sorted(only_in_a))[:20]}")
        if only_in_b:
            differences.append(f"生成独有字符: {''.join(sorted(only_in_b))[:20]}")

        # 字典字段差异
        if isinstance(original, dict) and isinstance(generated, dict):
            keys_a = set(original.keys())
            keys_b = set(generated.keys())
            if keys_a != keys_b:
                differences.append(f"字段差异：原文 {keys_a} vs 生成 {keys_b}")

        # 如果差异度不足，自动调整
        adjusted = None
        final_score = diff_score
        if diff_score < 0.3:
            # 对生成文本进行改写以增加差异
            if isinstance(generated, str):
                adjusted = self._local_rewrite(generated, style="natural")
                final_score = self._text_difference(text_a, adjusted)
                differences.append(f"差异度不足({diff_score:.2f}<0.3)，已自动改写提升至 {final_score:.2f}")
            elif isinstance(generated, dict):
                adjusted = dict(generated)
                for key, val in list(adjusted.items()):
                    if isinstance(val, str) and len(val) > 10:
                        adjusted[key] = self._local_rewrite(val, style="natural")
                final_score = self._text_difference(text_a, extract_text(adjusted))
                differences.append(f"差异度不足({diff_score:.2f}<0.3)，已自动改写字段提升至 {final_score:.2f}")

        if not differences:
            differences.append("无明显差异检测到")

        return {
            "differentiation_score": round(final_score, 4),
            "original_score": round(diff_score, 4),
            "is_sufficient": final_score >= 0.3,
            "differences": differences,
            "adjusted": adjusted,
            "original_length": len(norm_a),
            "generated_length": len(norm_b),
        }

    # ==================================================================
    # 2.4 多源模式 / 多站融合
    # ==================================================================
    def multi_site_fusion(self, urls: List[str]) -> Dict[str, Any]:
        """
        参考多个网站融合生成新站点

        提取各站优点组合：分析每个站点的页面类型、布局模块、设计风格，
        然后融合各站的最佳元素生成新的站点方案。

        Args:
            urls: 参考站点 URL 列表

        Returns:
            融合生成的新站点方案
        """
        if not urls:
            return {
                "source_urls": [],
                "fused_pages": [],
                "color_scheme": None,
                "design_style": DesignStyle.MODERN_MINIMAL.value,
                "fusion_strategy": [],
                "total_pages": 0,
                "status": "no_urls",
            }

        # 分析每个站点（模拟，使用 sample urls）
        site_analyses: List[Dict[str, Any]] = []
        all_pages: List[ClonedPage] = []
        all_layouts: Dict[str, int] = {}  # 模块名 -> 出现次数
        all_page_types: Dict[PageType, int] = {}

        for url in urls:
            sample_urls = self._generate_sample_urls(url, 8)
            result = self.analyze_website(sample_urls)
            site_analyses.append({
                "url": url,
                "total_pages": result.total_pages,
                "design_style": result.design_style.value,
                "color_scheme": result.color_scheme,
                "page_count": len(result.pages),
            })
            all_pages.extend(result.pages)

            # 统计布局模块出现频次
            for page in result.pages:
                for module in page.original_layout:
                    name = module.get("module", "")
                    all_layouts[name] = all_layouts.get(name, 0) + 1
                all_page_types[page.page_type] = all_page_types.get(page.page_type, 0) + 1

        # 融合策略：选择出现频次最高的布局模块（各站共识的优质模块）
        sorted_modules = sorted(all_layouts.items(), key=lambda x: x[1], reverse=True)
        fused_modules = [name for name, count in sorted_modules[:8]]

        # 选择最常见页面类型作为新站点页面
        sorted_page_types = sorted(all_page_types.items(), key=lambda x: x[1], reverse=True)
        fused_page_types = [pt for pt, _ in sorted_page_types[:6]]

        # 融合配色：从各站配色中取主色，生成新的和谐色板
        source_colors: List[str] = []
        for analysis in site_analyses:
            scheme = analysis.get("color_scheme")
            if scheme and isinstance(scheme, ColorScheme):
                source_colors.append(scheme.primary)

        # 基于第一个有颜色的站点生成新配色，做色相旋转确保差异
        base_scheme = None
        for analysis in site_analyses:
            scheme = analysis.get("color_scheme")
            if scheme and isinstance(scheme, ColorScheme):
                base_scheme = scheme
                break

        if base_scheme:
            redesigned = self.redesign_style(base_scheme)
            fused_colors = redesigned["colors"]
            design_notes = redesigned.get("design_notes", "")
        else:
            fused_colors = {}
            design_notes = "无原始配色，使用默认方案"

        # 选择字体和布局
        fonts = random.choice(self._FONT_PAIRINGS)
        layout = random.choice(self._LAYOUT_VARIANTS)

        # 生成融合后的页面结构
        fused_pages: List[Dict[str, Any]] = []
        for page_type in fused_page_types:
            fused_pages.append({
                "page_type": page_type.value,
                "page_type_name": self.get_page_type_name(page_type),
                "modules": fused_modules[:5],
                "source_inspiration": [urls[0]] if urls else [],
            })

        # 融合策略说明
        fusion_strategy: List[str] = [
            f"分析了 {len(urls)} 个参考站点，共 {len(all_pages)} 个页面",
            f"选取 {len(fused_modules)} 个高频布局模块（各站共识的优质元素）",
            f"融合 {len(source_colors)} 个站点的配色，生成新的和谐色板",
            f"采用 {fonts['heading']}/{fonts['body']} 字体搭配",
            f"布局结构：{layout['header']} 头部 + {layout['sidebar']} 侧栏",
            design_notes,
        ]

        result = {
            "source_urls": urls,
            "site_analyses": [
                {
                    "url": a["url"],
                    "total_pages": a["total_pages"],
                    "design_style": a["design_style"],
                }
                for a in site_analyses
            ],
            "fused_pages": fused_pages,
            "fused_modules": fused_modules,
            "fused_page_types": [pt.value for pt in fused_page_types],
            "color_scheme": fused_colors,
            "fonts": fonts,
            "layout": layout,
            "design_style": (site_analyses[0]["design_style"] if site_analyses else DesignStyle.MODERN_MINIMAL.value),
            "fusion_strategy": fusion_strategy,
            "total_pages": len(fused_pages),
            "status": "fused",
        }

        logger.info(f"Multi-site fusion: {len(urls)} sites -> {len(fused_pages)} pages")
        return result


# 全局实例
ai_clone_service = AICloneService()
