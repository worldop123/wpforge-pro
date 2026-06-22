"""
产品管理API - 产品的增删改查
"""
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.product import Product
from app.schemas import (
    ProductCreate,
    ProductUpdate,
    ProductResponse,
    ProductListResponse,
    SuccessResponse,
)

router = APIRouter(prefix="/products", tags=["产品管理"])


@router.get("", response_model=ProductListResponse)
async def list_products(
    site_id: Optional[int] = Query(None, description="站点ID过滤"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=200, description="每页数量"),
    status: Optional[str] = Query(None, description="状态过滤"),
    translated: Optional[bool] = Query(None, description="是否已翻译"),
    search: Optional[str] = Query(None, description="搜索关键词"),
    category: Optional[str] = Query(None, description="分类过滤"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取产品列表"""
    query = db.query(Product).filter(Product.is_deleted == False)
    
    # 站点过滤
    if site_id:
        # 验证站点属于当前用户
        from app.models.site import Site
        site = db.query(Site).filter(
            Site.id == site_id,
            Site.user_id == current_user.id,
            Site.is_deleted == False
        ).first()
        if not site:
            raise HTTPException(status_code=404, detail="站点不存在")
        query = query.filter(Product.site_id == site_id)
    
    # 状态过滤
    if status:
        query = query.filter(Product.status == status)
    
    # 翻译状态过滤
    if translated is not None:
        query = query.filter(Product.translated == translated)
    
    # 搜索
    if search:
        query = query.filter(
            Product.name.ilike(f"%{search}%") |
            Product.sku.ilike(f"%{search}%")
        )
    
    # 总数
    total = query.count()
    
    # 分页
    products = query.order_by(Product.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    
    return ProductListResponse(
        items=[ProductResponse.model_validate(p) for p in products],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.post("", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    product_data: ProductCreate,
    site_id: Optional[int] = Query(None, description="站点ID"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """创建产品"""
    # 验证站点
    if site_id:
        from app.models.site import Site
        site = db.query(Site).filter(
            Site.id == site_id,
            Site.user_id == current_user.id,
            Site.is_deleted == False
        ).first()
        if not site:
            raise HTTPException(status_code=404, detail="站点不存在")
    
    # 生成slug
    from slugify import slugify
    slug = slugify(product_data.name)
    
    product = Product(
        name=product_data.name,
        sku=product_data.sku,
        slug=slug,
        description=product_data.description,
        short_description=product_data.short_description,
        regular_price=product_data.regular_price,
        sale_price=product_data.sale_price,
        price=product_data.sale_price or product_data.regular_price,
        currency=product_data.currency,
        stock_quantity=product_data.stock_quantity,
        in_stock=product_data.in_stock,
        categories=product_data.categories,
        tags=product_data.tags,
        images=product_data.images,
        attributes=product_data.attributes,
        variations=product_data.variations,
        is_variable=product_data.is_variable,
        source_url=product_data.source_url,
        source_site=product_data.source_site,
        site_id=site_id,
        status="draft",
        wp_status="draft",
    )
    
    db.add(product)
    db.commit()
    db.refresh(product)
    
    return ProductResponse.model_validate(product)


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取产品详情"""
    product = db.query(Product).filter(
        Product.id == product_id,
        Product.is_deleted == False
    ).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="产品不存在"
        )
    
    return ProductResponse.model_validate(product)


@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: int,
    product_data: ProductUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """更新产品"""
    product = db.query(Product).filter(
        Product.id == product_id,
        Product.is_deleted == False
    ).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="产品不存在"
        )
    
    # 更新字段
    update_data = product_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        if value is not None:
            setattr(product, key, value)
    
    db.commit()
    db.refresh(product)
    
    return ProductResponse.model_validate(product)


@router.delete("/{product_id}", response_model=SuccessResponse)
async def delete_product(
    product_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """删除产品（软删除）"""
    product = db.query(Product).filter(
        Product.id == product_id,
        Product.is_deleted == False
    ).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="产品不存在"
        )
    
    product.is_deleted = True
    product.status = "trash"
    db.commit()
    
    return SuccessResponse(message="产品已删除")


@router.post("/batch-delete", response_model=SuccessResponse)
async def batch_delete_products(
    product_ids: List[int],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """批量删除产品"""
    products = db.query(Product).filter(
        Product.id.in_(product_ids),
        Product.is_deleted == False
    ).all()
    
    for product in products:
        product.is_deleted = True
        product.status = "trash"
    
    db.commit()
    
    return SuccessResponse(message=f"已删除 {len(products)} 个产品")
