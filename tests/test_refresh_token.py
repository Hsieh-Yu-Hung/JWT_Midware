"""
測試 Refresh Token 功能
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
from jwt_auth_middleware import (
    create_token_pair,
    verify_access_token,
    verify_refresh_token,
    refresh_access_token,
    revoke_token_pair,
    JWTConfig
)

class TestRefreshToken:
    """測試 Refresh Token 功能"""
    
    def setup_method(self):
        """設定測試環境"""
        import os
        os.environ['JWT_SECRET_KEY'] = 'test-secret-key'
        os.environ['JWT_ALGORITHM'] = 'HS256'
        os.environ['MONGODB_API_URL'] = 'http://test-api.com'
        os.environ['JWT_BLACKLIST_COLLECTION'] = 'test_blacklist'
        os.environ['JWT_ENABLE_BLACKLIST'] = 'true'
        os.environ['JWT_ACCESS_TOKEN_EXPIRES'] = '30'
        os.environ['JWT_REFRESH_TOKEN_EXPIRES'] = '1440'

        # 使用新的配置系統
        from jwt_auth_middleware import JWTConfig, set_jwt_config
        test_config = JWTConfig(
            secret_key="test-secret-key",
            algorithm="HS256",
            access_token_expires=30,
            refresh_token_expires=1440,
            mongodb_api_url="http://test-api.com",
            blacklist_collection="test_blacklist",
            enable_blacklist=True
        )
        set_jwt_config(test_config)
    
    def test_create_token_pair(self):
        """測試建立 Token 對"""
        data = {"user_id": 123, "role": "user"}
        tokens = create_token_pair(data)
        
        assert "access_token" in tokens
        assert "refresh_token" in tokens
        assert isinstance(tokens["access_token"], str)
        assert isinstance(tokens["refresh_token"], str)
        
        # 驗證兩個 token 不同
        assert tokens["access_token"] != tokens["refresh_token"]
    
    def test_verify_access_token(self):
        """測試驗證 Access Token"""
        data = {"user_id": 123, "role": "user"}
        tokens = create_token_pair(data)
        
        payload = verify_access_token(tokens["access_token"])
        assert payload["user_id"] == 123
        assert payload["type"] == "access"
        assert "iat" in payload  # 發行時間
    
    def test_verify_refresh_token(self):
        """測試驗證 Refresh Token"""
        data = {"user_id": 123, "role": "user"}
        tokens = create_token_pair(data)
        
        payload = verify_refresh_token(tokens["refresh_token"])
        assert payload["user_id"] == 123
        assert payload["type"] == "refresh"
        assert "iat" in payload  # 發行時間
    
    def test_refresh_access_token(self):
        """測試使用 Refresh Token 取得新的 Access Token"""
        data = {"user_id": 123, "role": "user"}
        tokens = create_token_pair(data)
        
        new_access_token = refresh_access_token(tokens["refresh_token"])
        assert new_access_token is not None
        
        # 驗證新的 Access Token
        payload = verify_access_token(new_access_token)
        assert payload["user_id"] == 123
        assert payload["type"] == "access"
        
        # 驗證新的 token 與原始的不同
        assert new_access_token != tokens["access_token"]
    
    def test_refresh_access_token_with_invalid_refresh_token(self):
        """測試使用無效的 Refresh Token"""
        invalid_token = "invalid.refresh.token"
        new_access_token = refresh_access_token(invalid_token)
        assert new_access_token is None
    
    def test_refresh_access_token_with_access_token(self):
        """測試使用 Access Token 作為 Refresh Token（應該失敗）"""
        data = {"user_id": 123, "role": "user"}
        tokens = create_token_pair(data)
        
        new_access_token = refresh_access_token(tokens["access_token"])
        assert new_access_token is None
    
    @patch('jwt_auth_middleware.jwt_utils._get_blacklist_manager')
    def test_revoke_token_pair(self, mock_get_blacklist_manager):
        """測試撤銷 Token 對"""
        mock_blacklist_manager = MagicMock()
        mock_blacklist_manager.add_to_blacklist.return_value = True
        mock_blacklist_manager.is_blacklisted.return_value = False
        mock_get_blacklist_manager.return_value = mock_blacklist_manager
        
        data = {"user_id": 123}
        tokens = create_token_pair(data)
        
        success = revoke_token_pair(
            tokens["access_token"], 
            tokens["refresh_token"], 
            "test_logout"
        )
        assert success is True
        assert mock_blacklist_manager.add_to_blacklist.call_count == 2
    
    @patch('jwt_auth_middleware.jwt_utils._get_blacklist_manager')
    def test_revoke_token_pair_with_blacklist_disabled(self, mock_get_blacklist_manager):
        """測試黑名單停用時的撤銷行為"""
        mock_blacklist_manager = MagicMock()
        mock_blacklist_manager.add_to_blacklist.return_value = False
        mock_get_blacklist_manager.return_value = mock_blacklist_manager
        
        data = {"user_id": 123}
        tokens = create_token_pair(data)
        
        success = revoke_token_pair(
            tokens["access_token"], 
            tokens["refresh_token"], 
            "test_logout"
        )
        assert success is False
    
    def test_token_type_validation(self):
        """測試 Token 類型驗證"""
        data = {"user_id": 123, "role": "user"}
        tokens = create_token_pair(data)
        
        # 嘗試用 verify_access_token 驗證 refresh_token（應該失敗）
        with pytest.raises(Exception) as exc_info:
            verify_access_token(tokens["refresh_token"])
        assert "expected access token" in str(exc_info.value)
        
        # 嘗試用 verify_refresh_token 驗證 access_token（應該失敗）
        with pytest.raises(Exception) as exc_info:
            verify_refresh_token(tokens["access_token"])
        assert "expected refresh token" in str(exc_info.value)
    
    def test_token_expiration_times(self):
        """測試 Token 過期時間設定"""
        config = JWTConfig(secret_key="test-secret-key")
        
        # 驗證預設過期時間
        assert config.access_token_expires == 120  # 從 config.yaml 載入
        assert config.refresh_token_expires == 1440  # 從 config.yaml 載入
        
        # 驗證自定義過期時間
        custom_config = JWTConfig(
            secret_key="test-secret-key",
            access_token_expires=60,
            refresh_token_expires=2880
        )
        assert custom_config.access_token_expires == 60
        assert custom_config.refresh_token_expires == 2880
    
    def test_config_validation(self):
        """測試配置驗證"""
        # 有效配置
        valid_config = JWTConfig(
            secret_key="test-key",
            mongodb_api_url="http://test.com",
            access_token_expires=30,
            refresh_token_expires=1440
        )
        assert valid_config.validate() is True
        
        # 無效配置 - 空 secret_key 會拋出異常
        with pytest.raises(ValueError, match="JWT_SECRET_KEY 是必要參數"):
            invalid_config1 = JWTConfig(
                secret_key="",
                mongodb_api_url="http://test.com",
                access_token_expires=30,
                refresh_token_expires=1440
            )
        
        # 無效配置 - access_token_expires <= 0
        invalid_config2 = JWTConfig(
            secret_key="test-key",
            mongodb_api_url="http://test.com",
            access_token_expires=0,
            refresh_token_expires=1440
        )
        assert invalid_config2.validate() is False
        
        # 無效配置 - refresh_token_expires <= 0
        invalid_config3 = JWTConfig(
            secret_key="test-key",
            mongodb_api_url="http://test.com",
            access_token_expires=30,
            refresh_token_expires=0
        )
        assert invalid_config3.validate() is False
    
    def test_token_payload_integrity(self):
        """測試 Token payload 完整性"""
        data = {"user_id": 123, "role": "user", "custom_field": "test_value"}
        tokens = create_token_pair(data)
        
        # 驗證 Access Token payload
        access_payload = verify_access_token(tokens["access_token"])
        assert access_payload["user_id"] == 123
        assert access_payload["role"] == "user"
        assert access_payload["custom_field"] == "test_value"
        assert access_payload["type"] == "access"
        assert "exp" in access_payload
        assert "iat" in access_payload
        
        # 驗證 Refresh Token payload
        refresh_payload = verify_refresh_token(tokens["refresh_token"])
        assert refresh_payload["user_id"] == 123
        assert refresh_payload["role"] == "user"
        assert refresh_payload["custom_field"] == "test_value"
        assert refresh_payload["type"] == "refresh"
        assert "exp" in refresh_payload
        assert "iat" in refresh_payload
    
    def test_multiple_refresh_operations(self):
        """測試多次重新整理操作"""
        data = {"user_id": 123, "role": "user"}
        tokens = create_token_pair(data)
        
        # 第一次重新整理
        new_token1 = refresh_access_token(tokens["refresh_token"])
        assert new_token1 is not None
        
        # 第二次重新整理
        new_token2 = refresh_access_token(tokens["refresh_token"])
        assert new_token2 is not None
        
        # 驗證兩個新 token 都有效但不同
        payload1 = verify_access_token(new_token1)
        payload2 = verify_access_token(new_token2)
        
        assert payload1["user_id"] == 123
        assert payload2["user_id"] == 123
        assert new_token1 != new_token2
    
    def test_environment_variable_override(self):
        """測試環境變數覆蓋配置"""
        import os
        
        # 設定自定義環境變數
        os.environ['JWT_ACCESS_TOKEN_EXPIRES'] = '60'
        os.environ['JWT_REFRESH_TOKEN_EXPIRES'] = '2880'
        
        # 重新建立配置（環境變數在新設計中不再自動載入）
        config = JWTConfig(secret_key="test-secret-key")
        
        # 由於新設計不再自動載入環境變數，這些值應該來自 config.yaml 或預設值
        assert config.access_token_expires == 120  # 來自 config.yaml
        assert config.refresh_token_expires == 1440  # 來自 config.yaml
        
        # 清理環境變數
        os.environ.pop('JWT_ACCESS_TOKEN_EXPIRES', None)
        os.environ.pop('JWT_REFRESH_TOKEN_EXPIRES', None)
    
    def test_token_creation_with_custom_expires_delta(self):
        """測試使用自定義過期時間建立 Access Token"""
        from jwt_auth_middleware import create_access_token
        from datetime import timedelta
        
        data = {"user_id": 123, "role": "user"}
        
        # 使用自定義過期時間
        custom_expires = timedelta(hours=2)
        token = create_access_token(data, expires_delta=custom_expires)
        
        # 驗證 token
        payload = verify_access_token(token)
        assert payload["user_id"] == 123
        assert payload["type"] == "access"
    
    def test_token_creation_with_empty_data(self):
        """測試使用空資料建立 Token"""
        empty_data = {}
        tokens = create_token_pair(empty_data)
        
        # 驗證 token 仍然可以建立
        assert "access_token" in tokens
        assert "refresh_token" in tokens
        
        # 驗證 payload 包含必要的欄位
        access_payload = verify_access_token(tokens["access_token"])
        assert "type" in access_payload
        assert "exp" in access_payload
        assert "iat" in access_payload
    
    def test_token_creation_with_complex_data(self):
        """測試使用複雜資料建立 Token"""
        complex_data = {
            "user_id": 123,
            "username": "test_user",
            "roles": ["user", "moderator"],
            "permissions": ["read", "write"],
            "metadata": {
                "last_login": "2024-01-01T00:00:00Z",
                "ip_address": "192.168.1.1"
            },
            "settings": {
                "theme": "dark",
                "language": "zh-TW"
            }
        }
        
        tokens = create_token_pair(complex_data)
        
        # 驗證 Access Token
        access_payload = verify_access_token(tokens["access_token"])
        assert access_payload["user_id"] == 123
        assert access_payload["username"] == "test_user"
        assert access_payload["roles"] == ["user", "moderator"]
        assert access_payload["permissions"] == ["read", "write"]
        assert access_payload["metadata"]["last_login"] == "2024-01-01T00:00:00Z"
        assert access_payload["settings"]["theme"] == "dark"
        
        # 驗證 Refresh Token
        refresh_payload = verify_refresh_token(tokens["refresh_token"])
        assert refresh_payload["user_id"] == 123
        assert refresh_payload["username"] == "test_user"
        assert refresh_payload["roles"] == ["user", "moderator"]
    
    def test_token_verification_with_missing_type(self):
        """測試驗證缺少 type 欄位的 Token"""
        from jwt_auth_middleware import create_access_token
        import jwt
        from datetime import datetime, timedelta, timezone

        # 建立沒有 type 欄位的 token，使用與配置相同的 secret key
        data = {"user_id": 123}
        now = datetime.now(timezone.utc)
        to_encode = data.copy()
        to_encode.update({
            "exp": int((now + timedelta(minutes=30)).timestamp()),
            "iat": int(now.timestamp())
        })
        token = jwt.encode(to_encode, "test-secret-key", algorithm="HS256")

        # 驗證應該失敗
        with pytest.raises(Exception) as exc_info:
            verify_access_token(token)
        assert "Invalid token type" in str(exc_info.value)

    def test_token_verification_with_wrong_type(self):
        """測試驗證錯誤類型的 Token"""
        from jwt_auth_middleware import create_access_token
        import jwt
        from datetime import datetime, timedelta, timezone

        # 建立錯誤類型的 token，使用與配置相同的 secret key
        data = {"user_id": 123}
        now = datetime.now(timezone.utc)
        to_encode = data.copy()
        to_encode.update({
            "exp": int((now + timedelta(minutes=30)).timestamp()),
            "type": "wrong_type",
            "iat": int(now.timestamp())
        })
        token = jwt.encode(to_encode, "test-secret-key", algorithm="HS256")

        # 驗證應該失敗
        with pytest.raises(Exception) as exc_info:
            verify_access_token(token)
        assert "Invalid token type" in str(exc_info.value)
    
    def test_refresh_token_with_expired_refresh_token(self):
        """測試使用過期的 Refresh Token"""
        # 建立一個過期的 refresh token
        from jwt_auth_middleware import create_refresh_token
        import jwt
        
        data = {"user_id": 123}
        to_encode = data.copy()
        to_encode.update({
            "exp": datetime.now() - timedelta(minutes=1),  # 已過期
            "type": "refresh",
            "iat": datetime.now() - timedelta(minutes=2)
        })
        expired_token = jwt.encode(to_encode, "test-secret-key", algorithm="HS256")
        
        # 嘗試重新整理應該失敗
        new_token = refresh_access_token(expired_token)
        assert new_token is None
    
    def test_revoke_token_pair_with_invalid_tokens(self):
        """測試撤銷無效的 Token 對"""
        invalid_access_token = "invalid.access.token"
        invalid_refresh_token = "invalid.refresh.token"
        
        # 撤銷無效 token 應該失敗
        success = revoke_token_pair(invalid_access_token, invalid_refresh_token, "test")
        assert success is False
    
    def test_config_to_dict_method(self):
        """測試配置轉換為字典"""
        config = JWTConfig(
            secret_key="test-key",
            algorithm="HS256",
            access_token_expires=30,
            refresh_token_expires=1440,
            mongodb_api_url="http://test.com",
            blacklist_collection="test_blacklist",
            enable_blacklist=True
        )
        
        config_dict = config.to_dict()
        
        assert config_dict["algorithm"] == "HS256"
        assert config_dict["access_token_expires"] == 30
        assert config_dict["refresh_token_expires"] == 1440
        assert config_dict["mongodb_api_url"] == "http://test.com"
        assert config_dict["blacklist_collection"] == "test_blacklist"
        assert config_dict["enable_blacklist"] is True
        assert "secret_key" not in config_dict  # secret_key 不應該包含在字典中 