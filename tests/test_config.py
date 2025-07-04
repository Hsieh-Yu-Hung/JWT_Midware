"""
測試 JWT 配置系統
"""

import pytest
import os
from jwt_auth_middleware import JWTConfig, set_jwt_config, create_access_token, verify_token

def test_config_without_dotenv():
    """測試配置可以在不載入 .env 檔案的情況下工作"""
    # 設置測試環境變數
    test_config = JWTConfig(
        secret_key="test-secret-key",
        config_file="tests/test_config.yaml"
    )
    
    # 設置配置
    set_jwt_config(test_config)
    
    # 測試 token 創建和驗證
    test_data = {"sub": "test@example.com", "email": "test@example.com"}
    token = create_access_token(test_data)
    
    # 驗證 token
    payload = verify_token(token)
    assert payload["sub"] == "test@example.com"
    assert payload["email"] == "test@example.com"

def test_config_validation():
    """測試配置驗證"""
    # 測試有效配置
    valid_config = JWTConfig(
        secret_key="test-secret",
        config_file="tests/test_config.yaml"
    )
    assert valid_config.validate() is True
    
    # 測試無效配置（空密鑰會拋出異常）
    with pytest.raises(ValueError, match="JWT_SECRET_KEY 是必要參數"):
        invalid_config = JWTConfig(
            secret_key="",
            config_file="tests/test_config.yaml"
        )

def test_config_to_dict():
    """測試配置轉換為字典"""
    config = JWTConfig(
        secret_key="test-secret",
        config_file="tests/test_config.yaml"
    )
    
    config_dict = config.to_dict()
    assert config_dict["algorithm"] == "HS256"
    assert config_dict["access_token_expires"] == 30
    assert config_dict["refresh_token_expires"] == 1440
    assert config_dict["mongodb_api_url"] == "http://localhost:3001"
    assert config_dict["blacklist_collection"] == "jwt_blacklist"
    assert config_dict["enable_blacklist"] is False 