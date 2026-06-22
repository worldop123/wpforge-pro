"""
安全相关工具：密码哈希、JWT令牌、密码策略等

密码哈希使用 bcrypt 直接调用，避免 passlib 与新版 bcrypt 的兼容性问题。
密码在哈希前会被截断到 72 字节（bcrypt 限制），并增加密码强度校验。
"""

import re
from datetime import datetime, timedelta
from typing import Optional, Union, Tuple

import bcrypt
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.models.user import User

# bcrypt 密码最大长度（字节）
BCRYPT_MAX_PASSWORD_BYTES = 72

# 密码策略配置
PASSWORD_MIN_LENGTH = 6
PASSWORD_MAX_LENGTH = 128

# OAuth2方案
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def _truncate_password(password: str) -> bytes:
    """将密码编码为字节并截断到 bcrypt 支持的最大长度（72字节）"""
    password_bytes = password.encode("utf-8")
    if len(password_bytes) > BCRYPT_MAX_PASSWORD_BYTES:
        password_bytes = password_bytes[:BCRYPT_MAX_PASSWORD_BYTES]
    return password_bytes


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码

    使用 bcrypt 直接验证，兼容新旧哈希格式。
    """
    try:
        if not plain_password or not hashed_password:
            return False
        password_bytes = _truncate_password(plain_password)
        hash_bytes = hashed_password.encode("utf-8")
        return bcrypt.checkpw(password_bytes, hash_bytes)
    except (ValueError, TypeError, AttributeError):
        return False


def get_password_hash(password: str) -> str:
    """获取密码哈希

    使用 bcrypt 直接哈希，自动处理 72 字节限制。
    返回的哈希字符串以 $2b$ 开头。
    """
    password_bytes = _truncate_password(password)
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode("utf-8")


def validate_password_strength(password: str) -> Tuple[bool, str]:
    """校验密码强度

    密码策略：
    - 长度 6-128 字符
    - 不能为纯数字或纯字母

    返回 (是否通过, 错误信息)
    """
    if not password:
        return False, "密码不能为空"

    if len(password) < PASSWORD_MIN_LENGTH:
        return False, f"密码长度不能少于 {PASSWORD_MIN_LENGTH} 位"

    if len(password) > PASSWORD_MAX_LENGTH:
        return False, f"密码长度不能超过 {PASSWORD_MAX_LENGTH} 位"

    if password.isdigit():
        return False, "密码不能为纯数字"

    if password.isalpha():
        return False, "密码不能为纯字母"

    return True, ""


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """创建访问令牌"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """解码访问令牌"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """获取当前用户"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无法验证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception

    user_id: Optional[str] = payload.get("sub")
    if user_id is None:
        raise credentials_exception

    user = db.query(User).filter(User.id == int(user_id)).first()
    if user is None:
        raise credentials_exception

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户已被禁用"
        )

    return user


def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """获取当前活跃用户"""
    return current_user


def get_current_admin_user(current_user: User = Depends(get_current_user)) -> User:
    """获取当前管理员用户"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要管理员权限"
        )
    return current_user
