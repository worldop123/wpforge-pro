"""
安全模块测试
覆盖密码哈希、密码策略、JWT令牌、CSRF防护、安全头、XSS防护等
"""
import pytest
from datetime import timedelta

from app.core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    decode_access_token,
    get_current_user,
    get_current_active_user,
    get_current_admin_user,
    validate_password_strength,
    PASSWORD_MIN_LENGTH,
    PASSWORD_MAX_LENGTH,
    BCRYPT_MAX_PASSWORD_BYTES,
)
from app.middleware.security_headers import SecurityHeadersMiddleware, DEFAULT_SECURITY_HEADERS
from app.middleware.csrf import CSRFMiddleware, generate_csrf_token, CSRF_HEADER_NAME, CSRF_COOKIE_NAME
from app.utils.validators import sanitize_html


# ==================== 密码哈希测试 ====================

def test_password_hash():
    """测试密码哈希"""
    password = "testpassword123"
    hashed = get_password_hash(password)

    # 哈希值不应等于原密码
    assert hashed != password
    # 哈希值应该是字符串
    assert isinstance(hashed, str)
    # 哈希值应该以 bcrypt 格式开头
    assert hashed.startswith("$2b$") or hashed.startswith("$2a$")


def test_password_verify():
    """测试密码验证"""
    password = "testpassword123"
    hashed = get_password_hash(password)

    # 正确的密码应该验证通过
    assert verify_password(password, hashed) is True

    # 错误的密码应该验证失败
    assert verify_password("wrongpassword", hashed) is False


def test_password_hash_uniqueness():
    """测试相同密码生成不同的哈希（盐值不同）"""
    password = "testpassword123"
    hash1 = get_password_hash(password)
    hash2 = get_password_hash(password)
    assert hash1 != hash2


def test_password_hash_long_password():
    """测试超长密码哈希（超过72字节应自动截断）"""
    long_password = "a" * 200
    hashed = get_password_hash(long_password)
    # 截断后的密码仍应验证通过
    assert verify_password(long_password, hashed) is True
    # 前72字节相同的密码也应验证通过
    assert verify_password("a" * 72, hashed) is True


def test_password_verify_invalid_hash():
    """测试对无效哈希的验证返回False"""
    assert verify_password("password", "invalid_hash") is False
    assert verify_password("password", "") is False
    assert verify_password("password", None) is False


# ==================== 密码策略测试 ====================

def test_password_strength_valid():
    """测试有效密码通过强度校验"""
    valid, msg = validate_password_strength("abc123")
    assert valid is True
    assert msg == ""


def test_password_strength_empty():
    """测试空密码不通过强度校验"""
    valid, msg = validate_password_strength("")
    assert valid is False
    assert "空" in msg


def test_password_strength_too_short():
    """测试过短密码不通过强度校验"""
    valid, msg = validate_password_strength("ab1")
    assert valid is False
    assert "少" in msg


def test_password_strength_pure_digits():
    """测试纯数字密码不通过强度校验"""
    valid, msg = validate_password_strength("12345678")
    assert valid is False
    assert "数字" in msg


def test_password_strength_pure_alpha():
    """测试纯字母密码不通过强度校验"""
    valid, msg = validate_password_strength("abcdefgh")
    assert valid is False
    assert "字母" in msg


def test_password_strength_too_long():
    """测试超长密码不通过强度校验"""
    valid, msg = validate_password_strength("a1" * 100)
    assert valid is False
    assert "超过" in msg


# ==================== JWT令牌测试 ====================

def test_create_access_token():
    """测试创建访问令牌"""
    data = {"sub": "testuser"}
    token = create_access_token(data=data)

    assert token is not None
    assert isinstance(token, str)
    # JWT token 应该有三部分，用 . 分隔
    assert len(token.split(".")) == 3


def test_create_access_token_with_expiry():
    """测试带过期时间的访问令牌"""
    data = {"sub": "testuser"}
    token = create_access_token(data=data, expires_delta=timedelta(minutes=30))

    assert token is not None
    assert isinstance(token, str)
    assert len(token.split(".")) == 3


def test_decode_access_token():
    """测试解码访问令牌"""
    data = {"sub": "testuser", "user_id": 1}
    token = create_access_token(data=data)

    decoded = decode_access_token(token)

    assert decoded is not None
    assert decoded.get("sub") == "testuser"
    assert decoded.get("user_id") == 1


def test_decode_invalid_token():
    """测试解码无效令牌"""
    invalid_token = "invalid.token.here"

    decoded = decode_access_token(invalid_token)

    assert decoded is None


def test_decode_expired_token():
    """测试解码过期令牌"""
    # 创建一个立即过期的令牌
    data = {"sub": "testuser"}
    token = create_access_token(data=data, expires_delta=timedelta(seconds=-1))

    decoded = decode_access_token(token)

    assert decoded is None


def test_get_current_user(client, test_user):
    """测试获取当前用户（通过API）"""
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "testuser", "password": "testpassword123"},
    )
    assert response.status_code == 200
    token = response.json()["access_token"]

    # 令牌应该能解码出用户信息
    decoded = decode_access_token(token)
    assert decoded is not None
    assert "sub" in decoded


