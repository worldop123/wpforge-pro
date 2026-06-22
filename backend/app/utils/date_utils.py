"""
日期时间工具函数
"""
from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple
import pytz


def format_datetime(dt: Optional[datetime], fmt: str = '%Y-%m-%d %H:%M:%S') -> str:
    """格式化日期时间"""
    if not dt:
        return ""
    
    if isinstance(dt, str):
        try:
            dt = parse_datetime(dt)
        except Exception:
            return dt
    
    return dt.strftime(fmt)


def parse_datetime(date_str: str, fmt: Optional[str] = None) -> Optional[datetime]:
    """解析日期时间字符串"""
    if not date_str:
        return None
    
    if fmt:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            pass
    
    # 尝试多种常见格式
    formats = [
        '%Y-%m-%d %H:%M:%S',
        '%Y-%m-%dT%H:%M:%S',
        '%Y-%m-%dT%H:%M:%SZ',
        '%Y-%m-%dT%H:%M:%S.%fZ',
        '%Y-%m-%d %H:%M',
        '%Y-%m-%d',
        '%d/%m/%Y %H:%M:%S',
        '%d/%m/%Y',
        '%m/%d/%Y %H:%M:%S',
        '%m/%d/%Y',
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    
    return None


def get_time_ago(dt: Optional[datetime]) -> str:
    """获取相对时间描述（如"5分钟前"）"""
    if not dt:
        return ""
    
    now = datetime.utcnow()
    if dt.tzinfo:
        now = datetime.now(timezone.utc)
        dt = dt.astimezone(timezone.utc)
    
    diff = now - dt
    
    seconds = diff.total_seconds()
    
    if seconds < 60:
        return "刚刚"
    elif seconds < 3600:
        minutes = int(seconds / 60)
        return f"{minutes}分钟前"
    elif seconds < 86400:
        hours = int(seconds / 3600)
        return f"{hours}小时前"
    elif seconds < 2592000:  # 30天
        days = int(seconds / 86400)
        return f"{days}天前"
    elif seconds < 31536000:  # 1年
        months = int(seconds / 2592000)
        return f"{months}个月前"
    else:
        years = int(seconds / 31536000)
        return f"{years}年前"


def get_date_range(days: int = 7, end_date: Optional[datetime] = None) -> Tuple[datetime, datetime]:
    """获取日期范围"""
    if end_date is None:
        end_date = datetime.utcnow()
    
    start_date = end_date - timedelta(days=days)
    
    return start_date, end_date


def convert_timezone(dt: datetime, from_tz: str = 'UTC', to_tz: str = 'Asia/Shanghai') -> datetime:
    """转换时区"""
    if dt.tzinfo is None:
        source_tz = pytz.timezone(from_tz)
        dt = source_tz.localize(dt)
    
    target_tz = pytz.timezone(to_tz)
    return dt.astimezone(target_tz)


def is_today(dt: datetime) -> bool:
    """判断是否是今天"""
    today = datetime.utcnow().date()
    return dt.date() == today


def is_this_week(dt: datetime) -> bool:
    """判断是否是本周"""
    now = datetime.utcnow()
    week_start = now - timedelta(days=now.weekday())
    week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)
    week_end = week_start + timedelta(days=7)
    return week_start <= dt < week_end


def is_this_month(dt: datetime) -> bool:
    """判断是否是本月"""
    now = datetime.utcnow()
    return dt.year == now.year and dt.month == now.month


def get_timestamp(dt: Optional[datetime] = None) -> int:
    """获取Unix时间戳"""
    if dt is None:
        dt = datetime.utcnow()
    
    return int(dt.timestamp())


def from_timestamp(timestamp: int) -> datetime:
    """从时间戳创建datetime"""
    return datetime.fromtimestamp(timestamp)
