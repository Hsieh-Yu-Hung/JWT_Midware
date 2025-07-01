"""
JWT Utilities

Provides JWT token creation, verification, and management functions.
"""

import jwt
import os
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

class JWTConfig:
    """JWT 配置類別"""
    
    def __init__(self, secret_key: Optional[str] = None, 
                 algorithm: str = "HS256",
                 access_token_expires: int = 30):
        """
        初始化 JWT 配置
        
        Args:
            secret_key: JWT 密鑰，如果未提供則從環境變數取得
            algorithm: JWT 演算法，預設為 HS256
            access_token_expires: Token 過期時間（分鐘），預設 30 分鐘
        """
        self.secret_key = secret_key or os.getenv('SECRET_KEY', 'your-secret-key-here')
        self.algorithm = algorithm
        self.access_token_expires = access_token_expires

# 全域配置實例
jwt_config = JWTConfig()

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    建立 JWT access token
    
    Args:
        data: 要編碼到 token 中的資料
        expires_delta: 自定義過期時間
        
    Returns:
        JWT token 字串
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=jwt_config.access_token_expires)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, jwt_config.secret_key, algorithm=jwt_config.algorithm)
    
    return encoded_jwt

def verify_token(token: str) -> Dict[str, Any]:
    """
    驗證 JWT token
    
    Args:
        token: JWT token 字串
        
    Returns:
        Token 中的資料
        
    Raises:
        jwt.ExpiredSignatureError: Token 已過期
        jwt.InvalidTokenError: Token 無效
    """
    try:
        payload = jwt.decode(token, jwt_config.secret_key, algorithms=[jwt_config.algorithm])
        return payload
    except jwt.ExpiredSignatureError:
        raise Exception("Token has expired")
    except jwt.InvalidTokenError:
        raise Exception("Invalid token")

def revoke_token(token: str) -> bool:
    """
    撤銷 JWT token（加入黑名單）
    
    Args:
        token: 要撤銷的 JWT token
        
    Returns:
        是否成功撤銷
    """
    try:
        # 這裡可以實作將 token 加入黑名單的邏輯
        # 例如存入 Redis 或資料庫
        # 目前只是簡單的驗證 token 格式
        verify_token(token)
        return True
    except Exception:
        return False

def get_token_expiration(token: str) -> Optional[datetime]:
    """
    取得 token 的過期時間
    
    Args:
        token: JWT token 字串
        
    Returns:
        過期時間，如果 token 無效則返回 None
    """
    try:
        payload = jwt.decode(token, jwt_config.secret_key, algorithms=[jwt_config.algorithm])
        exp_timestamp = payload.get("exp")
        if exp_timestamp:
            return datetime.fromtimestamp(exp_timestamp)
        return None
    except Exception:
        return None

def is_token_expired(token: str) -> bool:
    """
    檢查 token 是否已過期
    
    Args:
        token: JWT token 字串
        
    Returns:
        是否已過期
    """
    try:
        verify_token(token)
        return False
    except Exception as e:
        return "expired" in str(e).lower()

def refresh_token(token: str) -> Optional[str]:
    """
    重新整理 token（如果 token 即將過期）
    
    Args:
        token: 原始 JWT token
        
    Returns:
        新的 JWT token，如果無法重新整理則返回 None
    """
    try:
        payload = verify_token(token)
        
        # 移除過期時間
        payload.pop("exp", None)
        
        # 建立新的 token
        return create_access_token(payload)
    except Exception:
        return None 