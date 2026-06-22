"""
认证 API 测试

实际 API 行为：
- /auth/login 使用 OAuth2PasswordRequestForm（表单数据），返回 Token（access_token 在顶层）
- /auth/register 返回 UserResponse（顶层，无 success/data 包装）
- /auth/me 返回 UserResponse
- /auth/logout 返回 SuccessResponse（含 success/message）
- /auth/refresh 返回 Token
- /auth/change-password 不存在（404）
"""
import pytest


def test_login_success(client, test_user):
    """测试登录成功"""
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "testuser", "password": "testpassword123"},
    )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["username"] == "testuser"


def test_login_wrong_password(client, test_user):
    """测试密码错误"""
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "testuser", "password": "wrongpassword"},
    )

    assert response.status_code == 401
    data = response.json()
    assert "detail" in data


def test_login_wrong_username(client):
    """测试用户名不存在"""
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "nonexistent", "password": "testpassword123"},
    )

    assert response.status_code == 401


def test_login_missing_fields(client):
    """测试缺少必填字段（表单缺少 password）"""
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "testuser"},
    )

    assert response.status_code == 422


def test_get_current_user(client, auth_headers):
    """测试获取当前用户信息"""
    response = client.get(
        "/api/v1/auth/me",
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser"


def test_get_current_user_no_auth(client):
    """测试未认证时获取用户信息"""
    response = client.get("/api/v1/auth/me")

    assert response.status_code == 401


def test_logout(client, auth_headers):
    """测试登出"""
    response = client.post(
        "/api/v1/auth/logout",
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True


def test_refresh_token(client, auth_headers):
    """测试刷新令牌"""
    response = client.post(
        "/api/v1/auth/refresh",
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_register_success(client):
    """测试注册成功"""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "username": "newuser",
            "email": "new@example.com",
            "password": "newpassword123",
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "newuser"
    assert data["email"] == "new@example.com"


def test_register_duplicate_username(client, test_user):
    """测试用户名重复"""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "username": "testuser",
            "email": "another@example.com",
            "password": "password123",
        },
    )

    assert response.status_code == 400


def test_register_duplicate_email(client, test_user):
    """测试邮箱重复"""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "username": "anotheruser",
            "email": "test@example.com",
            "password": "password123",
        },
    )

    assert response.status_code == 400


def test_register_missing_fields(client):
    """测试注册缺少必填字段"""
    response = client.post(
        "/api/v1/auth/register",
        json={"username": "incomplete"},
    )

    assert response.status_code == 422


def test_register_short_password(client):
    """测试密码过短"""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "username": "newuser2",
            "email": "new2@example.com",
            "password": "123",
        },
    )

    assert response.status_code == 422
