"""
安全模块测试
"""
import pytest

from app.core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
    get_current_user,
)


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
    assert verify_password(password, hashed) == True

    # 错误的密码应该验证失败
    assert verify_password("wrongpassword", hashed) == False


def test_create_access_token():
    """测试创建访问令牌"""
    data = {"sub": "testuser"}
    token = create_access_token(data=data)

    assert token is not None
    assert isinstance(token, str)
    # JWT token 应该有三部分，用 . 分隔
    assert len(token.split(".")) == 3


def test_create_refresh_token():
    """测试创建刷新令牌"""
    data = {"sub": "testuser"}
    token = create_refresh_token(data=data)

    assert token is not None
    assert isinstance(token, str)
    assert len(token.split(".")) == 3


def test_decode_token():
    """测试解码令牌"""
    data = {"sub": "testuser", "user_id": 1}
    token = create_access_token(data=data)

    decoded = decode_token(token)

    assert decoded is not None
    assert decoded.get("sub") == "testuser"
    assert decoded.get("user_id") == 1


def test_decode_invalid_token():
    """测试解码无效令牌"""
    invalid_token = "invalid.token.here"

    decoded = decode_token(invalid_token)

    assert decoded is None


def test_decode_expired_token():
    """测试解码过期令牌"""
    # 创建一个立即过期的令牌
    data = {"sub": "testuser"}
    token = create_access_token(data=data, expires_delta=-1)

    decoded = decode_token(token)

    assert decoded is None
