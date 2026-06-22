"""
站点管理 API 测试
"""
import pytest


def test_get_sites_empty(client, auth_headers):
    """测试获取空站点列表"""
    response = client.get(
        "/api/v1/sites",
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] == True
    assert data["data"]["total"] == 0
    assert len(data["data"]["items"]) == 0


def test_get_sites_with_data(client, auth_headers, test_site):
    """测试获取站点列表"""
    response = client.get(
        "/api/v1/sites",
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] == True
    assert data["data"]["total"] == 1
    assert len(data["data"]["items"]) == 1
    assert data["data"]["items"][0]["name"] == "Test Site"


def test_get_sites_no_auth(client):
    """测试未认证时获取站点列表"""
    response = client.get("/api/v1/sites")

    assert response.status_code == 401


def test_create_site(client, auth_headers):
    """测试创建站点"""
    response = client.post(
        "/api/v1/sites",
        headers=auth_headers,
        json={
            "name": "New Site",
            "url": "https://new.example.com",
            "wp_username": "admin",
            "wp_password": "password",
            "wp_api_key": "api_key",
            "language": "en-US",
            "currency": "USD",
            "page_builder": "elementor",
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["success"] == True
    assert data["data"]["name"] == "New Site"
    assert data["data"]["url"] == "https://new.example.com"


def test_create_site_missing_fields(client, auth_headers):
    """测试创建站点缺少必填字段"""
    response = client.post(
        "/api/v1/sites",
        headers=auth_headers,
        json={
            "name": "New Site",
        },
    )

    assert response.status_code == 422


def test_get_site_detail(client, auth_headers, test_site):
    """测试获取站点详情"""
    response = client.get(
        f"/api/v1/sites/{test_site.id}",
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] == True
    assert data["data"]["name"] == "Test Site"
    assert data["data"]["id"] == test_site.id


def test_get_site_not_found(client, auth_headers):
    """测试获取不存在的站点"""
    response = client.get(
        "/api/v1/sites/9999",
        headers=auth_headers,
    )

    assert response.status_code == 404


def test_update_site(client, auth_headers, test_site):
    """测试更新站点"""
    response = client.put(
        f"/api/v1/sites/{test_site.id}",
        headers=auth_headers,
        json={
            "name": "Updated Site",
            "url": "https://updated.example.com",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] == True
    assert data["data"]["name"] == "Updated Site"
    assert data["data"]["url"] == "https://updated.example.com"


def test_update_site_not_found(client, auth_headers):
    """测试更新不存在的站点"""
    response = client.put(
        "/api/v1/sites/9999",
        headers=auth_headers,
        json={
            "name": "Updated Site",
        },
    )

    assert response.status_code == 404


def test_delete_site(client, auth_headers, test_site):
    """测试删除站点"""
    response = client.delete(
        f"/api/v1/sites/{test_site.id}",
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] == True

    # 确认已删除
    get_response = client.get(
        f"/api/v1/sites/{test_site.id}",
        headers=auth_headers,
    )
    assert get_response.status_code == 404


def test_delete_site_not_found(client, auth_headers):
    """测试删除不存在的站点"""
    response = client.delete(
        "/api/v1/sites/9999",
        headers=auth_headers,
    )

    assert response.status_code == 404


def test_test_connection(client, auth_headers, test_site):
    """测试测试连接"""
    response = client.post(
        f"/api/v1/sites/{test_site.id}/test-connection",
        headers=auth_headers,
    )

    # 由于是测试环境，可能连接失败，但接口应该正常响应
    assert response.status_code in [200, 400]
    data = response.json()
    assert "success" in data


def test_get_site_stats(client, auth_headers, test_site):
    """测试获取站点统计"""
    response = client.get(
        f"/api/v1/sites/{test_site.id}/stats",
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] == True
    assert "data" in data


def test_site_pagination(client, auth_headers, db, test_user):
    """测试站点分页"""
    # 创建多个站点
    from app.models.site import Site

    for i in range(15):
        site = Site(
            name=f"Site {i}",
            url=f"https://site{i}.example.com",
            wp_username="admin",
            wp_password="password",
            user_id=test_user.id,
        )
        db.add(site)
    db.commit()

    # 测试第一页
    response = client.get(
        "/api/v1/sites?page=1&page_size=10",
        headers=auth_headers,
    )
    data = response.json()
    assert data["data"]["total"] == 15
    assert data["data"]["page"] == 1
    assert data["data"]["page_size"] == 10
    assert len(data["data"]["items"]) == 10

    # 测试第二页
    response = client.get(
        "/api/v1/sites?page=2&page_size=10",
        headers=auth_headers,
    )
    data = response.json()
    assert data["data"]["page"] == 2
    assert len(data["data"]["items"]) == 5
