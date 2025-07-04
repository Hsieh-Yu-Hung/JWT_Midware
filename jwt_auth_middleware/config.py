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
                 secret_key: str,  # 必要參數
                 config_file: str):  # 必要參數
        """
        初始化 JWT 配置
        
        配置載入優先順序：
        1. YAML 配置檔案（主要配置來源）
        2. 預設值（備用）
        
        Args:
            secret_key: JWT 密鑰（必要參數，由應用端提供）
            config_file: YAML 配置檔案路徑（必要參數，由應用端提供）
            
        Raises:
            ValueError: 當必要的配置未設定時拋出異常
            FileNotFoundError: 當配置檔案不存在時拋出異常
        """
        # 驗證必要參數
        if not secret_key or secret_key.strip() == '':
            raise ValueError("JWT_SECRET_KEY 是必要參數，不能為空。請在創建 JWTConfig 時提供此值。")
        
        if not config_file or config_file.strip() == '':
            raise ValueError("config_file 是必要參數，不能為空。請在創建 JWTConfig 時提供配置檔案路徑。")
        
        # 載入 YAML 配置檔案
        self._config_data = self._load_yaml_config(config_file)
        
        # 驗證配置檔案結構
        self._validate_config_structure()
        
        # 設定配置值，從配置檔案載入
        self.secret_key = secret_key
        self.algorithm = self._get_config_value('jwt.algorithm', 'HS256')
        self.access_token_expires = self._get_config_value('jwt.access_token_expires', 120, int)
        self.refresh_token_expires = self._get_config_value('jwt.refresh_token_expires', 1440, int)
        
        # 根據 API 模式決定 MongoDB API URL
        self.api_mode = self._get_config_value('api.mode', 'internal')
        if self.api_mode not in ['internal', 'public']:
            raise ValueError(f"無效的 API 模式: {self.api_mode}。可選值: internal, public")
        
        if self.api_mode == 'internal':
            self.mongodb_api_url = self._get_config_value('mongodb.internal_api_url')
        else:
            self.mongodb_api_url = self._get_config_value('mongodb.public_api_url')
        
        self.blacklist_collection = self._get_config_value('mongodb.blacklist.collection', 'jwt_blacklist')
        self.enable_blacklist = self._get_config_value('mongodb.blacklist.enabled', True, bool)
    
    def _load_yaml_config(self, config_file: str) -> Dict[str, Any]:
        """載入 YAML 配置檔案"""
        if not Path(config_file).exists():
            raise FileNotFoundError(f"配置檔案不存在：{config_file}")
        
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {}
        except Exception as e:
            raise ValueError(f"無法載入配置檔案 {config_file}: {e}")
    
    def _validate_config_structure(self) -> None:
        """驗證配置檔案結構是否正確"""
        required_sections = {
            'jwt': ['algorithm', 'access_token_expires', 'refresh_token_expires'],
            'api': ['mode'],
            'mongodb': ['internal_api_url', 'public_api_url', 'blacklist']
        }
        
        for section, required_keys in required_sections.items():
            if section not in self._config_data:
                raise ValueError(f"配置檔案缺少必要區段: {section}")
            
            section_data = self._config_data[section]
            for key in required_keys:
                if key not in section_data:
                    raise ValueError(f"配置檔案 {section} 區段缺少必要配置: {key}")
        
        # 驗證 blacklist 子區段
        blacklist_data = self._config_data['mongodb']['blacklist']
        required_blacklist_keys = ['collection', 'enabled']
        for key in required_blacklist_keys:
            if key not in blacklist_data:
                raise ValueError(f"配置檔案 mongodb.blacklist 區段缺少必要配置: {key}")
        
        # 驗證 API 模式值
        api_mode = self._config_data['api']['mode']
        if api_mode not in ['internal', 'public']:
            raise ValueError(f"無效的 API 模式: {api_mode}。可選值: internal, public")
        
        # 驗證 URL 格式
        internal_url = self._config_data['mongodb']['internal_api_url']
        public_url = self._config_data['mongodb']['public_api_url']
        
        if not internal_url.startswith(('http://', 'https://')):
            raise ValueError(f"無效的內部 API URL 格式: {internal_url}")
        if not public_url.startswith(('http://', 'https://')):
            raise ValueError(f"無效的公網 API URL 格式: {public_url}")
        
        # 驗證數值範圍
        access_expires = self._config_data['jwt']['access_token_expires']
        refresh_expires = self._config_data['jwt']['refresh_token_expires']
        
        if not isinstance(access_expires, int) or access_expires <= 0:
            raise ValueError(f"無效的 access_token_expires 值: {access_expires}。必須為正整數")
        if not isinstance(refresh_expires, int) or refresh_expires <= 0:
            raise ValueError(f"無效的 refresh_token_expires 值: {refresh_expires}。必須為正整數")
        
        # 驗證演算法
        algorithm = self._config_data['jwt']['algorithm']
        valid_algorithms = ['HS256', 'HS384', 'HS512', 'RS256', 'RS384', 'RS512']
        if algorithm not in valid_algorithms:
            raise ValueError(f"無效的 JWT 演算法: {algorithm}。可選值: {', '.join(valid_algorithms)}")
    
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
        try:
            if not self.secret_key or self.secret_key.strip() == '':
                return False
            if not self.mongodb_api_url or self.mongodb_api_url.strip() == '':
                return False
            if self.access_token_expires <= 0:
                return False
            if self.refresh_token_expires <= 0:
                return False
            if self.api_mode not in ['internal', 'public']:
                return False
            return True
        except Exception:
            return False
    
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
            'api_mode': self.api_mode,
            'mongodb_api_url': self.mongodb_api_url,
            'blacklist_collection': self.blacklist_collection,
            'enable_blacklist': self.enable_blacklist
        }
    
    def __str__(self) -> str:
        """字串表示（不包含敏感資訊）"""
        config_dict = self.to_dict()
        return f"JWTConfig({', '.join(f'{k}={v}' for k, v in config_dict.items())})"

# 移除預設配置函數，改為提供工廠函數
def create_jwt_config(secret_key: str, config_file: str) -> JWTConfig:
    """
    創建 JWT 配置的工廠函數
    
    Args:
        secret_key: JWT 密鑰（必要參數）
        config_file: YAML 配置檔案路徑（必要參數）
        
    Returns:
        JWTConfig 實例
    """
    return JWTConfig(secret_key=secret_key, config_file=config_file) 