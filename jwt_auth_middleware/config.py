"""
JWT Configuration

Provides configuration management for JWT authentication.
"""

import yaml
from typing import Optional, Dict, Any
from pathlib import Path

class JWTConfig:
    """JWT 配置類別"""
    
    def __init__(self, 
                 secret_key: str,  # 改為必要參數
                 config_file: Optional[str] = None,
                 algorithm: Optional[str] = None,
                 access_token_expires: Optional[int] = None,
                 refresh_token_expires: Optional[int] = None,
                 mongodb_api_url: Optional[str] = None,
                 blacklist_collection: Optional[str] = None,
                 enable_blacklist: Optional[bool] = None):
        """
        初始化 JWT 配置
        
        配置載入優先順序：
        1. 直接傳入的參數（最高優先級）
        2. YAML 配置檔案（用於非敏感配置）
        3. 預設值（最低優先級）
        
        Args:
            secret_key: JWT 密鑰（必要參數，由應用端提供）
            config_file: YAML 配置檔案路徑
            algorithm: JWT 演算法
            access_token_expires: Access token 過期時間（分鐘）
            refresh_token_expires: Refresh token 過期時間（分鐘）
            mongodb_api_url: MongoDB API URL（用於黑名單功能）
            blacklist_collection: 黑名單集合名稱
            enable_blacklist: 是否啟用黑名單功能
            
        Raises:
            ValueError: 當必要的配置未設定時拋出異常
            FileNotFoundError: 當配置檔案不存在時拋出異常
        """
        # 驗證必要參數
        if not secret_key or secret_key.strip() == '':
            raise ValueError("JWT_SECRET_KEY 是必要參數，不能為空。請在創建 JWTConfig 時提供此值。")
        
        # 載入 YAML 配置檔案
        self._config_data = self._load_yaml_config(config_file)
        
        # 設定配置值，優先順序：參數 > YAML > 預設值
        self.secret_key = secret_key
        self.algorithm = algorithm or self._get_config_value('jwt.algorithm', 'HS256')
        self.access_token_expires = access_token_expires if access_token_expires is not None else self._get_config_value('jwt.access_token_expires', 120, int)
        self.refresh_token_expires = refresh_token_expires if refresh_token_expires is not None else self._get_config_value('jwt.refresh_token_expires', 1440, int)
        self.mongodb_api_url = mongodb_api_url if mongodb_api_url is not None else self._get_config_value('mongodb.api_url')
        self.blacklist_collection = blacklist_collection or self._get_config_value('mongodb.blacklist.collection', 'jwt_blacklist')
        self.enable_blacklist = enable_blacklist if enable_blacklist is not None else self._get_config_value('mongodb.blacklist.enabled', True, bool)
    
    def _load_yaml_config(self, config_file: Optional[str] = None) -> Dict[str, Any]:
        """載入 YAML 配置檔案"""
        if config_file is None:
            # 尋找預設配置檔案
            possible_paths = [
                'config.yaml',
                'config.yml',
                'jwt_config.yaml',
                'jwt_config.yml'
            ]
            
            for path in possible_paths:
                if Path(path).exists():
                    config_file = path
                    break
        
        if config_file and Path(config_file).exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    return yaml.safe_load(f) or {}
            except Exception as e:
                print(f"警告：無法載入配置檔案 {config_file}: {e}")
                return {}
        else:
            print("警告：未找到配置檔案，將使用預設值")
            return {}
    
    def _get_config_value(self, key_path: str, default: Any = None, value_type: type = str) -> Any:
        """
        從配置字典中獲取值，支援點分隔的鍵路徑
        
        Args:
            key_path: 配置鍵路徑，如 'jwt.algorithm'
            default: 預設值
            value_type: 值類型轉換函數
            
        Returns:
            配置值
        """
        try:
            # 支援點分隔的鍵路徑
            keys = key_path.split('.')
            value = self._config_data
            
            for key in keys:
                value = value[key]
            
            # 類型轉換
            if value_type == bool and isinstance(value, str):
                return value.lower() in ('true', '1', 'yes', 'on')
            elif value_type != str:
                return value_type(value)
            else:
                return value
                
        except (KeyError, TypeError, ValueError):
            return default
    
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
        將配置轉換為字典（不包含敏感資訊）
        
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
    
    def __str__(self) -> str:
        """字串表示（不包含敏感資訊）"""
        config_dict = self.to_dict()
        return f"JWTConfig({', '.join(f'{k}={v}' for k, v in config_dict.items())})"

# 移除預設配置函數，改為提供工廠函數
def create_jwt_config(secret_key: str, **kwargs) -> JWTConfig:
    """
    創建 JWT 配置的工廠函數
    
    Args:
        secret_key: JWT 密鑰（必要參數）
        **kwargs: 其他配置參數
        
    Returns:
        JWTConfig 實例
    """
    return JWTConfig(secret_key=secret_key, **kwargs) 