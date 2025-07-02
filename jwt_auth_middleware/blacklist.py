"""
JWT Blacklist Management

使用 MongoDB API 管理被撤銷的 JWT tokens
"""

import requests
import hashlib
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from .config import JWTConfig

class BlacklistManager:
    """JWT 黑名單管理器"""
    
    def __init__(self, 
                 mongodb_api_url: str,
                 collection_name: str = "jwt_blacklist",
                 jwt_config: Optional[JWTConfig] = None):
        """
        初始化黑名單管理器
        
        Args:
            mongodb_api_url: MongoDB API 的基礎 URL
            collection_name: 黑名單集合名稱
            jwt_config: JWT 配置實例
        """
        self.mongodb_api_url = mongodb_api_url.rstrip('/')
        self.collection_name = collection_name
        self.jwt_config = jwt_config or JWTConfig()
    
    def _hash_token(self, token: str) -> str:
        """
        對 token 進行雜湊處理以保護隱私
        
        Args:
            token: JWT token
            
        Returns:
            雜湊後的 token
        """
        return hashlib.sha256(token.encode()).hexdigest()
    
    def _get_token_expiration(self, token: str) -> Optional[datetime]:
        """
        取得 token 的過期時間
        
        Args:
            token: JWT token
            
        Returns:
            過期時間
        """
        try:
            import jwt
            payload = jwt.decode(token, self.jwt_config.secret_key, 
                               algorithms=[self.jwt_config.algorithm])
            exp_timestamp = payload.get("exp")
            if exp_timestamp:
                return datetime.fromtimestamp(exp_timestamp)
        except Exception:
            pass
        return None
    
    def add_to_blacklist(self, token: str, reason: str = "revoked") -> bool:
        """
        將 token 加入黑名單
        
        Args:
            token: 要加入黑名單的 JWT token
            reason: 撤銷原因
            
        Returns:
            是否成功加入黑名單
        """
        try:
            # 雜湊 token
            token_hash = self._hash_token(token)
            
            # 取得過期時間
            expiration = self._get_token_expiration(token)
            
            # 準備文件資料
            document = {
                "token_hash": token_hash,
                "reason": reason,
                "revoked_at": datetime.now(timezone.utc).isoformat(),
                "expires_at": expiration.isoformat() if expiration else None
            }
            
            # 呼叫 MongoDB API 插入文件
            response = requests.post(
                f"{self.mongodb_api_url}/insert",
                json={
                    "collection": self.collection_name,
                    "document": document
                },
                timeout=10
            )
            
            if response.status_code == 200:
                return True
            else:
                print(f"加入黑名單失敗: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"加入黑名單時發生錯誤: {str(e)}")
            return False
    
    def is_blacklisted(self, token: str) -> bool:
        """
        檢查 token 是否在黑名單中
        
        Args:
            token: 要檢查的 JWT token
            
        Returns:
            是否在黑名單中
        """
        try:
            # 雜湊 token
            token_hash = self._hash_token(token)
            
            # 呼叫 MongoDB API 查詢
            response = requests.post(
                f"{self.mongodb_api_url}/find",
                json={
                    "collection": self.collection_name,
                    "filter": {"token_hash": token_hash}
                },
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                return len(result.get("documents", [])) > 0
            else:
                print(f"查詢黑名單失敗: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"查詢黑名單時發生錯誤: {str(e)}")
            return False
    
    def remove_from_blacklist(self, token: str) -> bool:
        """
        從黑名單中移除 token
        
        Args:
            token: 要移除的 JWT token
            
        Returns:
            是否成功移除
        """
        try:
            # 雜湊 token
            token_hash = self._hash_token(token)
            
            # 呼叫 MongoDB API 刪除
            response = requests.post(
                f"{self.mongodb_api_url}/delete",
                json={
                    "collection": self.collection_name,
                    "filter": {"token_hash": token_hash}
                },
                timeout=10
            )
            
            if response.status_code == 200:
                return True
            else:
                print(f"從黑名單移除失敗: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"從黑名單移除時發生錯誤: {str(e)}")
            return False
    
    def cleanup_expired_tokens(self) -> int:
        """
        清理已過期的黑名單 tokens
        
        Returns:
            清理的 token 數量
        """
        try:
            # 取得當前時間
            now = datetime.now(timezone.utc)
            
            # 呼叫 MongoDB API 刪除過期文件
            response = requests.post(
                f"{self.mongodb_api_url}/delete",
                json={
                    "collection": self.collection_name,
                    "filter": {
                        "expires_at": {
                            "$lt": now.isoformat()
                        }
                    }
                },
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("deleted_count", 0)
            else:
                print(f"清理過期 tokens 失敗: {response.status_code} - {response.text}")
                return 0
                
        except Exception as e:
            print(f"清理過期 tokens 時發生錯誤: {str(e)}")
            return 0
    
    def get_blacklist_stats(self) -> Dict[str, Any]:
        """
        取得黑名單統計資訊
        
        Returns:
            統計資訊字典
        """
        try:
            # 呼叫 MongoDB API 取得集合統計
            response = requests.post(
                f"{self.mongodb_api_url}/count",
                json={
                    "collection": self.collection_name
                },
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                total_count = result.get("count", 0)
                
                # 取得過期 tokens 數量
                now = datetime.now(timezone.utc)
                expired_response = requests.post(
                    f"{self.mongodb_api_url}/count",
                    json={
                        "collection": self.collection_name,
                        "filter": {
                            "expires_at": {
                                "$lt": now.isoformat()
                            }
                        }
                    },
                    timeout=10
                )
                
                expired_count = 0
                if expired_response.status_code == 200:
                    expired_result = expired_response.json()
                    expired_count = expired_result.get("count", 0)
                
                return {
                    "total_tokens": total_count,
                    "expired_tokens": expired_count,
                    "active_tokens": total_count - expired_count
                }
            else:
                print(f"取得統計資訊失敗: {response.status_code} - {response.text}")
                return {"total_tokens": 0, "expired_tokens": 0, "active_tokens": 0}
                
        except Exception as e:
            print(f"取得統計資訊時發生錯誤: {str(e)}")
            return {"total_tokens": 0, "expired_tokens": 0, "active_tokens": 0}

# 全域黑名單管理器實例
blacklist_manager = None

def init_blacklist_manager(mongodb_api_url: str, 
                          collection_name: str = "jwt_blacklist",
                          jwt_config: Optional[JWTConfig] = None) -> BlacklistManager:
    """
    初始化全域黑名單管理器
    
    Args:
        mongodb_api_url: MongoDB API 的基礎 URL
        collection_name: 黑名單集合名稱
        jwt_config: JWT 配置實例
        
    Returns:
        黑名單管理器實例
    """
    global blacklist_manager
    blacklist_manager = BlacklistManager(mongodb_api_url, collection_name, jwt_config)
    return blacklist_manager

def get_blacklist_manager() -> Optional[BlacklistManager]:
    """
    取得全域黑名單管理器
    
    Returns:
        黑名單管理器實例，如果未初始化則返回 None
    """
    return blacklist_manager 