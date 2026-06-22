"""
测试配置文件
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.core.config import settings
from app.core.database import Base, get_db
from app.main import app
from app.models import *  # noqa: F401, F403

# 使用 SQLite 内存数据库进行测试
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session")
def db_engine():
    """创建数据库引擎"""
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db(db_engine):
    """创建数据库会话"""
    connection = db_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def client(db):
    """创建测试客户端"""

    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def test_user(db):
    """创建测试用户"""
    from app.models.user import User
    from app.core.security import get_password_hash

    user = User(
        username="testuser",
        email="test@example.com",
        password_hash=get_password_hash("testpassword123"),
        is_active=True,
        role="user",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def test_admin(db):
    """创建测试管理员"""
    from app.models.user import User
    from app.core.security import get_password_hash

    admin = User(
        username="admin",
        email="admin@example.com",
        password_hash=get_password_hash("adminpassword123"),
        is_active=True,
        role="admin",
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)
    return admin


@pytest.fixture
def auth_headers(client, test_user):
    """获取认证头"""
    response = client.post(
        "/api/v1/auth/login",
        json={"username": "testuser", "password": "testpassword123"},
    )
    token = response.json()["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def admin_auth_headers(client, test_admin):
    """获取管理员认证头"""
    response = client.post(
        "/api/v1/auth/login",
        json={"username": "admin", "password": "adminpassword123"},
    )
    token = response.json()["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def test_site(db, test_user):
    """创建测试站点"""
    from app.models.site import Site

    site = Site(
        name="Test Site",
        url="https://test.example.com",
        wp_username="admin",
        wp_password="password",
        wp_api_key="test_api_key",
        language="zh-CN",
        currency="CNY",
        page_builder="elementor",
        user_id=test_user.id,
        is_active=True,
    )
    db.add(site)
    db.commit()
    db.refresh(site)
    return site


@pytest.fixture
def test_product(db, test_user, test_site):
    """创建测试产品"""
    from app.models.product import Product

    product = Product(
        title="Test Product",
        description="This is a test product description.",
        short_description="Short description.",
        price="99.99",
        regular_price="129.99",
        sale_price="99.99",
        stock_quantity=100,
        sku="TEST-001",
        status="draft",
        source_url="https://example.com/product/test",
        site_id=test_site.id,
        user_id=test_user.id,
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


@pytest.fixture
def test_task(db, test_user, test_site):
    """创建测试任务"""
    from app.models.task import Task

    task = Task(
        name="Test Task",
        type="scraping",
        status="pending",
        progress=0,
        site_id=test_site.id,
        user_id=test_user.id,
        params={"url": "https://example.com", "max_products": 10},
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task
