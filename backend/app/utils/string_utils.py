"""
字符串处理工具函数
"""
import re
import hashlib
from urllib.parse import urlparse
from slugify import slugify as _slugify
from bs4 import BeautifulSoup


def clean_text(text: str) -> str:
    """清理文本，去除多余空白和特殊字符"""
    if not text:
        return ""
    
    # 去除HTML标签
    text = remove_html_tags(text)
    
    # 替换多个空白字符为单个空格
    text = re.sub(r'\s+', ' ', text)
    
    # 去除首尾空白
    text = text.strip()
    
    return text


def extract_domain(url: str) -> str:
    """从URL中提取域名"""
    if not url:
        return ""
    
    try:
        parsed = urlparse(url)
        domain = parsed.netloc
        # 去除www前缀
        if domain.startswith('www.'):
            domain = domain[4:]
        return domain
    except Exception:
        return ""


def generate_slug(text: str, max_length: int = 200) -> str:
    """生成URL友好的slug"""
    if not text:
        return ""
    
    slug = _slugify(text)
    
    # 限制长度
    if len(slug) > max_length:
        slug = slug[:max_length]
        # 确保不在单词中间截断
        if '-' in slug:
            slug = slug.rsplit('-', 1)[0]
    
    return slug


def truncate_string(text: str, max_length: int = 100, suffix: str = '...') -> str:
    """截断字符串到指定长度"""
    if not text:
        return ""
    
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix


def remove_html_tags(html: str) -> str:
    """移除HTML标签"""
    if not html:
        return ""
    
    try:
        soup = BeautifulSoup(html, 'html.parser')
        return soup.get_text(separator=' ', strip=True)
    except Exception:
        # 如果解析失败，使用正则表达式
        text = re.sub(r'<[^>]+>', '', html)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()


def normalize_url(url: str) -> str:
    """标准化URL格式"""
    if not url:
        return ""
    
    url = url.strip()
    
    # 添加协议
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    # 去除末尾斜杠
    url = url.rstrip('/')
    
    return url


def generate_hash(text: str, algorithm: str = 'md5') -> str:
    """生成字符串的哈希值"""
    if not text:
        return ""
    
    if algorithm == 'md5':
        return hashlib.md5(text.encode('utf-8')).hexdigest()
    elif algorithm == 'sha1':
        return hashlib.sha1(text.encode('utf-8')).hexdigest()
    elif algorithm == 'sha256':
        return hashlib.sha256(text.encode('utf-8')).hexdigest()
    else:
        return hashlib.md5(text.encode('utf-8')).hexdigest()


def extract_numbers(text: str) -> list:
    """从文本中提取所有数字"""
    if not text:
        return []
    
    return re.findall(r'\d+\.?\d*', text)


def camel_to_snake(name: str) -> str:
    """驼峰命名转下划线命名"""
    pattern = re.compile(r'(?<!^)(?=[A-Z])')
    return pattern.sub('_', name).lower()


def snake_to_camel(name: str) -> str:
    """下划线命名转驼峰命名"""
    components = name.split('_')
    return components[0] + ''.join(x.title() for x in components[1:])
