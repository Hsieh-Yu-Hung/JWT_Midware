"""
測試新的配置系統
"""

import os
import tempfile
import yaml
import pytest
from unittest.mock import patch
from jwt_auth_middleware.config import JWTConfig


class TestNewConfigSystem:
    """測試新的配置系統"""
    
    def setup_method(self):
        """每個測試前的設定"""
        # 清除可能存在的環境變數
        env_vars_to_clear = [
            'JWT_SECRET_KEY', 'JWT_ALGORITHM', 'JWT_ACCESS_TOKEN_EXPIRES',
            'JWT_REFRESH_TOKEN_EXPIRES', 'MONGODB_API_URL', 
            'JWT_BLACKLIST_COLLECTION', 'JWT_ENABLE_BLACKLIST'
        ]
        for var in env_vars_to_clear:
            if var in os.environ:
                del os.environ[var]
    
    def test_config_with_yaml_file(self):
        """測試從 YAML 檔案載入配置"""
        # 使用現有的測試配置檔案
        config_file = "tests/test_new_config.yaml"
        
        # 設定環境變數（敏感資訊）
        os.environ['JWT_SECRET_KEY'] = 'test_secret_key'
        
        # 載入配置
        config = JWTConfig(secret_key='test_secret_key', config_file=config_file)
        
        # 驗證配置
        assert config.secret_key == 'test_secret_key'
        assert config.algorithm == 'HS512'
        assert config.access_token_expires == 60
        assert config.refresh_token_expires == 720
        assert config.mongodb_api_url == 'https://test-mongodb-api.example.com'
        assert config.blacklist_collection == 'test_blacklist'
        assert config.enable_blacklist is False
    
    def test_config_priority_order(self):
        """測試配置優先順序"""
        # 使用現有的測試配置檔案
        config_file = "tests/test_new_config.yaml"
        
        # 設定環境變數
        os.environ['JWT_SECRET_KEY'] = 'env_secret_key'
        
        # 載入配置（新的 API 不支援程式化覆蓋）
        config = JWTConfig(
            secret_key='env_secret_key',
            config_file=config_file
        )
        
        # 驗證配置
        assert config.secret_key == 'env_secret_key'  # 從參數
        assert config.algorithm == 'HS512'  # 從 YAML
        assert config.access_token_expires == 60  # 從 YAML
        assert config.refresh_token_expires == 720  # 從 YAML
        assert config.mongodb_api_url == 'https://test-mongodb-api.example.com'  # 從 YAML
        assert config.blacklist_collection == 'test_blacklist'  # 從 YAML
        assert config.enable_blacklist is False  # 從 YAML
    
    def test_missing_yaml_file(self):
        """測試缺少 YAML 檔案時拋出異常"""
        os.environ['JWT_SECRET_KEY'] = 'test_secret_key'
        
        # 應該拋出 FileNotFoundError
        with pytest.raises(FileNotFoundError, match="配置檔案不存在"):
            JWTConfig(secret_key='test_secret_key', config_file='nonexistent.yaml')
    
    def test_invalid_yaml_file(self):
        """測試無效的 YAML 檔案"""
        # 創建無效的 YAML 檔案
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("invalid: yaml: content: [")
            config_file = f.name
        
        try:
            os.environ['JWT_SECRET_KEY'] = 'test_secret_key'
            
            # 應該拋出 ValueError
            with pytest.raises(ValueError, match="無法載入配置檔案"):
                JWTConfig(secret_key='test_secret_key', config_file=config_file)
            
        finally:
            os.unlink(config_file)
    
    def test_missing_secret_key(self):
        """測試缺少 JWT 密鑰時拋出異常"""
        with pytest.raises(ValueError, match="JWT_SECRET_KEY 是必要參數"):
            JWTConfig(secret_key="", config_file="tests/test_new_config.yaml")
    
    def test_config_validation(self):
        """測試配置驗證"""
        os.environ['JWT_SECRET_KEY'] = 'test_secret_key'
        
        # 有效配置
        config = JWTConfig(
            secret_key='test_secret_key',
            config_file='tests/test_new_config.yaml'
        )
        assert config.validate() is True
    
    def test_config_to_dict(self):
        """測試配置轉換為字典（不包含敏感資訊）"""
        os.environ['JWT_SECRET_KEY'] = 'test_secret_key'
        
        config = JWTConfig(
            secret_key='test_secret_key',
            config_file='tests/test_new_config.yaml'
        )
        
        config_dict = config.to_dict()
        
        # 應該不包含敏感資訊
        assert 'secret_key' not in config_dict
        assert config_dict['algorithm'] == 'HS512'
        assert config_dict['access_token_expires'] == 60
        assert config_dict['mongodb_api_url'] == 'https://test-mongodb-api.example.com'
    
    def test_config_string_representation(self):
        """測試配置的字串表示（不包含敏感資訊）"""
        os.environ['JWT_SECRET_KEY'] = 'test_secret_key'
        
        config = JWTConfig(
            secret_key='test_secret_key',
            config_file='tests/test_new_config.yaml'
        )
        
        config_str = str(config)
        
        # 應該不包含敏感資訊
        assert 'secret_key' not in config_str
        assert 'test_secret_key' not in config_str
        assert 'algorithm=HS512' in config_str
        assert 'access_token_expires=60' in config_str
    
    def test_dotenv_loading_control(self):
        """測試 .env 檔案載入控制"""
        # 這個測試在新的設計中不再適用，因為不再自動載入 .env
        # 改為測試配置創建
        config = JWTConfig(secret_key='test_secret_key', config_file='tests/test_new_config.yaml')
        assert config.secret_key == 'test_secret_key' 