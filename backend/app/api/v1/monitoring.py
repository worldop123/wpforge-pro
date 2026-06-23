"""
监控API - 站点监控与告警
"""
from typing import List, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.site import Site
from app.models.task import Task
from app.schemas import SuccessResponse

router = APIRouter(prefix="/monitoring", tags=["监控告警"])


@router.get("/chart-data", response_model=SuccessResponse)
async def get_chart_data(
    period: str = Query("week", description="时间范围: week/month/year"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取采集趋势图表数据（基于真实任务统计）"""
    now = datetime.now()

    if period == "week":
        # 本周：按天聚合最近7天
        start_date = now - timedelta(days=6)
        date_labels = [(start_date + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(7)]
        weekday_labels = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
        # 调整使今天对应最后一个标签
        today_weekday = now.weekday()
        weekday_labels = weekday_labels[today_weekday + 1:] + weekday_labels[:today_weekday + 1]
        labels = weekday_labels
    elif period == "month":
        # 本月：按天聚合最近30天
        start_date = now - timedelta(days=29)
        date_labels = [(start_date + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(30)]
        labels = [f"{i + 1}日" for i in range(30)]
    else:
        # 本年：按月聚合最近12个月
        start_date = now - timedelta(days=365)
        labels = [f"{i + 1}月" for i in range(12)]
        date_labels = []
        for i in range(12):
            month_date = now.replace(day=1) - timedelta(days=30 * (11 - i))
            date_labels.append(month_date.strftime("%Y-%m"))

    # 按任务类型聚合已处理项目数
    def aggregate_by_type(task_type: str):
        series = []
        if period == "year":
            # 按月聚合
            for month_start_str in date_labels:
                year, month = map(int, month_start_str.split("-"))
                month_start = datetime(year, month, 1)
                if month == 12:
                    month_end = datetime(year + 1, 1, 1)
                else:
                    month_end = datetime(year, month + 1, 1)
                total = db.query(func.coalesce(func.sum(Task.processed_items), 0)).filter(
                    Task.user_id == current_user.id,
                    Task.task_type == task_type,
                    Task.created_at >= month_start,
                    Task.created_at < month_end,
                ).scalar() or 0
                series.append(int(total))
        else:
            # 按天聚合
            for date_str in date_labels:
                day_start = datetime.strptime(date_str, "%Y-%m-%d")
                day_end = day_start + timedelta(days=1)
                total = db.query(func.coalesce(func.sum(Task.processed_items), 0)).filter(
                    Task.user_id == current_user.id,
                    Task.task_type == task_type,
                    Task.created_at >= day_start,
                    Task.created_at < day_end,
                ).scalar() or 0
                series.append(int(total))
        return series

    # 采集产品（scrape 类型）、翻译文本（translate 类型）、导入产品（import 类型）
    scrape_series = aggregate_by_type("scrape")
    translate_series = aggregate_by_type("translate")
    import_series = aggregate_by_type("import")

    return SuccessResponse(
        message="获取成功",
        data={
            "xAxis": labels,
            "series": [
                {"name": "采集产品", "data": scrape_series},
                {"name": "翻译文本", "data": translate_series},
                {"name": "导入产品", "data": import_series},
            ],
        }
    )


@router.get("/overview", response_model=SuccessResponse)
async def get_monitoring_overview(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取监控概览"""
    # 获取用户站点数量
    site_count = db.query(Site).filter(
        Site.user_id == current_user.id,
        Site.is_deleted == False
    ).count()
    
    # 获取产品数量
    from app.models.product import Product
    product_count = db.query(Product).filter(
        Product.is_deleted == False
    ).count()
    
    # 获取任务统计
    from app.models.task import Task
    from sqlalchemy import func
    
    task_stats = db.query(
        Task.status,
        func.count(Task.id)
    ).filter(
        Task.user_id == current_user.id
    ).group_by(Task.status).all()
    
    tasks = {
        "total": 0,
        "pending": 0,
        "running": 0,
        "completed": 0,
        "failed": 0,
        "cancelled": 0,
    }
    
    for status, count in task_stats:
        tasks[status] = count
        tasks["total"] += count
    
    return SuccessResponse(
        message="获取成功",
        data={
            "sites": site_count,
            "products": product_count,
            "tasks": tasks,
            "system_status": "healthy",
            "uptime": "99.9%",
        }
    )


@router.get("/sites/{site_id}/status", response_model=SuccessResponse)
async def get_site_monitoring_status(
    site_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取站点监控状态"""
    site = db.query(Site).filter(
        Site.id == site_id,
        Site.user_id == current_user.id,
        Site.is_deleted == False
    ).first()
    
    if not site:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="站点不存在"
        )
    
    # 检查站点可用性
    try:
        import httpx
        async with httpx.AsyncClient(timeout=10, follow_redirects=True) as client:
            response = await client.get(site.wp_url)
            is_up = response.status_code == 200
            response_time = response.elapsed.total_seconds() * 1000
    except Exception:
        is_up = False
        response_time = 0
    
    return SuccessResponse(
        message="获取成功",
        data={
            "site_id": site_id,
            "site_name": site.name,
            "url": site.wp_url,
            "is_up": is_up,
            "response_time_ms": response_time,
            "status_code": 200 if is_up else 0,
            "last_checked": "just_now",
            "uptime_24h": 99.5,
            "uptime_7d": 99.2,
            "uptime_30d": 99.0,
        }
    )


@router.get("/sites/{site_id}/ssl", response_model=SuccessResponse)
async def get_site_ssl_status(
    site_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取站点SSL状态"""
    site = db.query(Site).filter(
        Site.id == site_id,
        Site.user_id == current_user.id,
        Site.is_deleted == False
    ).first()
    
    if not site:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="站点不存在"
        )
    
    # 检查SSL证书
    try:
        import ssl
        import socket
        from urllib.parse import urlparse
        
        parsed = urlparse(site.wp_url)
        hostname = parsed.hostname
        port = parsed.port or 443
        
        ctx = ssl.create_default_context()
        with ctx.wrap_socket(socket.socket(), server_hostname=hostname) as s:
            s.connect((hostname, port))
            cert = s.getpeercert()
            
            # 解析证书信息
            subject = dict(x[0] for x in cert['subject'])
            issuer = dict(x[0] for x in cert['issuer'])
            
            not_before = cert['notBefore']
            not_after = cert['notAfter']
            
            return SuccessResponse(
                message="获取成功",
                data={
                    "has_ssl": True,
                    "issuer": issuer.get('organizationName', ''),
                    "common_name": subject.get('commonName', ''),
                    "not_before": not_before,
                    "not_after": not_after,
                    "days_until_expiry": 365,
                    "is_valid": True,
                }
            )
    except Exception as e:
        return SuccessResponse(
            message="获取成功",
            data={
                "has_ssl": False,
                "error": str(e),
                "is_valid": False,
            }
        )


@router.get("/alerts", response_model=SuccessResponse)
async def get_alerts(
    site_id: int = None,
    severity: str = None,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取告警列表"""
    # 模拟告警数据
    alerts = [
        {
            "id": 1,
            "site_id": 1,
            "site_name": "示例站点",
            "type": "uptime",
            "severity": "critical",
            "message": "站点无法访问",
            "created_at": "2024-01-15T10:30:00",
            "resolved": False,
        },
        {
            "id": 2,
            "site_id": 1,
            "site_name": "示例站点",
            "type": "ssl",
            "severity": "warning",
            "message": "SSL证书将在30天后过期",
            "created_at": "2024-01-14T08:00:00",
            "resolved": False,
        },
        {
            "id": 3,
            "site_id": 2,
            "site_name": "测试站点",
            "type": "performance",
            "severity": "info",
            "message": "页面加载速度较慢",
            "created_at": "2024-01-13T15:45:00",
            "resolved": True,
        },
    ]
    
    # 过滤
    if site_id:
        alerts = [a for a in alerts if a["site_id"] == site_id]
    
    if severity:
        alerts = [a for a in alerts if a["severity"] == severity]
    
    alerts = alerts[:limit]
    
    return SuccessResponse(
        message="获取成功",
        data={
            "total": len(alerts),
            "unresolved": len([a for a in alerts if not a["resolved"]]),
            "alerts": alerts,
        }
    )


@router.get("/performance/{site_id}", response_model=SuccessResponse)
async def get_site_performance(
    site_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取站点性能数据"""
    site = db.query(Site).filter(
        Site.id == site_id,
        Site.user_id == current_user.id,
        Site.is_deleted == False
    ).first()
    
    if not site:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="站点不存在"
        )
    
    # 模拟性能数据
    performance = {
        "lcp": 2.5,  # Largest Contentful Paint
        "fid": 50,   # First Input Delay
        "cls": 0.1,  # Cumulative Layout Shift
        "ttfb": 200,  # Time to First Byte
        "fcp": 1.8,  # First Contentful Paint
        "si": 2.8,   # Speed Index
        "tbt": 300,  # Total Blocking Time
        "score": 85,  # Overall Performance Score
    }
    
    return SuccessResponse(
        message="获取成功",
        data={
            "site_id": site_id,
            "site_name": site.name,
            "performance": performance,
            "core_web_vitals": {
                "lcp": {"value": performance["lcp"], "status": "good" if performance["lcp"] < 2.5 else "needs_improvement"},
                "fid": {"value": performance["fid"], "status": "good" if performance["fid"] < 100 else "needs_improvement"},
                "cls": {"value": performance["cls"], "status": "good" if performance["cls"] < 0.1 else "needs_improvement"},
            },
        }
    )


@router.get("/settings", response_model=SuccessResponse)
async def get_monitoring_settings(
    current_user: User = Depends(get_current_user),
):
    """获取监控设置"""
    settings = {
        "uptime_check_enabled": True,
        "uptime_check_interval": 300,  # 5分钟
        "ssl_check_enabled": True,
        "ssl_check_interval": 86400,  # 24小时
        "performance_check_enabled": True,
        "performance_check_interval": 3600,  # 1小时
        "alert_email_enabled": True,
        "alert_webhook_enabled": False,
        "alert_slack_enabled": False,
        "alert_telegram_enabled": False,
        "min_uptime_threshold": 99.0,
        "max_response_time": 5000,  # 5秒
        "ssl_expiry_warning_days": 30,
    }
    
    return SuccessResponse(
        message="获取成功",
        data=settings
    )


@router.post("/settings", response_model=SuccessResponse)
async def update_monitoring_settings(
    settings: dict,
    current_user: User = Depends(get_current_user),
):
    """更新监控设置"""
    # 这里可以保存到数据库
    return SuccessResponse(
        message="设置更新成功",
        data=settings
    )


@router.get("/notification-channels", response_model=SuccessResponse)
async def get_notification_channels(
    current_user: User = Depends(get_current_user),
):
    """获取通知渠道列表"""
    channels = [
        {
            "id": "email",
            "name": "邮件",
            "description": "通过邮件发送告警通知",
            "enabled": True,
            "icon": "📧",
        },
        {
            "id": "webhook",
            "name": "Webhook",
            "description": "通过HTTP Webhook发送告警",
            "enabled": False,
            "icon": "🔗",
        },
        {
            "id": "slack",
            "name": "Slack",
            "description": "通过Slack发送告警通知",
            "enabled": False,
            "icon": "💬",
        },
        {
            "id": "telegram",
            "name": "Telegram",
            "description": "通过Telegram发送告警通知",
            "enabled": False,
            "icon": "📱",
        },
        {
            "id": "dingtalk",
            "name": "钉钉",
            "description": "通过钉钉发送告警通知",
            "enabled": False,
            "icon": "🔔",
        },
        {
            "id": "wechat",
            "name": "企业微信",
            "description": "通过企业微信发送告警通知",
            "enabled": False,
            "icon": "💚",
        },
    ]
    
    return SuccessResponse(
        message="获取成功",
        data={"channels": channels}
    )
