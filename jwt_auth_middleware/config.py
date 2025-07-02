"""
JWT Configuration

Provides configuration management for JWT authentication.
"""

import os
from typing import Optional

class JWTConfig:
    """JWT 配置類別"""
    
    def __init__(self, 
                 secret_key: Optional[str] = None,
                 algorithm: str = "HS256",
                 access_token_expires: int = 30,
                 refresh_token_expires: int = 1440,  # 24 小時
                 mongodb_api_url: Optional[str] = None,
                 blacklist_collection: str = "jwt_blacklist",
                 enable_blacklist: bool = True):
        """
        初始化 JWT 配置
        
        Args:
            secret_key: JWT 密鑰
            algorithm: JWT 演算法
            access_token_expires: Access token 過期時間（分鐘）
            refresh_token_expires: Refresh token 過期時間（分鐘）
            mongodb_api_url: MongoDB API URL（用於黑名單功能）
            blacklist_collection: 黑名單集合名稱
            enable_blacklist: 是否啟用黑名單功能
        """
        self.secret_key = secret_key or os.getenv('SECRET_KEY', 'your-secret-key-here')
        self.algorithm = algorithm
        self.access_token_expires = access_token_expires
        self.refresh_token_expires = refresh_token_expires
        self.mongodb_api_url = mongodb_api_url or os.getenv('MONGODB_API_URL')
        self.blacklist_collection = blacklist_collection
        self.enable_blacklist = enable_blacklist
    
    def validate(self) -> bool:
        """
        驗證配置是否有效
        
        Returns:
            配置是否有效
        """
        if not self.secret_key or self.secret_key == 'your-secret-key-here':
            return False
        if self.access_token_expires <= 0:
            return False
        return True
    
    def to_dict(self) -> dict:
        """
        將配置轉換為字典
        
        Returns:
            配置字典
        """
        return {
            'algorithm': self.algorithm,
            'access_token_expires': self.access_token_expires,
            'refresh_token_expires': self.refresh_token_expires,
            'mongodb_api_url': self.mongodb_api_url,
            'blacklist_collection': self.blacklist_collection,
            'enable_blacklist': self.enable_blacklist
        }

# 預設配置
default_config = JWTConfig() 