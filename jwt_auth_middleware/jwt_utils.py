"""
JWT Utilities

Provides JWT token creation, verification, and management functions.
"""

import jwt
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional
from .config import JWTConfig
from .blacklist import get_blacklist_manager, init_blacklist_manager

# 全域配置實例 - 使用預設配置
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
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=jwt_config.access_token_expires)
    
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
        
        # 檢查黑名單
        if jwt_config.enable_blacklist:
            blacklist_mgr = get_blacklist_manager()
            if blacklist_mgr and blacklist_mgr.is_blacklisted(token):
                raise Exception("Token has been revoked")
        
        return payload
    except jwt.ExpiredSignatureError:
        raise Exception("Token has expired")
    except jwt.InvalidTokenError:
        raise Exception("Invalid token")

def revoke_token(token: str, reason: str = "revoked") -> bool:
    """
    撤銷 JWT token（加入黑名單）
    
    Args:
        token: 要撤銷的 JWT token
        reason: 撤銷原因
        
    Returns:
        是否成功撤銷
    """
    try:
        # 驗證 token 格式
        verify_token(token)
        
        # 如果啟用黑名單功能，將 token 加入黑名單
        if jwt_config.enable_blacklist:
            blacklist_mgr = get_blacklist_manager()
            if blacklist_mgr:
                return blacklist_mgr.add_to_blacklist(token, reason)
            else:
                print("警告: 黑名單管理器未初始化")
                return False
        else:
            print("警告: 黑名單功能已停用")
            return False
            
    except Exception as e:
        print(f"撤銷 token 時發生錯誤: {str(e)}")
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

def is_token_blacklisted(token: str) -> bool:
    """
    檢查 token 是否在黑名單中
    
    Args:
        token: JWT token 字串
        
    Returns:
        是否在黑名單中
    """
    if not jwt_config.enable_blacklist:
        return False
    
    blacklist_mgr = get_blacklist_manager()
    if blacklist_mgr:
        return blacklist_mgr.is_blacklisted(token)
    return False

def remove_from_blacklist(token: str) -> bool:
    """
    從黑名單中移除 token
    
    Args:
        token: JWT token 字串
        
    Returns:
        是否成功移除
    """
    if not jwt_config.enable_blacklist:
        return False
    
    blacklist_mgr = get_blacklist_manager()
    if blacklist_mgr:
        return blacklist_mgr.remove_from_blacklist(token)
    return False

def cleanup_expired_blacklist_tokens() -> int:
    """
    清理已過期的黑名單 tokens
    
    Returns:
        清理的 token 數量
    """
    if not jwt_config.enable_blacklist:
        return 0
    
    blacklist_mgr = get_blacklist_manager()
    if blacklist_mgr:
        return blacklist_mgr.cleanup_expired_tokens()
    return 0

def get_blacklist_statistics() -> Dict[str, Any]:
    """
    取得黑名單統計資訊
    
    Returns:
        統計資訊字典
    """
    if not jwt_config.enable_blacklist:
        return {"total_tokens": 0, "expired_tokens": 0, "active_tokens": 0}
    
    blacklist_mgr = get_blacklist_manager()
    if blacklist_mgr:
        return blacklist_mgr.get_blacklist_stats()
    return {"total_tokens": 0, "expired_tokens": 0, "active_tokens": 0}

def initialize_blacklist_system(mongodb_api_url: str = None, 
                               collection_name: str = None) -> bool:
    """
    初始化黑名單系統
    
    Args:
        mongodb_api_url: MongoDB API URL（如果為 None 則使用配置中的值）
        collection_name: 集合名稱（如果為 None 則使用配置中的值）
        
    Returns:
        是否成功初始化
    """
    try:
        api_url = mongodb_api_url or jwt_config.mongodb_api_url
        collection = collection_name or jwt_config.blacklist_collection
        
        if not api_url:
            print("錯誤: 未提供 MongoDB API URL")
            return False
        
        init_blacklist_manager(api_url, collection, jwt_config)
        return True
    except Exception as e:
        print(f"初始化黑名單系統時發生錯誤: {str(e)}")
        return False 