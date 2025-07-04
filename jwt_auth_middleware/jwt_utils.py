"""
JWT Utilities

Provides JWT token creation, verification, and management functions.
"""

import jwt
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional
from .config import JWTConfig
from .blacklist import BlacklistManager

# 全域配置實例 - 自動從環境變數讀取配置
jwt_config = JWTConfig()

# 全域黑名單管理器實例
blacklist_manager = BlacklistManager(
    mongodb_api_url=jwt_config.mongodb_api_url,
    collection_name=jwt_config.blacklist_collection,
    jwt_config=jwt_config
) if jwt_config.enable_blacklist and jwt_config.mongodb_api_url else None

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
    
    to_encode.update({
        "exp": expire,
        "type": "access",  # 標記為 Access Token
        "iat": datetime.now(timezone.utc)  # 發行時間
    })
    encoded_jwt = jwt.encode(to_encode, jwt_config.secret_key, algorithm=jwt_config.algorithm)
    
    return encoded_jwt

def create_refresh_token(data: Dict[str, Any]) -> str:
    """
    建立 JWT refresh token
    
    Args:
        data: 要編碼到 token 中的資料
        
    Returns:
        JWT refresh token 字串
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=jwt_config.refresh_token_expires)
    
    to_encode.update({
        "exp": expire,
        "type": "refresh",  # 標記為 Refresh Token
        "iat": datetime.now(timezone.utc)  # 發行時間
    })
    encoded_jwt = jwt.encode(to_encode, jwt_config.secret_key, algorithm=jwt_config.algorithm)
    
    return encoded_jwt

def create_token_pair(data: Dict[str, Any]) -> Dict[str, str]:
    """
    建立 Access Token 和 Refresh Token 對
    
    Args:
        data: 要編碼到 token 中的資料
        
    Returns:
        包含 access_token 和 refresh_token 的字典
    """
    access_token = create_access_token(data)
    refresh_token = create_refresh_token(data)
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token
    }

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
        if jwt_config.enable_blacklist and blacklist_manager:
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

def refresh_access_token(refresh_token: str) -> Optional[str]:
    """
    使用 Refresh Token 取得新的 Access Token
    
    Args:
        refresh_token: JWT refresh token 字串
        
    Returns:
        新的 JWT access token，如果無法重新整理則返回 None
    """
    try:
        # 驗證 Refresh Token
        payload = verify_refresh_token(refresh_token)
        
        # 移除過期時間、類型標記和發行時間
        payload.pop("exp", None)
        payload.pop("type", None)
        payload.pop("iat", None)
        
        # 建立新的 Access Token
        return create_access_token(payload)
    except Exception as e:
        print(f"Refresh token 失敗: {str(e)}")
        return None

def revoke_token(token: str, reason: str = "revoked") -> bool:
    """
    撤銷 JWT token（加入黑名單）
    
    Args:
        token: 要撤銷的 JWT token
        reason: 撤銷原因
        
    Returns:
        是否成功撤銷
    """
    print(f"嘗試 revoke_token: {token}")
    try:
        # 驗證 token 格式
        verify_token(token)
        
        # 如果啟用黑名單功能，將 token 加入黑名單
        if jwt_config.enable_blacklist and blacklist_manager:
            print(f"jwt_config.enable_blacklist: {jwt_config.enable_blacklist}")
            print(f"blacklist_mgr: {blacklist_manager}")
            return blacklist_manager.add_to_blacklist(token, reason)
        else:
            print("警告: 黑名單功能已停用或未初始化")
            return False
            
    except Exception as e:
        print(f"撤銷 token 時發生錯誤: {str(e)}")
        return False

def revoke_token_pair(access_token: str, refresh_token: str, reason: str = "user_logout") -> bool:
    """
    撤銷 Access Token 和 Refresh Token 對
    
    Args:
        access_token: 要撤銷的 Access Token
        refresh_token: 要撤銷的 Refresh Token
        reason: 撤銷原因
        
    Returns:
        是否成功撤銷兩個 token
    """
    try:
        success = True
        
        # 撤銷 Access Token
        if not revoke_token(access_token, f"{reason}_access"):
            success = False
        
        # 撤銷 Refresh Token
        if not revoke_token(refresh_token, f"{reason}_refresh"):
            success = False
        
        return success
    except Exception as e:
        print(f"撤銷 token 對時發生錯誤: {str(e)}")
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

def is_token_blacklisted(token: str) -> bool:
    """
    檢查 token 是否在黑名單中
    
    Args:
        token: JWT token 字串
        
    Returns:
        是否在黑名單中
    """
    if not jwt_config.enable_blacklist or not blacklist_manager:
        return False
    
    return blacklist_manager.is_blacklisted(token)

def remove_from_blacklist(token: str) -> bool:
    """
    從黑名單中移除 token
    
    Args:
        token: JWT token 字串
        
    Returns:
        是否成功移除
    """
    if not jwt_config.enable_blacklist or not blacklist_manager:
        return False
    
    return blacklist_manager.remove_from_blacklist(token)

def cleanup_expired_blacklist_tokens() -> int:
    """
    清理已過期的黑名單 tokens
    
    Returns:
        清理的 token 數量
    """
    if not jwt_config.enable_blacklist or not blacklist_manager:
        return 0
    
    return blacklist_manager.cleanup_expired_tokens()

def get_blacklist_statistics() -> Dict[str, Any]:
    """
    取得黑名單統計資訊
    
    Returns:
        統計資訊字典
    """
    if not jwt_config.enable_blacklist or not blacklist_manager:
        return {"total_tokens": 0, "expired_tokens": 0, "active_tokens": 0}
    
    return blacklist_manager.get_blacklist_stats()

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
    global blacklist_manager
    
    try:
        api_url = mongodb_api_url or jwt_config.mongodb_api_url
        collection = collection_name or jwt_config.blacklist_collection
        
        if not api_url:
            print("錯誤: 未提供 MongoDB API URL")
            return False
        
        # 重新建立黑名單管理器
        blacklist_manager = BlacklistManager(api_url, collection, jwt_config)
        return True
    except Exception as e:
        print(f"初始化黑名單系統時發生錯誤: {str(e)}")
        return False 