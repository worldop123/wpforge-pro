"""
SEO优化服务 - 页面SEO、技术SEO、速度优化
"""

from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field
import re
import hashlib
from urllib.parse import urlparse

from app.core.config import settings
from app.core.logging import get_logger
from app.services.ai_service import ai_manager, ChatMessage

logger = get_logger(__name__)


@dataclass
class SEOAnalysisResult:
    """SEO分析结果"""
    url: str
    overall_score: int = 0
    content_score: int = 0
    technical_score: int = 0
    performance_score: int = 0
    
    # 元数据
    title: Optional[str] = None
    description: Optional[str] = None
    keywords: Optional[str] = None
    
    # 问题和建议
    issues: List[Dict] = field(default_factory=list)
    recommendations: List[Dict] = field(default_factory=list)
    
    # 详细数据
    headings: List[Dict] = field(default_factory=list)
    images: List[Dict] = field(default_factory=list)
    links: List[Dict] = field(default_factory=list)
    word_count: int = 0
    keyword_density: Dict[str, float] = field(default_factory=dict)


class SEOAnalyzer:
    """SEO分析器"""
    
    def __init__(self):
        pass
    
    def analyze_html(self, html: str, url: str, target_keywords: Optional[List[str]] = None) -> SEOAnalysisResult:
        """分析HTML页面的SEO"""
        from bs4 import BeautifulSoup
        
        result = SEOAnalysisResult(url=url)
        soup = BeautifulSoup(html, 'html.parser')
        
        # 分析元数据
        self._analyze_meta(soup, result)
        
        # 分析标题结构
        self._analyze_headings(soup, result)
        
        # 分析图片
        self._analyze_images(soup, result)
        
        # 分析链接
        self._analyze_links(soup, result, url)
        
        # 分析内容
        self._analyze_content(soup, result, target_keywords)
        
        # 计算分数
        self._calculate_scores(result)
        
        # 生成建议
        self._generate_recommendations(result)
        
        return result
    
    def _analyze_meta(self, soup, result: SEOAnalysisResult):
        """分析元数据"""
        # Title
        title_tag = soup.find('title')
        if title_tag:
            result.title = title_tag.string.strip() if title_tag.string else ''
            
            # 检查标题长度
            title_len = len(result.title)
            if title_len < 30:
                result.issues.append({
                    "type": "title",
                    "severity": "warning",
                    "message": f"标题过短: {title_len}字符，建议30-60字符"
                })
            elif title_len > 60:
                result.issues.append({
                    "type": "title",
                    "severity": "warning",
                    "message": f"标题过长: {title_len}字符，建议30-60字符"
                })
        
        # Meta Description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc and meta_desc.get('content'):
            result.description = meta_desc['content'].strip()
            
            desc_len = len(result.description)
            if desc_len < 70:
                result.issues.append({
                    "type": "description",
                    "severity": "warning",
                    "message": f"描述过短: {desc_len}字符，建议70-160字符"
                })
            elif desc_len > 160:
                result.issues.append({
                    "type": "description",
                    "severity": "warning",
                    "message": f"描述过长: {desc_len}字符，建议70-160字符"
                })
        else:
            result.issues.append({
                "type": "description",
                "severity": "error",
                "message": "缺少meta description"
            })
        
        # Meta Keywords
        meta_keywords = soup.find('meta', attrs={'name': 'keywords'})
        if meta_keywords and meta_keywords.get('content'):
            result.keywords = meta_keywords['content'].strip()
        
        # Canonical
        canonical = soup.find('link', attrs={'rel': 'canonical'})
        if not canonical:
            result.issues.append({
                "type": "canonical",
                "severity": "warning",
                "message": "缺少canonical标签"
            })
        
        # OG tags
        og_title = soup.find('meta', attrs={'property': 'og:title'})
        og_image = soup.find('meta', attrs={'property': 'og:image'})
        if not og_title or not og_image:
            result.issues.append({
                "type": "og",
                "severity": "info",
                "message": "建议添加Open Graph标签"
            })
    
    def _analyze_headings(self, soup, result: SEOAnalysisResult):
        """分析标题结构"""
        headings = []
        
        for level in range(1, 7):
            tags = soup.find_all(f'h{level}')
            for i, tag in enumerate(tags):
                text = tag.get_text(strip=True)
                headings.append({
                    "level": level,
                    "text": text,
                    "index": i + 1,
                    "length": len(text)
                })
        
        result.headings = headings
        
        # 检查H1
        h1_tags = soup.find_all('h1')
        if len(h1_tags) == 0:
            result.issues.append({
                "type": "headings",
                "severity": "error",
                "message": "缺少H1标题"
            })
        elif len(h1_tags) > 1:
            result.issues.append({
                "type": "headings",
                "severity": "warning",
                "message": f"有{len(h1_tags)}个H1标题，建议只有1个"
            })
        
        # 检查标题层级
        levels = [h['level'] for h in headings]
        if levels:
            # 检查是否跳级
            for i in range(1, len(levels)):
                if levels[i] > levels[i-1] + 1:
                    result.issues.append({
                        "type": "headings",
                        "severity": "warning",
                        "message": f"标题层级跳级: H{levels[i-1]} -> H{levels[i]}"
                    })
                    break
    
    def _analyze_images(self, soup, result: SEOAnalysisResult):
        """分析图片"""
        images = []
        img_tags = soup.find_all('img')
        
        for img in img_tags:
            src = img.get('src', '')
            alt = img.get('alt', '')
            
            images.append({
                "src": src,
                "alt": alt,
                "has_alt": bool(alt),
                "is_internal": not src.startswith('http') or urlparse(src).netloc == urlparse(result.url).netloc
            })
        
        result.images = images
        
        # 检查alt属性
        missing_alt = sum(1 for img in images if not img['has_alt'])
        if missing_alt > 0:
            result.issues.append({
                "type": "images",
                "severity": "warning",
                "message": f"有{missing_alt}张图片缺少alt属性"
            })
    
    def _analyze_links(self, soup, result: SEOAnalysisResult, base_url: str):
        """分析链接"""
        links = []
        a_tags = soup.find_all('a', href=True)
        
        base_domain = urlparse(base_url).netloc
        
        for a in a_tags:
            href = a['href']
            text = a.get_text(strip=True)
            
            is_internal = False
            if href.startswith('/') or (href.startswith('http') and urlparse(href).netloc == base_domain):
                is_internal = True
            
            links.append({
                "href": href,
                "text": text,
                "is_internal": is_internal,
                "has_text": bool(text)
            })
        
        result.links = links
        
        # 检查空链接文本
        empty_text = sum(1 for link in links if not link['has_text'])
        if empty_text > 0:
            result.issues.append({
                "type": "links",
                "severity": "info",
                "message": f"有{empty_text}个链接没有锚文本"
            })
    
    def _analyze_content(self, soup, result: SEOAnalysisResult, target_keywords: Optional[List[str]] = None):
        """分析内容"""
        # 获取正文文本
        text = soup.get_text()
        
        # 清理文本
        text = re.sub(r'\s+', ' ', text).strip()
        words = text.split()
        result.word_count = len(words)
        
        # 检查字数
        if result.word_count < 300:
            result.issues.append({
                "type": "content",
                "severity": "warning",
                "message": f"内容较少: {result.word_count}字，建议至少300字"
            })
        elif result.word_count < 1000:
            result.issues.append({
                "type": "content",
                "severity": "info",
                "message": f"内容一般: {result.word_count}字，建议1000字以上效果更好"
            })
        
        # 关键词密度
        if target_keywords:
            word_freq = {}
            for word in words:
                word_lower = word.lower()
                word_freq[word_lower] = word_freq.get(word_lower, 0) + 1
            
            for keyword in target_keywords:
                keyword_lower = keyword.lower()
                count = word_freq.get(keyword_lower, 0)
                density = (count / len(words)) * 100 if words else 0
                result.keyword_density[keyword] = density
                
                if density < 0.5:
                    result.issues.append({
                        "type": "keyword",
                        "severity": "warning",
                        "message": f"关键词'{keyword}'密度过低: {density:.2f}%"
                    })
                elif density > 3:
                    result.issues.append({
                        "type": "keyword",
                        "severity": "warning",
                        "message": f"关键词'{keyword}'密度过高: {density:.2f}%，可能被判定为关键词堆砌"
                    })
    
    def _calculate_scores(self, result: SEOAnalysisResult):
        """计算SEO分数"""
        # 内容分数
        content_score = 100
        
        # 根据问题扣分
        for issue in result.issues:
            if issue['type'] in ('title', 'description', 'headings', 'content', 'keyword'):
                if issue['severity'] == 'error':
                    content_score -= 20
                elif issue['severity'] == 'warning':
                    content_score -= 10
                elif issue['severity'] == 'info':
                    content_score -= 5
        
        result.content_score = max(0, min(100, content_score))
        
        # 技术分数
        technical_score = 100
        for issue in result.issues:
            if issue['type'] in ('canonical', 'og', 'images', 'links'):
                if issue['severity'] == 'error':
                    technical_score -= 15
                elif issue['severity'] == 'warning':
                    technical_score -= 8
                elif issue['severity'] == 'info':
                    technical_score -= 3
        
        result.technical_score = max(0, min(100, technical_score))
        
        # 性能分数（默认值，需要实际检测）
        result.performance_score = 70
        
        # 综合分数
        result.overall_score = int(
            result.content_score * 0.4 +
            result.technical_score * 0.3 +
            result.performance_score * 0.3
        )
    
    def _generate_recommendations(self, result: SEOAnalysisResult):
        """生成优化建议"""
        # 根据问题生成建议
        for issue in result.issues:
            recommendation = self._get_recommendation(issue)
            if recommendation:
                result.recommendations.append(recommendation)
    
    def _get_recommendation(self, issue: Dict) -> Optional[Dict]:
        """获取具体建议"""
        recommendations_map = {
            "title": {
                "suggestion": "优化页面标题，确保包含核心关键词，长度控制在30-60字符之间",
                "priority": "high"
            },
            "description": {
                "suggestion": "编写吸引人的meta描述，包含关键词，长度控制在70-160字符",
                "priority": "high"
            },
            "headings": {
                "suggestion": "优化标题结构，确保只有一个H1，标题层级不跳级",
                "priority": "medium"
            },
            "images": {
                "suggestion": "为所有图片添加描述性的alt属性，有助于图片SEO和可访问性",
                "priority": "medium"
            },
            "content": {
                "suggestion": "增加高质量内容，确保内容全面、有价值，包含相关关键词",
                "priority": "high"
            },
            "keyword": {
                "suggestion": "调整关键词密度，保持在0.5%-2%之间，自然融入内容",
                "priority": "medium"
            },
            "canonical": {
                "suggestion": "添加canonical标签，避免重复内容问题",
                "priority": "medium"
            },
            "og": {
                "suggestion": "添加Open Graph标签，优化社交媒体分享效果",
                "priority": "low"
            },
            "links": {
                "suggestion": "为链接添加描述性锚文本，有助于SEO和用户体验",
                "priority": "low"
            },
        }
        
        rec = recommendations_map.get(issue['type'])
        if rec:
            return {
                "type": issue['type'],
                "suggestion": rec['suggestion'],
                "priority": rec['priority'],
                "related_issue": issue['message']
            }
        return None


