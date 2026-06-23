"""
Funnel API - 电商漏斗数据
从已注册的 WordPress 站点拉取漏斗数据并聚合返回
"""
from datetime import date, timedelta
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.site import Site
from app.schemas import SuccessResponse

router = APIRouter(prefix="/funnel", tags=["电商漏斗"])

# 时间范围到 (start_date, end_date) 的映射
def _resolve_range(time_range: str):
    today = date.today()
    mapping = {
        "today": (today, today),
        "yesterday": (today - timedelta(days=1), today - timedelta(days=1)),
        "7days": (today - timedelta(days=6), today),
        "30days": (today - timedelta(days=29), today),
        "thisMonth": (today.replace(day=1), today),
        "lastMonth": (
            (today.replace(day=1) - timedelta(days=1)).replace(day=1),
            today.replace(day=1) - timedelta(days=1),
        ),
    }
    return mapping.get(time_range, (today - timedelta(days=29), today))


async def _call_wp_funnel(site: Site, path: str, params: dict) -> Optional[dict]:
    """调用单个 WordPress 站点的漏斗 REST API

    使用应用密码进行 HTTP Basic Auth 认证。
    任何异常都返回 None，由调用方处理聚合。
    """
    import httpx

    base = (site.wp_url or "").rstrip("/")
    url = f"{base}/wp-json/wpforge/v1/funnel/{path}"
    try:
        async with httpx.AsyncClient(
            auth=(site.wp_username or "", site.wp_password or ""),
            headers={"User-Agent": "WPForge/1.0"},
            timeout=15,
            follow_redirects=True,
        ) as client:
            resp = await client.get(url, params=params)
            if resp.status_code == 200:
                return resp.json()
            return None
    except Exception:
        return None


def _get_target_sites(db: Session, user: User, site_ids: Optional[List[int]]) -> List[Site]:
    """获取目标站点列表"""
    query = db.query(Site).filter(
        Site.user_id == user.id,
        Site.is_deleted == False,
        Site.status == "active",
    )
    if site_ids:
        query = query.filter(Site.id.in_(site_ids))
    return query.all()


