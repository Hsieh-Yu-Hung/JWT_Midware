"""
JWT Configuration

Provides configuration management for JWT authentication.
"""

import os
from typing import Optional
from dotenv import load_dotenv

# 載入 .env 檔案
load_dotenv()

class JWTConfig:
    """JWT 配置類別"""
    
    def __init__(self, 
                 secret_key: Optional[str] = None,
                 algorithm: Optional[str] = None,
                 access_token_expires: Optional[int] = None,
                 refresh_token_expires: Optional[int] = None,
                 mongodb_api_url: Optional[str] = None,
                 blacklist_collection: Optional[str] = None,
                 enable_blacklist: Optional[bool] = None):
        """
        初始化 JWT 配置
        
        如果參數為 None，將從環境變數讀取配置：
        - JWT_SECRET_KEY: JWT 密鑰
        - JWT_ALGORITHM: JWT 演算法
        - JWT_ACCESS_TOKEN_EXPIRES: Access token 過期時間（分鐘）
        - JWT_REFRESH_TOKEN_EXPIRES: Refresh token 過期時間（分鐘）
        - MONGODB_API_URL: MongoDB API URL（用於黑名單功能）
        - JWT_BLACKLIST_COLLECTION: 黑名單集合名稱
        - JWT_ENABLE_BLACKLIST: 是否啟用黑名單功能
        
        Args:
            secret_key: JWT 密鑰
            algorithm: JWT 演算法
            access_token_expires: Access token 過期時間（分鐘）
            refresh_token_expires: Refresh token 過期時間（分鐘）
            mongodb_api_url: MongoDB API URL（用於黑名單功能）
            blacklist_collection: 黑名單集合名稱
            enable_blacklist: 是否啟用黑名單功能
            
        Raises:
            ValueError: 當必要的環境變數未設定時拋出異常
        """
        # 從環境變數讀取配置，如果參數為 None
        self.secret_key = secret_key if secret_key is not None else self._get_env_var('JWT_SECRET_KEY')
        self.algorithm = algorithm or self._get_env_var('JWT_ALGORITHM')
        self.access_token_expires = access_token_expires if access_token_expires is not None else int(self._get_env_var('JWT_ACCESS_TOKEN_EXPIRES'))
        self.refresh_token_expires = refresh_token_expires if refresh_token_expires is not None else int(self._get_env_var('JWT_REFRESH_TOKEN_EXPIRES'))
        self.mongodb_api_url = mongodb_api_url if mongodb_api_url is not None else self._get_env_var('MONGODB_API_URL')
        self.blacklist_collection = blacklist_collection or self._get_env_var('JWT_BLACKLIST_COLLECTION')
        self.enable_blacklist = enable_blacklist if enable_blacklist is not None else (self._get_env_var('JWT_ENABLE_BLACKLIST').lower() == 'true')
    
    def _get_env_var(self, var_name: str) -> str:
        """
        從環境變數獲取值，如果不存在則拋出異常
        
        Args:
            var_name: 環境變數名稱
            
        Returns:
            環境變數的值
            
        Raises:
            ValueError: 當環境變數未設定時拋出異常
        """
        value = os.getenv(var_name)
        if value is None:
            raise ValueError(f"環境變數 '{var_name}' 未設定。請檢查 .env 檔案是否正確配置。")
        return value
    
    def validate(self) -> bool:
        """
        驗證配置是否有效
        
        Returns:
            配置是否有效
        """
        if not self.secret_key or self.secret_key == '':
            return False
        if not self.mongodb_api_url or self.mongodb_api_url == '':
            return False
        if self.access_token_expires <= 0:
            return False
        if self.refresh_token_expires <= 0:
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