# ==================== CSRF防护测试 ====================

class TestCSRFProtection:
    """CSRF防护测试"""

    def test_generate_csrf_token_returns_string(self):
        """测试CSRF Token生成返回字符串"""
        token = generate_csrf_token()
        assert isinstance(token, str)
        assert len(token) > 10

    def test_generate_csrf_token_uniqueness(self):
        """测试每次生成的CSRF Token不同"""
        token1 = generate_csrf_token()
        token2 = generate_csrf_token()
        assert token1 != token2

    def test_csrf_get_request_not_blocked(self, client):
        """测试GET请求不受CSRF限制"""
        response = client.get("/api/v1/sites")
        # 401表示认证失败，但不是403 CSRF错误
        assert response.status_code == 401

    def test_csrf_bearer_token_exempt(self, client, auth_headers):
        """测试Bearer Token认证的请求豁免CSRF"""
        # 带Bearer Token的POST请求不应被CSRF拦截
        response = client.post(
            "/api/v1/sites",
            headers=auth_headers,
            json={
                "name": "Test Site",
                "url": "https://test.example.com",
                "wp_url": "https://test.example.com",
                "wp_username": "admin",
                "wp_password": "password",
            },
        )
        # 不应返回403 CSRF错误
        assert response.status_code != 403

    def test_csrf_login_exempt(self, client):
        """测试登录端点豁免CSRF"""
        response = client.post(
            "/api/v1/auth/login",
            data={"username": "nonexistent", "password": "wrongpassword"},
        )
        # 应返回401认证失败，而非403 CSRF错误
        assert response.status_code == 401

    def test_csrf_header_name(self):
        """测试CSRF请求头名称"""
        assert CSRF_HEADER_NAME == "X-CSRF-Token"

    def test_csrf_cookie_name(self):
        """测试CSRF Cookie名称"""
        assert CSRF_COOKIE_NAME == "csrf_token"


# ==================== 安全头测试 ====================

class TestSecurityHeaders:
    """安全响应头测试"""

    def test_security_headers_present(self, client):
        """测试响应包含安全头"""
        response = client.get("/api/health")
        assert response.headers.get("X-Content-Type-Options") == "nosniff"
        assert response.headers.get("X-Frame-Options") == "SAMEORIGIN"
        assert response.headers.get("X-XSS-Protection") == "1; mode=block"

    def test_security_headers_referrer_policy(self, client):
        """测试Referrer-Policy头"""
        response = client.get("/api/health")
        assert response.headers.get("Referrer-Policy") == "strict-origin-when-cross-origin"

    def test_default_security_headers_config(self):
        """测试默认安全头配置"""
        assert "X-Content-Type-Options" in DEFAULT_SECURITY_HEADERS
        assert "X-Frame-Options" in DEFAULT_SECURITY_HEADERS
        assert "X-XSS-Protection" in DEFAULT_SECURITY_HEADERS
        assert DEFAULT_SECURITY_HEADERS["X-Content-Type-Options"] == "nosniff"


# ==================== XSS防护测试 ====================

class TestXSSProtection:
    """XSS防护测试"""

    def test_sanitize_html_removes_script_tag(self):
        """测试HTML净化移除script标签"""
        html = '<script>alert("xss")</script><p>safe</p>'
        result = sanitize_html(html)
        assert "<script" not in result.lower()
        assert "alert" not in result
        assert "safe" in result

    def test_sanitize_html_removes_on_events(self):
        """测试HTML净化移除on事件属性"""
        html = '<img src="x" onerror="alert(1)">'
        result = sanitize_html(html)
        assert "onerror" not in result.lower()

    def test_sanitize_html_removes_javascript_protocol(self):
        """测试HTML净化移除javascript:协议"""
        html = '<a href="javascript:alert(1)">click</a>'
        result = sanitize_html(html)
        assert "javascript:" not in result.lower()

    def test_sanitize_html_removes_iframe(self):
        """测试HTML净化移除iframe标签"""
        html = '<iframe src="evil.com"></iframe><p>ok</p>'
        result = sanitize_html(html)
        assert "<iframe" not in result.lower()
        assert "ok" in result

    def test_sanitize_html_empty_input(self):
        """测试空输入返回空字符串"""
        assert sanitize_html("") == ""
        assert sanitize_html(None) == ""


# ==================== 限流测试 ====================

class TestRateLimiting:
    """API限流测试"""

    def test_rate_limit_allows_normal_requests(self, client):
        """测试正常请求不被限流"""
        for _ in range(5):
            response = client.get("/api/health")
            assert response.status_code == 200

    def test_rate_limit_blocks_excessive_requests(self, client):
        """测试超过限流阈值返回429"""
        # 发送大量请求触发限流
        blocked = False
        for _ in range(100):
            response = client.get("/api/v1/sites")
            if response.status_code == 429:
                blocked = True
                break
        assert blocked is True