class SEOGenerator:
    """SEO内容生成器"""
    
    def __init__(self):
        pass
    
    async def generate_seo_title(
        self,
        content: str,
        keywords: List[str],
        language: str = "zh-CN",
        max_length: int = 60
    ) -> str:
        """生成SEO标题"""
        system_prompt = f"""你是一个SEO专家。请根据以下内容和关键词，生成一个吸引人的SEO标题。
要求：
1. 标题要包含主要关键词
2. 长度控制在{max_length}字符以内
3. 吸引人，提高点击率
4. 符合{language}语言的表达习惯
5. 只返回标题文本，不要添加任何解释"""
        
        prompt = f"""内容摘要：{content[:500]}
关键词：{', '.join(keywords)}

请生成SEO标题："""
        
        messages = [
            ChatMessage(role="system", content=system_prompt),
            ChatMessage(role="user", content=prompt)
        ]
        
        response = ai_manager.chat(
            messages=messages,
            temperature=0.7,
            max_tokens=100
        )
        
        title = response.content.strip()
        # 确保长度符合要求
        if len(title) > max_length:
            title = title[:max_length-3] + "..."
        
        return title
    
    async def generate_meta_description(
        self,
        content: str,
        keywords: List[str],
        language: str = "zh-CN",
        max_length: int = 160
    ) -> str:
        """生成meta描述"""
        system_prompt = f"""你是一个SEO专家。请根据以下内容和关键词，生成一个吸引人的meta描述。
要求：
1. 描述要包含主要关键词
2. 长度控制在{max_length}字符以内
3. 吸引人，提高点击率
4. 准确概括页面内容
5. 符合{language}语言的表达习惯
6. 只返回描述文本，不要添加任何解释"""
        
        prompt = f"""内容摘要：{content[:1000]}
关键词：{', '.join(keywords)}

请生成meta描述："""
        
        messages = [
            ChatMessage(role="system", content=system_prompt),
            ChatMessage(role="user", content=prompt)
        ]
        
        response = ai_manager.chat(
            messages=messages,
            temperature=0.7,
            max_tokens=200
        )
        
        description = response.content.strip()
        # 确保长度符合要求
        if len(description) > max_length:
            description = description[:max_length-3] + "..."
        
        return description
    
    async def optimize_content(
        self,
        content: str,
        keywords: List[str],
        language: str = "zh-CN",
        optimization_type: str = "balanced"
    ) -> str:
        """优化内容的SEO"""
        system_prompt = f"""你是一个SEO内容优化专家。请对以下内容进行SEO优化。
要求：
1. 自然融入关键词，关键词密度保持在1%-2%
2. 保持内容原意和可读性
3. 优化标题结构（H1-H6）
4. 添加相关的内部链接锚文本建议
5. 改善内容的结构和逻辑
6. 符合{language}语言的表达习惯
7. 优化类型：{optimization_type}（balanced/max_seo/readability）
8. 只返回优化后的内容，不要添加任何解释"""
        
        prompt = f"""原始内容：
{content}

关键词：{', '.join(keywords)}

请进行SEO优化："""
        
        messages = [
            ChatMessage(role="system", content=system_prompt),
            ChatMessage(role="user", content=prompt)
        ]
        
        response = ai_manager.chat(
            messages=messages,
            temperature=0.5,
            max_tokens=4000
        )
        
        return response.content.strip()


