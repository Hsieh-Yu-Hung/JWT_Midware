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
        # 創建臨時 YAML 配置檔案
        config_data = {
            'jwt': {
                'algorithm': 'HS512',
                'access_token_expires': 60,
                'refresh_token_expires': 720
            },
            'mongodb': {
                'api_url': 'https://test-mongodb-api.example.com',
                'blacklist': {
                    'collection': 'test_blacklist',
                    'enabled': False
                }
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(config_data, f)
            config_file = f.name
        
        try:
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
            
        finally:
            # 清理臨時檔案
            os.unlink(config_file)
    
    def test_config_priority_order(self):
        """測試配置優先順序"""
        # 創建 YAML 配置檔案
        config_data = {
            'jwt': {
                'algorithm': 'HS256',
                'access_token_expires': 120
            },
            'mongodb': {
                'api_url': 'https://yaml-mongodb.example.com',
                'blacklist': {
                    'collection': 'yaml_blacklist',
                    'enabled': True
                }
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(config_data, f)
            config_file = f.name
        
        try:
            # 設定環境變數
            os.environ['JWT_SECRET_KEY'] = 'env_secret_key'
            os.environ['JWT_ALGORITHM'] = 'HS384'  # 覆蓋 YAML 中的值
            
            # 程式化設定（最高優先級）
            config = JWTConfig(
                secret_key='env_secret_key',
                config_file=config_file,
                algorithm='HS512',  # 應該覆蓋環境變數和 YAML
                access_token_expires=30,  # 應該覆蓋 YAML
                mongodb_api_url='https://programmatic-mongodb.example.com'  # 應該覆蓋 YAML
            )
            
            # 驗證優先順序：程式化 > 環境變數 > YAML
            assert config.secret_key == 'env_secret_key'  # 從環境變數
            assert config.algorithm == 'HS512'  # 程式化設定（最高優先級）
            assert config.access_token_expires == 30  # 程式化設定
            assert config.refresh_token_expires == 1440  # YAML 中的值
            assert config.mongodb_api_url == 'https://programmatic-mongodb.example.com'  # 程式化設定
            assert config.blacklist_collection == 'yaml_blacklist'  # YAML 中的值
            assert config.enable_blacklist is True  # YAML 中的值
            
        finally:
            os.unlink(config_file)
    
    def test_missing_yaml_file(self):
        """測試缺少 YAML 檔案時使用預設值"""
        os.environ['JWT_SECRET_KEY'] = 'test_secret_key'
        
        # 應該使用預設值
        config = JWTConfig(secret_key='test_secret_key', config_file='nonexistent.yaml')
        
        assert config.secret_key == 'test_secret_key'
        assert config.algorithm == 'HS256'  # 預設值
        assert config.access_token_expires == 120  # 預設值
        assert config.refresh_token_expires == 1440  # 預設值
        assert config.blacklist_collection == 'jwt_blacklist'  # 預設值
        assert config.enable_blacklist is True  # 預設值
    
    def test_invalid_yaml_file(self):
        """測試無效的 YAML 檔案"""
        # 創建無效的 YAML 檔案
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("invalid: yaml: content: [")
            config_file = f.name
        
        try:
            os.environ['JWT_SECRET_KEY'] = 'test_secret_key'
            
            # 應該使用預設值而不拋出異常
            config = JWTConfig(secret_key='test_secret_key', config_file=config_file)
            
            assert config.secret_key == 'test_secret_key'
            assert config.algorithm == 'HS256'  # 預設值
            
        finally:
            os.unlink(config_file)
    
    def test_missing_secret_key(self):
        """測試缺少 JWT 密鑰時拋出異常"""
        with pytest.raises(ValueError, match="JWT_SECRET_KEY 是必要參數"):
            JWTConfig(secret_key="")
    
    def test_config_validation(self):
        """測試配置驗證"""
        os.environ['JWT_SECRET_KEY'] = 'test_secret_key'
        
        # 有效配置
        config = JWTConfig(
            secret_key='test_secret_key',
            mongodb_api_url='https://test.example.com',
            access_token_expires=60,
            refresh_token_expires=1440
        )
        assert config.validate() is True
        
        # 無效配置
        invalid_config = JWTConfig(
            secret_key='valid_key',  # 有效密鑰
            mongodb_api_url='',  # 空 URL
            access_token_expires=0  # 無效過期時間
        )
        assert invalid_config.validate() is False
    
    def test_config_to_dict(self):
        """測試配置轉換為字典（不包含敏感資訊）"""
        os.environ['JWT_SECRET_KEY'] = 'test_secret_key'
        
        config = JWTConfig(
            secret_key='test_secret_key',
            algorithm='HS512',
            access_token_expires=60,
            mongodb_api_url='https://test.example.com'
        )
        
        config_dict = config.to_dict()
        
        # 應該不包含敏感資訊
        assert 'secret_key' not in config_dict
        assert config_dict['algorithm'] == 'HS512'
        assert config_dict['access_token_expires'] == 60
        assert config_dict['mongodb_api_url'] == 'https://test.example.com'
    
    def test_config_string_representation(self):
        """測試配置的字串表示（不包含敏感資訊）"""
        os.environ['JWT_SECRET_KEY'] = 'test_secret_key'
        
        config = JWTConfig(
            secret_key='test_secret_key',
            algorithm='HS512',
            access_token_expires=60
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
        config = JWTConfig(secret_key='test_secret_key')
        assert config.secret_key == 'test_secret_key' 