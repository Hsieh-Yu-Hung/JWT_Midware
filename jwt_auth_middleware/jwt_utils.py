"""
JWT Utilities for Middleware Package

Provides JWT token verification functions only.
Business logic functions have been moved to main project.
"""

import jwt
from typing import Dict, Any, Optional
from .config import JWTConfig

# 全域配置實例 - 延遲初始化
_jwt_config = None

def _get_jwt_config() -> JWTConfig:
    """獲取 JWT 配置實例"""
    global _jwt_config
    if _jwt_config is None:
        raise RuntimeError(
            "JWT 配置未初始化。請先使用 set_jwt_config() 設定配置，"
            "或使用 create_jwt_config() 創建配置實例。"
            "範例：\n"
            "from jwt_auth_middleware import create_jwt_config, set_jwt_config\n"
            "config = create_jwt_config(secret_key='your_secret_key', config_file='config.yaml')\n"
            "set_jwt_config(config)"
        )
    return _jwt_config

def set_jwt_config(config: JWTConfig):
    """設置 JWT 配置（主要用於測試）"""
    global _jwt_config
    _jwt_config = config

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
        jwt_config = _get_jwt_config()
        payload = jwt.decode(token, jwt_config.secret_key, algorithms=[jwt_config.algorithm])
        
        # 檢查黑名單（如果啟用）
        if jwt_config.enable_blacklist and jwt_config.mongodb_api_url:
            from .blacklist import BlacklistManager
            blacklist_manager = BlacklistManager(jwt_config)
            if blacklist_manager.is_blacklisted(token):
                raise Exception("Token has been revoked")
        
        return payload
    except jwt.ExpiredSignatureError:
        raise Exception("Token has expired")
    except jwt.InvalidTokenError:
        raise Exception("Invalid token")

def verify_access_token(token: str) -> Dict[str, Any]:
    """
    驗證 Access Token
    
    Args:
        token: JWT access token 字串
        
    Returns:
        Token 中的資料
        
    Raises:
        Exception: Token 類型錯誤或驗證失敗
    """
    payload = verify_token(token)
    
    # 檢查是否為 Access Token
    if payload.get("type") != "access":
        raise Exception("Invalid token type: expected access token")
    
    return payload

def verify_refresh_token(token: str) -> Dict[str, Any]:
    """
    驗證 Refresh Token
    
    Args:
        token: JWT refresh token 字串
        
    Returns:
        Token 中的資料
        
    Raises:
        Exception: Token 類型錯誤或驗證失敗
    """
    payload = verify_token(token)
    
    # 檢查是否為 Refresh Token
    if payload.get("type") != "refresh":
        raise Exception("Invalid token type: expected refresh token")
    
    return payload 