"""
验证工具函数
"""
import re
import json
from typing import Optional
from urllib.parse import urlparse


def is_valid_url(url: str) -> bool:
    """验证URL是否有效"""
    if not url:
        return False
    
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


def is_valid_email(email: str) -> bool:
    """验证邮箱是否有效"""
    if not email:
        return False
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def is_valid_ip(ip: str) -> bool:
    """验证IP地址是否有效（支持IPv4和IPv6）"""
    if not ip:
        return False
    
    # IPv4验证
    ipv4_pattern = r'^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
    if re.match(ipv4_pattern, ip):
        return True
    
    # IPv6验证（简化版）
    ipv6_pattern = r'^([0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}$'
    if re.match(ipv6_pattern, ip):
        return True
    
    return False


def is_valid_json(json_str: str) -> bool:
    """验证JSON字符串是否有效"""
    if not json_str:
        return False
    
    try:
        json.loads(json_str)
        return True
    except (json.JSONDecodeError, TypeError):
        return False


def is_valid_phone(phone: str, country: str = 'CN') -> bool:
    """验证手机号是否有效"""
    if not phone:
        return False
    
    # 移除空格和特殊字符
    phone = re.sub(r'[\s\-+()]', '', phone)
    
    if country == 'CN':
        # 中国大陆手机号
        pattern = r'^1[3-9]\d{9}$'
    elif country == 'US':
        # 美国手机号
        pattern = r'^1?\d{10}$'
    else:
        # 通用验证：至少7位数字
        pattern = r'^\d{7,15}$'
    
    return bool(re.match(pattern, phone))


def is_valid_password(password: str, min_length: int = 6, require_complexity: bool = False) -> bool:
    """验证密码强度"""
    if not password or len(password) < min_length:
        return False
    
    if require_complexity:
        # 必须包含大小写字母、数字和特殊字符
        has_upper = bool(re.search(r'[A-Z]', password))
        has_lower = bool(re.search(r'[a-z]', password))
        has_digit = bool(re.search(r'\d', password))
        has_special = bool(re.search(r'[!@#$%^&*(),.?":{}|<>]', password))
        
        return has_upper and has_lower and has_digit and has_special
    
    return True


def is_valid_username(username: str, min_length: int = 3, max_length: int = 50) -> bool:
    """验证用户名"""
    if not username:
        return False
    
    if len(username) < min_length or len(username) > max_length:
        return False
    
    # 只能包含字母、数字、下划线和连字符
    pattern = r'^[a-zA-Z0-9_-]+$'
    return bool(re.match(pattern, username))


def is_valid_domain(domain: str) -> bool:
    """验证域名是否有效"""
    if not domain:
        return False
    
    pattern = r'^([a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$'
    return bool(re.match(pattern, domain))


def is_valid_port(port: int) -> bool:
    """验证端口号是否有效"""
    if not isinstance(port, int):
        try:
            port = int(port)
        except (ValueError, TypeError):
            return False
    
    return 1 <= port <= 65535


def is_valid_hex_color(color: str) -> bool:
    """验证十六进制颜色值"""
    if not color:
        return False
    
    pattern = r'^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$'
    return bool(re.match(pattern, color))


def is_valid_date(date_str: str, fmt: str = '%Y-%m-%d') -> bool:
    """验证日期字符串"""
    if not date_str:
        return False
    
    try:
        from datetime import datetime
        datetime.strptime(date_str, fmt)
        return True
    except ValueError:
        return False


def is_valid_uuid(uuid_str: str) -> bool:
    """验证UUID格式"""
    if not uuid_str:
        return False
    
    pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
    return bool(re.match(pattern, uuid_str.lower()))


def sanitize_html(html: str) -> str:
    """清理HTML，移除危险标签和属性"""
    if not html:
        return ""
    
    # 移除script标签
    html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL | re.IGNORECASE)
    
    # 移除style标签
    html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL | re.IGNORECASE)
    
    # 移除iframe标签
    html = re.sub(r'<iframe[^>]*>.*?</iframe>', '', html, flags=re.DOTALL | re.IGNORECASE)
    
    # 移除on事件属性
    html = re.sub(r'\s+on\w+\s*=\s*"[^"]*"', '', html, flags=re.IGNORECASE)
    html = re.sub(r"\s+on\w+\s*=\s*'[^']*'", '', html, flags=re.IGNORECASE)
    
    # 移除javascript:协议
    html = re.sub(r'javascript:', '', html, flags=re.IGNORECASE)
    
    return html
