"""
測試 JWT 黑名單功能
"""

import pytest
import jwt
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
from jwt_auth_middleware.blacklist import BlacklistManager
from jwt_auth_middleware.config import JWTConfig
from jwt_auth_middleware.jwt_utils import (
    create_access_token,
    verify_token,
    revoke_token,
    is_token_blacklisted,
    remove_from_blacklist,
    cleanup_expired_blacklist_tokens,
    get_blacklist_statistics,
    initialize_blacklist_system,
    set_jwt_config
)

class TestBlacklistManager:
    """測試黑名單管理器"""
    
    def setup_method(self):
        """設定測試環境"""
        self.config = JWTConfig(
            secret_key="test-secret-key",
            algorithm="HS256",
            access_token_expires=30,
            mongodb_api_url="http://test-api.com",
            blacklist_collection="test_blacklist",
            enable_blacklist=True
        )
        
        self.blacklist_mgr = BlacklistManager(
            mongodb_api_url="http://test-api.com",
            collection_name="test_blacklist",
            jwt_config=self.config
        )
    
    def test_hash_token(self):
        """測試 token 雜湊功能"""
        token = "test.jwt.token"
        hash1 = self.blacklist_mgr._hash_token(token)
        hash2 = self.blacklist_mgr._hash_token(token)
        
        # 相同 token 應該產生相同的雜湊
        assert hash1 == hash2
        assert len(hash1) == 64  # SHA256 雜湊長度
    
    @patch('requests.post')
    def test_add_to_blacklist_success(self, mock_post):
        """測試成功加入黑名單"""
        # 模擬成功的 API 回應
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "ok"}
        mock_post.return_value = mock_response
        
        token = "test.jwt.token"
        result = self.blacklist_mgr.add_to_blacklist(token, "test_reason")
        
        assert result is True
        mock_post.assert_called_once()
    
    @patch('requests.get')
    def test_is_blacklisted_success(self, mock_get):
        """測試成功查詢黑名單"""
        # 模擬成功的 API 回應
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": [{"token_hash": "test_hash"}]}
        mock_get.return_value = mock_response
        
        token = "test.jwt.token"
        result = self.blacklist_mgr.is_blacklisted(token)
        
        assert result is True
        mock_get.assert_called_once()
    
    @patch('requests.get')
    def test_is_blacklisted_not_found(self, mock_get):
        """測試查詢黑名單（未找到）"""
        # 模擬成功的 API 回應（空結果）
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": []}
        mock_get.return_value = mock_response
        
        token = "test.jwt.token"
        result = self.blacklist_mgr.is_blacklisted(token)
        
        assert result is False
        mock_get.assert_called_once()

class TestJWTUtils:
    """測試 JWT 工具函數"""
    
    def setup_method(self):
        """設定測試環境"""
        # 設定測試環境變數
        import os
        os.environ['JWT_SECRET_KEY'] = 'test-secret-key'
        os.environ['JWT_ALGORITHM'] = 'HS256'
        os.environ['MONGODB_API_URL'] = 'http://test-api.com'
        os.environ['JWT_BLACKLIST_COLLECTION'] = 'test_blacklist'
        os.environ['JWT_ENABLE_BLACKLIST'] = 'true'
        
        # 使用新的配置系統
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
    
    def test_create_access_token(self):
        """測試建立 access token"""
        data = {"user_id": 123, "email": "test@example.com"}
        token = create_access_token(data)
        
        assert token is not None
        assert isinstance(token, str)
        assert len(token.split('.')) == 3  # JWT 格式
    
    def test_verify_token(self):
        """測試驗證 token"""
        data = {"user_id": 123, "email": "test@example.com"}
        token = create_access_token(data)
        
        payload = verify_token(token)
        assert payload["user_id"] == 123
        assert payload["email"] == "test@example.com"
    
    @patch('jwt_auth_middleware.jwt_utils._get_blacklist_manager')
    def test_revoke_token_with_blacklist(self, mock_get_blacklist_manager):
        """測試撤銷 token（啟用黑名單）"""
        # 模擬黑名單管理器
        mock_blacklist_manager = MagicMock()
        mock_blacklist_manager.add_to_blacklist.return_value = True
        mock_blacklist_manager.is_blacklisted.return_value = False  # 初始狀態不在黑名單中
        mock_get_blacklist_manager.return_value = mock_blacklist_manager
        
        data = {"user_id": 123}
        token = create_access_token(data)
        
        result = revoke_token(token, "test_reason")
        assert result is True
        mock_blacklist_manager.add_to_blacklist.assert_called_once()
    
    @patch('jwt_auth_middleware.jwt_utils._get_blacklist_manager')
    def test_is_token_blacklisted(self, mock_get_blacklist_manager):
        """測試檢查 token 是否在黑名單中"""
        # 模擬黑名單管理器
        mock_blacklist_manager = MagicMock()
        mock_blacklist_manager.is_blacklisted.return_value = True
        mock_get_blacklist_manager.return_value = mock_blacklist_manager
        
        token = "test.jwt.token"
        result = is_token_blacklisted(token)
        
        assert result is True
        mock_blacklist_manager.is_blacklisted.assert_called_once_with(token)
    
    @patch('jwt_auth_middleware.jwt_utils._get_blacklist_manager')
    def test_remove_from_blacklist(self, mock_get_blacklist_manager):
        """測試從黑名單中移除 token"""
        # 模擬黑名單管理器
        mock_blacklist_manager = MagicMock()
        mock_blacklist_manager.remove_from_blacklist.return_value = True
        mock_get_blacklist_manager.return_value = mock_blacklist_manager
        
        token = "test.jwt.token"
        result = remove_from_blacklist(token)
        
        assert result is True
        mock_blacklist_manager.remove_from_blacklist.assert_called_once_with(token)
    
    @patch('jwt_auth_middleware.jwt_utils._get_blacklist_manager')
    def test_cleanup_expired_tokens(self, mock_get_blacklist_manager):
        """測試清理過期 tokens"""
        # 模擬黑名單管理器
        mock_blacklist_manager = MagicMock()
        mock_blacklist_manager.cleanup_expired_tokens.return_value = 5
        mock_get_blacklist_manager.return_value = mock_blacklist_manager
        
        result = cleanup_expired_blacklist_tokens()
        
        assert result == 5
        mock_blacklist_manager.cleanup_expired_tokens.assert_called_once()
    
    @patch('jwt_auth_middleware.jwt_utils._get_blacklist_manager')
    def test_get_blacklist_statistics(self, mock_get_blacklist_manager):
        """測試取得黑名單統計"""
        # 模擬黑名單管理器
        mock_blacklist_manager = MagicMock()
        mock_stats = {"total_tokens": 10, "expired_tokens": 3, "active_tokens": 7}
        mock_blacklist_manager.get_blacklist_stats.return_value = mock_stats
        mock_get_blacklist_manager.return_value = mock_blacklist_manager
        
        result = get_blacklist_statistics()
        
        assert result == mock_stats
        mock_blacklist_manager.get_blacklist_stats.assert_called_once()
    
    def test_initialize_blacklist_system(self):
        """測試初始化黑名單系統"""
        # 這個測試會重新建立全域 blacklist_manager
        result = initialize_blacklist_system(
            mongodb_api_url="http://test-api.com",
            collection_name="test_collection"
        )
        
        assert result is True

if __name__ == "__main__":
    pytest.main([__file__]) 