class SiteSpeedOptimizer:
    """网站速度优化器"""
    
    def __init__(self):
        pass
    
    def get_optimization_suggestions(self, site_data: Dict) -> List[Dict]:
        """获取速度优化建议"""
        suggestions = []
        
        # 图片优化
        suggestions.append({
            "category": "images",
            "title": "图片压缩与WebP格式",
            "description": "压缩图片并转换为WebP格式可以显著减少图片大小，加快加载速度",
            "priority": "high",
            "impact": "high",
            "effort": "medium",
            "tools": ["WPForge Image Optimizer", "ShortPixel", "Smush"]
        })
        
        # 缓存
        suggestions.append({
            "category": "caching",
            "title": "配置页面缓存",
            "description": "启用页面缓存可以大幅减少服务器响应时间，提升访问速度",
            "priority": "high",
            "impact": "high",
            "effort": "medium",
            "tools": ["WP Rocket", "W3 Total Cache", "LiteSpeed Cache"]
        })
        
        # CDN
        suggestions.append({
            "category": "cdn",
            "title": "配置CDN加速",
            "description": "使用CDN分发静态资源，减少延迟，提升全球访问速度",
            "priority": "high",
            "impact": "high",
            "effort": "medium",
            "tools": ["Cloudflare", "StackPath", "KeyCDN"]
        })
        
        # 懒加载
        suggestions.append({
            "category": "lazyload",
            "title": "图片懒加载",
            "description": "延迟加载视窗外的图片，加快首屏加载速度",
            "priority": "medium",
            "impact": "medium",
            "effort": "low",
            "tools": ["原生loading='lazy'", "Lazy Load插件"]
        })
        
        # 数据库优化
        suggestions.append({
            "category": "database",
            "title": "数据库优化",
            "description": "清理修订版本、垃圾评论、过期瞬态等，优化数据库性能",
            "priority": "medium",
            "impact": "medium",
            "effort": "low",
            "tools": ["WP-Optimize", "WP-Sweep"]
        })
        
        # GZIP压缩
        suggestions.append({
            "category": "compression",
            "title": "启用GZIP/Brotli压缩",
            "description": "压缩文本资源可以减少传输大小，加快加载速度",
            "priority": "medium",
            "impact": "medium",
            "effort": "low",
            "tools": [".htaccess配置", "Nginx配置", "CDN配置"]
        })
        
        # 字体优化
        suggestions.append({
            "category": "fonts",
            "title": "字体优化",
            "description": "预加载关键字体，使用字体子集化，减少字体文件大小",
            "priority": "low",
            "impact": "medium",
            "effort": "medium",
            "tools": ["font-display: swap", "Google Fonts优化"]
        })
        
        # Heartbeat控制
        suggestions.append({
            "category": "heartbeat",
            "title": "控制Heartbeat API",
            "description": "降低WordPress Heartbeat频率，减少服务器负载",
            "priority": "low",
            "impact": "low",
            "effort": "low",
            "tools": ["Heartbeat Control插件"]
        })
        
        # 修订版本控制
        suggestions.append({
            "category": "revisions",
            "title": "限制修订版本数量",
            "description": "限制文章修订版本数量，减少数据库体积",
            "priority": "low",
            "impact": "low",
            "effort": "low",
            "tools": ["wp-config.php配置", "插件"]
        })
        
        return suggestions
    
    def generate_htaccess_rules(self, optimizations: List[str]) -> str:
        """生成.htaccess优化规则"""
        rules = []
        
        rules.append("# BEGIN WPForge SEO Optimization")
        rules.append("")
        
        # GZIP压缩
        if "gzip" in optimizations or "compression" in optimizations:
            rules.append("# GZIP Compression")
            rules.append("<IfModule mod_deflate.c>")
            rules.append("    AddOutputFilterByType DEFLATE text/plain")
            rules.append("    AddOutputFilterByType DEFLATE text/html")
            rules.append("    AddOutputFilterByType DEFLATE text/xml")
            rules.append("    AddOutputFilterByType DEFLATE text/css")
            rules.append("    AddOutputFilterByType DEFLATE application/xml")
            rules.append("    AddOutputFilterByType DEFLATE application/xhtml+xml")
            rules.append("    AddOutputFilterByType DEFLATE application/rss+xml")
            rules.append("    AddOutputFilterByType DEFLATE application/javascript")
            rules.append("    AddOutputFilterByType DEFLATE application/x-javascript")
            rules.append("</IfModule>")
            rules.append("")
        
        # 浏览器缓存
        if "caching" in optimizations:
            rules.append("# Browser Caching")
            rules.append("<IfModule mod_expires.c>")
            rules.append("    ExpiresActive On")
            rules.append("    ExpiresByType image/jpg \"access plus 1 year\"")
            rules.append("    ExpiresByType image/jpeg \"access plus 1 year\"")
            rules.append("    ExpiresByType image/gif \"access plus 1 year\"")
            rules.append("    ExpiresByType image/png \"access plus 1 year\"")
            rules.append("    ExpiresByType image/webp \"access plus 1 year\"")
            rules.append("    ExpiresByType text/css \"access plus 1 month\"")
            rules.append("    ExpiresByType application/pdf \"access plus 1 month\"")
            rules.append("    ExpiresByType text/javascript \"access plus 1 month\"")
            rules.append("    ExpiresByType application/javascript \"access plus 1 month\"")
            rules.append("    ExpiresByType application/x-javascript \"access plus 1 month\"")
            rules.append("    ExpiresByType image/x-icon \"access plus 1 year\"")
            rules.append("</IfModule>")
            rules.append("")
        
        rules.append("# END WPForge SEO Optimization")
        
        return "\n".join(rules)


# 全局实例
seo_analyzer = SEOAnalyzer()
seo_generator = SEOGenerator()
site_speed_optimizer = SiteSpeedOptimizer()