@router.get("/overview", response_model=SuccessResponse)
async def get_funnel_overview(
    time_range: str = Query("30days", description="时间范围"),
    site_ids: Optional[str] = Query(None, description="站点ID列表，逗号分隔"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取漏斗概览数据（KPI + 漏斗层级 + 站点列表）"""
    ids = [int(x) for x in site_ids.split(",") if x.strip().isdigit()] if site_ids else None
    sites = _get_target_sites(db, current_user, ids)
    start_date, end_date = _resolve_range(time_range)
    params = {"start_date": start_date.isoformat(), "end_date": end_date.isoformat()}

    # 聚合指标
    agg = {
        "visitors": 0, "product_views": 0, "add_to_cart": 0,
        "checkout_starts": 0, "purchases": 0, "orders": 0,
        "revenue": 0.0, "avg_order_value": 0.0, "conversion_rate": 0.0,
    }
    site_list = []
    per_site = []

    import asyncio
    tasks = [_call_wp_funnel(s, "data", params) for s in sites]
    results = await asyncio.gather(*tasks, return_exceptions=False)

    for site, raw in zip(sites, results):
        site_list.append({"id": site.id, "name": site.name})
        if not raw or not raw.get("success"):
            per_site.append({"site_id": site.id, "site_name": site.name, "metrics": None})
            continue
        metrics = (raw.get("data") or {}).get("metrics") or {}
        for k in agg:
            if k in metrics and isinstance(metrics[k], (int, float)):
                agg[k] += metrics[k]
        per_site.append({
            "site_id": site.id,
            "site_name": site.name,
            "metrics": metrics,
        })

    # 计算派生指标
    visitors = agg["visitors"] or 0
    orders = agg["orders"] or agg["purchases"] or 0
    revenue = agg["revenue"] or 0.0
    agg["conversion_rate"] = round(visitors and (orders / visitors * 100), 2) or 0.0
    agg["avg_order_value"] = round(orders and (revenue / orders), 2) or 0.0

    # 构建漏斗层级
    stages = [
        {"name": "访客数", "key": "visitors", "value": agg["visitors"], "color": "#3b82f6", "conversion_from_prev": 100.0},
        {"name": "浏览产品", "key": "product_views", "value": agg["product_views"], "color": "#10b981",
         "conversion_from_prev": round(visitors and (agg["product_views"] / visitors * 100), 2) or 0.0},
        {"name": "加入购物车", "key": "add_to_cart", "value": agg["add_to_cart"], "color": "#f59e0b",
         "conversion_from_prev": round(agg["product_views"] and (agg["add_to_cart"] / agg["product_views"] * 100), 2) or 0.0},
        {"name": "开始结账", "key": "checkout_starts", "value": agg["checkout_starts"], "color": "#8b5cf6",
         "conversion_from_prev": round(agg["add_to_cart"] and (agg["checkout_starts"] / agg["add_to_cart"] * 100), 2) or 0.0},
        {"name": "完成购买", "key": "purchases", "value": agg["purchases"], "color": "#ef4444",
         "conversion_from_prev": round(agg["checkout_starts"] and (agg["purchases"] / agg["checkout_starts"] * 100), 2) or 0.0},
    ]

    return SuccessResponse(
        message="获取成功",
        data={
            "sites": site_list,
            "metrics": agg,
            "stages": stages,
            "per_site": per_site,
            "period": {"start": start_date.isoformat(), "end": end_date.isoformat()},
        },
    )


@router.get("/sales-trend", response_model=SuccessResponse)
async def get_funnel_sales_trend(
    time_range: str = Query("30days"),
    period: str = Query("day"),
    site_ids: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取销售趋势（按日期聚合所有站点）"""
    ids = [int(x) for x in site_ids.split(",") if x.strip().isdigit()] if site_ids else None
    sites = _get_target_sites(db, current_user, ids)
    start_date, end_date = _resolve_range(time_range)
    params = {
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "period": period,
    }

    import asyncio
    tasks = [_call_wp_funnel(s, "sales-trend", params) for s in sites]
    results = await asyncio.gather(*tasks, return_exceptions=False)

    # 按日期合并
    merged: dict = {}
    for raw in results:
        if not raw or not raw.get("success"):
            continue
        for item in (raw.get("data") or []):
            d = item.get("date")
            if not d:
                continue
            cur = merged.setdefault(d, {"date": d, "revenue": 0.0, "orders": 0, "visitors": 0})
            cur["revenue"] += float(item.get("revenue") or 0)
            cur["orders"] += int(item.get("orders") or 0)
            cur["visitors"] += int(item.get("visitors") or 0)

    trend = sorted(merged.values(), key=lambda x: x["date"])
    return SuccessResponse(message="获取成功", data=trend)


@router.get("/top-products", response_model=SuccessResponse)
async def get_funnel_top_products(
    time_range: str = Query("30days"),
    order_by: str = Query("sales"),
    limit: int = Query(10, ge=1, le=50),
    site_ids: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取热销产品（聚合所有站点）"""
    ids = [int(x) for x in site_ids.split(",") if x.strip().isdigit()] if site_ids else None
    sites = _get_target_sites(db, current_user, ids)
    start_date, end_date = _resolve_range(time_range)
    params = {
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "limit": limit,
        "order_by": order_by,
    }

    import asyncio
    tasks = [_call_wp_funnel(s, "top-products", params) for s in sites]
    results = await asyncio.gather(*tasks, return_exceptions=False)

    products = []
    for raw in results:
        if not raw or not raw.get("success"):
            continue
        for p in (raw.get("data") or []):
            products.append({
                "id": p.get("product_id") or p.get("id"),
                "name": p.get("name") or "未命名产品",
                "sales": int(p.get("purchases") or 0),
                "revenue": float(p.get("revenue") or 0),
                "views": int(p.get("views") or 0),
                "add_to_cart": int(p.get("add_to_cart") or 0),
                "abandonRate": round(float(p.get("abandonment_rate") or 0), 2),
                "amount": round(float(p.get("revenue") or 0), 2),
            })

    # 排序
    sort_key = {"sales": "sales", "revenue": "revenue", "cart": "add_to_cart", "views": "views"}.get(order_by, "sales")
    products.sort(key=lambda x: x.get(sort_key, 0), reverse=True)
    return SuccessResponse(message="获取成功", data=products[:limit])


@router.get("/insights", response_model=SuccessResponse)
async def get_funnel_insights(
    time_range: str = Query("30days"),
    site_ids: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取 AI 洞察（聚合所有站点）"""
    ids = [int(x) for x in site_ids.split(",") if x.strip().isdigit()] if site_ids else None
    sites = _get_target_sites(db, current_user, ids)
    start_date, end_date = _resolve_range(time_range)
    params = {"start_date": start_date.isoformat(), "end_date": end_date.isoformat()}

    import asyncio
    tasks = [_call_wp_funnel(s, "insights", params) for s in sites]
    results = await asyncio.gather(*tasks, return_exceptions=False)

    insights = []
    for raw in results:
        if not raw or not raw.get("success"):
            continue
        data = raw.get("data") or {}
        for ins in (data.get("insights") or []):
            insights.append(ins)

    return SuccessResponse(message="获取成功", data={"insights": insights, "total": len(insights)})


@router.get("/comparison", response_model=SuccessResponse)
async def get_funnel_comparison(
    time_range: str = Query("30days"),
    site_ids: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取站点对比数据"""
    ids = [int(x) for x in site_ids.split(",") if x.strip().isdigit()] if site_ids else None
    sites = _get_target_sites(db, current_user, ids)
    start_date, end_date = _resolve_range(time_range)
    params = {"start_date": start_date.isoformat(), "end_date": end_date.isoformat()}

    import asyncio
    tasks = [_call_wp_funnel(s, "data", params) for s in sites]
    results = await asyncio.gather(*tasks, return_exceptions=False)

    comparison = []
    for site, raw in zip(sites, results):
        metrics = (raw or {}).get("data", {}).get("metrics") if (raw or {}).get("success") else None
        if metrics:
            visitors = int(metrics.get("visitors") or 0)
            orders = int(metrics.get("orders") or metrics.get("purchases") or 0)
            revenue = float(metrics.get("revenue") or 0)
            comparison.append({
                "siteId": site.id,
                "siteName": site.name,
                "visitors": visitors,
                "productViews": int(metrics.get("product_views") or 0),
                "cartAdds": int(metrics.get("add_to_cart") or 0),
                "checkouts": int(metrics.get("checkout_starts") or 0),
                "orders": orders,
                "revenue": round(revenue, 2),
                "conversionRate": round(visitors and (orders / visitors * 100), 2) or 0.0,
                "avgOrderValue": round(orders and (revenue / orders), 2) or 0.0,
            })
        else:
            comparison.append({
                "siteId": site.id, "siteName": site.name,
                "visitors": 0, "productViews": 0, "cartAdds": 0,
                "checkouts": 0, "orders": 0, "revenue": 0,
                "conversionRate": 0.0, "avgOrderValue": 0.0,
            })

    return SuccessResponse(message="获取成功", data=comparison)
