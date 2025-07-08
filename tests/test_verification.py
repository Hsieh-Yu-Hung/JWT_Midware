"""
Tests for JWT verification functions (v2.0.0)

Tests the verification functionality only, as business logic has been moved to main projects.
"""

import pytest
import jwt
from datetime import datetime, timedelta, timezone
from jwt_auth_middleware import JWTConfig, set_jwt_config, verify_token, verify_access_token, verify_refresh_token

@pytest.fixture
def setup_config():
    """設置測試配置"""
    test_config = JWTConfig(
        secret_key="test-jwt-secret",
        config_file="tests/test_config.yaml"
    )
    set_jwt_config(test_config)
    return test_config

def create_test_token(payload, secret_key="test-jwt-secret", expires_minutes=30):
    """Helper function to create test tokens"""
    token_payload = payload.copy()
    token_payload.update({
        "exp": datetime.now(timezone.utc) + timedelta(minutes=expires_minutes),
        "iat": datetime.now(timezone.utc)
    })
    return jwt.encode(token_payload, secret_key, algorithm="HS256")

def test_verify_token_valid(setup_config):
    """測試有效 token 驗證"""
    test_data = {
        "sub": "test@example.com",
        "email": "test@example.com",
        "type": "access"
    }
    token = create_test_token(test_data)
    
    payload = verify_token(token)
    assert payload["sub"] == "test@example.com"
    assert payload["email"] == "test@example.com"
    assert payload["type"] == "access"

def test_verify_token_invalid_signature(setup_config):
    """測試無效簽名的 token"""
    test_data = {
        "sub": "test@example.com",
        "email": "test@example.com",
        "type": "access"
    }
    # 使用錯誤的密鑰創建 token
    token = create_test_token(test_data, secret_key="wrong-secret")
    
    with pytest.raises(Exception, match="Invalid token"):
        verify_token(token)

def test_verify_token_expired(setup_config):
    """測試過期 token"""
    test_data = {
        "sub": "test@example.com",
        "email": "test@example.com",
        "type": "access"
    }
    # 創建過期的 token
    token = create_test_token(test_data, expires_minutes=-10)
    
    with pytest.raises(Exception, match="expired"):
        verify_token(token)

def test_verify_access_token_valid(setup_config):
    """測試有效的 access token"""
    test_data = {
        "sub": "test@example.com",
        "email": "test@example.com",
        "type": "access"
    }
    token = create_test_token(test_data)
    
    payload = verify_access_token(token)
    assert payload["sub"] == "test@example.com"
    assert payload["type"] == "access"

def test_verify_access_token_wrong_type(setup_config):
    """測試錯誤類型的 token"""
    test_data = {
        "sub": "test@example.com",
        "email": "test@example.com",
        "type": "refresh"  # 錯誤的類型
    }
    token = create_test_token(test_data)
    
    with pytest.raises(Exception, match="expected access token"):
        verify_access_token(token)

def test_verify_refresh_token_valid(setup_config):
    """測試有效的 refresh token"""
    test_data = {
        "sub": "test@example.com",
        "email": "test@example.com",
        "type": "refresh"
    }
    token = create_test_token(test_data)
    
    payload = verify_refresh_token(token)
    assert payload["sub"] == "test@example.com"
    assert payload["type"] == "refresh"

def test_verify_refresh_token_wrong_type(setup_config):
    """測試錯誤類型的 refresh token"""
    test_data = {
        "sub": "test@example.com",
        "email": "test@example.com",
        "type": "access"  # 錯誤的類型
    }
    token = create_test_token(test_data)
    
    with pytest.raises(Exception, match="expected refresh token"):
        verify_refresh_token(token)

def test_verify_token_missing_type(setup_config):
    """測試缺少 type 欄位的 token"""
    test_data = {
        "sub": "test@example.com",
        "email": "test@example.com"
        # 缺少 type 欄位
    }
    token = create_test_token(test_data)
    
    # 一般驗證應該通過
    payload = verify_token(token)
    assert payload["sub"] == "test@example.com"
    
    # 但特定類型驗證應該失敗
    with pytest.raises(Exception, match="expected access token"):
        verify_access_token(token)

def test_verify_token_with_roles(setup_config):
    """測試包含角色的 token"""
    test_data = {
        "sub": "test@example.com",
        "email": "test@example.com",
        "type": "access",
        "roles": ["user", "admin"]
    }
    token = create_test_token(test_data)
    
    payload = verify_access_token(token)
    assert payload["sub"] == "test@example.com"
    assert "roles" in payload
    assert "user" in payload["roles"]
    assert "admin" in payload["roles"]

def test_verify_token_with_permissions(setup_config):
    """測試包含權限的 token"""
    test_data = {
        "sub": "test@example.com",
        "email": "test@example.com",
        "type": "access",
        "permissions": ["read_user", "delete_user"]
    }
    token = create_test_token(test_data)
    
    payload = verify_access_token(token)
    assert payload["sub"] == "test@example.com"
    assert "permissions" in payload
    assert "read_user" in payload["permissions"]
    assert "delete_user" in payload["permissions"]

def test_verify_token_malformed(setup_config):
    """測試格式錯誤的 token"""
    with pytest.raises(Exception, match="Invalid token"):
        verify_token("not.a.valid.token")

def test_verify_token_empty(setup_config):
    """測試空 token"""
    with pytest.raises(Exception, match="Invalid token"):
        verify_token("")

def test_verify_token_none(setup_config):
    """測試 None token"""
    with pytest.raises(Exception, match="Invalid token"):
        verify_token(None)

def test_config_not_initialized():
    """測試未初始化配置時的錯誤"""
    # 重置配置
    from jwt_auth_middleware import set_jwt_config
    set_jwt_config(None)
    
    test_data = {
        "sub": "test@example.com",
        "email": "test@example.com",
        "type": "access"
    }
    token = create_test_token(test_data)
    
    with pytest.raises(RuntimeError, match="JWT 配置未初始化"):
        verify_token(token)

if __name__ == "__main__":
    print("🧪 Running verification tests for jwt_auth_middleware v2.0.0...")
    
    # 設置測試配置
    test_config = JWTConfig(
        secret_key="test-jwt-secret",
        config_file="tests/test_config.yaml"
    )
    set_jwt_config(test_config)
    
    print("✅ All verification tests completed!") 