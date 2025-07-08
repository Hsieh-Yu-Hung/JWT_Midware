"""
Tests for JWT configuration system (v2.0.0)

Tests the configuration functionality only, as business logic has been moved to main projects.
"""

import pytest
import os
from jwt_auth_middleware import JWTConfig, set_jwt_config, verify_token, verify_access_token

def test_config_without_dotenv():
    """測試配置可以在不載入 .env 檔案的情況下工作"""
    # 設置測試環境變數
    test_config = JWTConfig(
        secret_key="test-secret-key",
        config_file="tests/test_config.yaml"
    )
    
    # 設置配置
    set_jwt_config(test_config)
    
    # 測試 token 驗證（使用外部創建的 token）
    import jwt
    from datetime import datetime, timedelta, timezone
    
    # 創建測試 token
    test_data = {
        "sub": "test@example.com", 
        "email": "test@example.com",
        "type": "access",
        "exp": datetime.now(timezone.utc) + timedelta(minutes=30),
        "iat": datetime.now(timezone.utc)
    }
    token = jwt.encode(test_data, "test-secret-key", algorithm="HS256")
    
    # 驗證 token
    payload = verify_token(token)
    assert payload["sub"] == "test@example.com"
    assert payload["email"] == "test@example.com"
    assert payload["type"] == "access"

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

def test_config_creation():
    """測試配置創建函數"""
    from jwt_auth_middleware import create_jwt_config
    
    config = create_jwt_config(
        secret_key="test-secret",
        config_file="tests/test_config.yaml"
    )
    
    assert config.secret_key == "test-secret"
    assert config.algorithm == "HS256"
    assert config.access_token_expires == 30
    assert config.refresh_token_expires == 1440

def test_config_string_representation():
    """測試配置的字串表示"""
    config = JWTConfig(
        secret_key="test-secret",
        config_file="tests/test_config.yaml"
    )
    
    config_str = str(config)
    assert "JWTConfig" in config_str
    assert "algorithm" in config_str
    assert "access_token_expires" in config_str
    # 確保敏感資訊不會出現在字串表示中
    assert "test-secret" not in config_str

def test_config_repr():
    """測試配置的詳細字串表示"""
    config = JWTConfig(
        secret_key="test-secret",
        config_file="tests/test_config.yaml"
    )
    
    config_repr = repr(config)
    config_str = str(config)
    # 由於沒有自定義 __repr__，預設會顯示類別名稱和記憶體位置
    assert "JWTConfig" in config_repr
    # 確保敏感資訊不會出現在字串表示中
    assert "test-secret" not in config_str

def test_config_with_different_algorithms():
    """測試不同演算法的配置"""
    # 測試 HS256
    config_hs256 = JWTConfig(
        secret_key="test-secret",
        config_file="tests/test_config.yaml"
    )
    assert config_hs256.algorithm == "HS256"
    
    # 測試其他演算法（需要修改配置檔案）
    # 這裡只測試預設演算法

def test_config_api_mode():
    """測試 API 模式配置"""
    config = JWTConfig(
        secret_key="test-secret",
        config_file="tests/test_config.yaml"
    )
    
    assert config.api_mode in ["internal", "public"]
    assert config.mongodb_api_url is not None

def test_config_blacklist_settings():
    """測試黑名單設定"""
    config = JWTConfig(
        secret_key="test-secret",
        config_file="tests/test_config.yaml"
    )
    
    assert isinstance(config.enable_blacklist, bool)
    assert config.blacklist_collection is not None

if __name__ == "__main__":
    print("🧪 Running configuration tests for jwt_auth_middleware v2.0.0...")
    
    test_config_without_dotenv()
    test_config_validation()
    test_config_to_dict()
    test_config_creation()
    test_config_string_representation()
    test_config_repr()
    test_config_with_different_algorithms()
    test_config_api_mode()
    test_config_blacklist_settings()
    
    print("✅ All configuration tests passed!") 