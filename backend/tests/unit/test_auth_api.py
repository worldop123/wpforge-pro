"""
认证 API 测试
"""
import pytest


def test_login_success(client, test_user):
    """测试登录成功"""
    response = client.post(
        "/api/v1/auth/login",
        json={"username": "testuser", "password": "testpassword123"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] == True
    assert "access_token" in data["data"]
    assert "refresh_token" in data["data"]
    assert data["data"]["token_type"] == "bearer"
    assert data["data"]["user"]["username"] == "testuser"


def test_login_wrong_password(client, test_user):
    """测试密码错误"""
    response = client.post(
        "/api/v1/auth/login",
        json={"username": "testuser", "password": "wrongpassword"},
    )

    assert response.status_code == 401
    data = response.json()
    assert data["success"] == False


def test_login_wrong_username(client):
    """测试用户名不存在"""
    response = client.post(
        "/api/v1/auth/login",
        json={"username": "nonexistent", "password": "testpassword123"},
    )

    assert response.status_code == 401
    data = response.json()
    assert data["success"] == False


def test_login_missing_fields(client):
    """测试缺少必填字段"""
    response = client.post(
        "/api/v1/auth/login",
        json={"username": "testuser"},
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
    assert data["success"] == True
    assert data["data"]["username"] == "testuser"


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
    assert data["success"] == True


def test_refresh_token(client, test_user):
    """测试刷新令牌"""
    # 先登录获取 refresh token
    login_response = client.post(
        "/api/v1/auth/login",
        json={"username": "testuser", "password": "testpassword123"},
    )
    refresh_token = login_response.json()["data"]["refresh_token"]

    # 使用 refresh token 刷新
    response = client.post(
        "/api/v1/auth/refresh",
        headers={"Authorization": f"Bearer {refresh_token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] == True
    assert "access_token" in data["data"]


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
    assert data["success"] == True
    assert data["data"]["username"] == "newuser"


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
    data = response.json()
    assert data["success"] == False


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
    data = response.json()
    assert data["success"] == False


def test_change_password(client, auth_headers):
    """测试修改密码"""
    response = client.post(
        "/api/v1/auth/change-password",
        headers=auth_headers,
        json={
            "old_password": "testpassword123",
            "new_password": "newpassword123",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] == True

    # 使用新密码登录
    login_response = client.post(
        "/api/v1/auth/login",
        json={"username": "testuser", "password": "newpassword123"},
    )
    assert login_response.status_code == 200


def test_change_password_wrong_old(client, auth_headers):
    """测试旧密码错误"""
    response = client.post(
        "/api/v1/auth/change-password",
        headers=auth_headers,
        json={
            "old_password": "wrongpassword",
            "new_password": "newpassword123",
        },
    )

    assert response.status_code == 400
    data = response.json()
    assert data["success"] == False
