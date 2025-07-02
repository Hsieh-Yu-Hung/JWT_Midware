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
    initialize_blacklist_system
)

class TestBlacklistManager:
    """測試黑名單管理器"""
    
    def setup_method(self):
        """設定測試環境"""
        self.config = JWTConfig(
            secret_key="test-secret-key",
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
        mock_post.return_value = mock_response
        
        token = "test.jwt.token"
        result = self.blacklist_mgr.add_to_blacklist(token, "test_reason")
        
        assert result is True
        mock_post.assert_called_once()
    
    @patch('requests.post')
    def test_add_to_blacklist_failure(self, mock_post):
        """測試加入黑名單失敗"""
        # 模擬失敗的 API 回應
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_post.return_value = mock_response
        
        token = "test.jwt.token"
        result = self.blacklist_mgr.add_to_blacklist(token, "test_reason")
        
        assert result is False
    
    @patch('requests.post')
    def test_is_blacklisted_true(self, mock_post):
        """測試檢查 token 在黑名單中"""
        # 模擬找到文件的 API 回應
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"documents": [{"token_hash": "test_hash"}]}
        mock_post.return_value = mock_response
        
        token = "test.jwt.token"
        result = self.blacklist_mgr.is_blacklisted(token)
        
        assert result is True
    
    @patch('requests.post')
    def test_is_blacklisted_false(self, mock_post):
        """測試檢查 token 不在黑名單中"""
        # 模擬找不到文件的 API 回應
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"documents": []}
        mock_post.return_value = mock_response
        
        token = "test.jwt.token"
        result = self.blacklist_mgr.is_blacklisted(token)
        
        assert result is False
    
    @patch('requests.post')
    def test_remove_from_blacklist_success(self, mock_post):
        """測試成功從黑名單移除"""
        # 模擬成功的 API 回應
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        token = "test.jwt.token"
        result = self.blacklist_mgr.remove_from_blacklist(token)
        
        assert result is True
    
    @patch('requests.post')
    def test_cleanup_expired_tokens(self, mock_post):
        """測試清理過期 tokens"""
        # 模擬成功的 API 回應
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"deleted_count": 5}
        mock_post.return_value = mock_response
        
        result = self.blacklist_mgr.cleanup_expired_tokens()
        
        assert result == 5
    
    @patch('requests.post')
    def test_get_blacklist_stats(self, mock_post):
        """測試取得黑名單統計資訊"""
        # 模擬 API 回應
        mock_response1 = MagicMock()
        mock_response1.status_code = 200
        mock_response1.json.return_value = {"count": 10}
        
        mock_response2 = MagicMock()
        mock_response2.status_code = 200
        mock_response2.json.return_value = {"count": 3}
        
        mock_post.side_effect = [mock_response1, mock_response2]
        
        result = self.blacklist_mgr.get_blacklist_stats()
        
        expected = {
            "total_tokens": 10,
            "expired_tokens": 3,
            "active_tokens": 7
        }
        assert result == expected

class TestBlacklistIntegration:
    """測試黑名單整合功能"""
    
    def setup_method(self):
        """設定測試環境"""
        self.config = JWTConfig(
            secret_key="test-secret-key",
            access_token_expires=30,
            mongodb_api_url="http://test-api.com",
            blacklist_collection="test_blacklist",
            enable_blacklist=True
        )
    
    @patch('jwt_auth_middleware.jwt_utils.get_blacklist_manager')
    @patch('jwt_auth_middleware.jwt_utils.verify_token')
    def test_revoke_token_with_blacklist(self, mock_verify, mock_get_manager):
        """測試使用黑名單撤銷 token"""
        # 模擬黑名單管理器
        mock_manager = MagicMock()
        mock_manager.add_to_blacklist.return_value = True
        mock_get_manager.return_value = mock_manager
        
        # 模擬 verify_token 成功
        mock_verify.return_value = {"sub": "test_user", "role": "user"}
        
        # 建立測試 token
        token_data = {"sub": "test_user", "role": "user"}
        token = create_access_token(token_data)
        
        # 撤銷 token
        result = revoke_token(token, "test_reason")
        
        assert result is True
        mock_manager.add_to_blacklist.assert_called_once_with(token, "test_reason")
    
    @patch('jwt_auth_middleware.jwt_utils.get_blacklist_manager')
    def test_verify_token_with_blacklist(self, mock_get_manager):
        """測試驗證 token 時檢查黑名單"""
        # 模擬黑名單管理器
        mock_manager = MagicMock()
        mock_manager.is_blacklisted.return_value = True
        mock_get_manager.return_value = mock_manager
        
        # 建立測試 token
        token_data = {"sub": "test_user", "role": "user"}
        token = create_access_token(token_data)
        
        # 驗證 token（應該失敗因為在黑名單中）
        with pytest.raises(Exception, match="Token has been revoked"):
            verify_token(token)
    
    def test_blacklist_disabled(self):
        """測試黑名單功能停用時的行為"""
        # 建立停用黑名單的配置
        config = JWTConfig(
            secret_key="test-secret-key",
            enable_blacklist=False
        )
        
        # 建立測試 token
        token_data = {"sub": "test_user", "role": "user"}
        token = create_access_token(token_data)
        
        # 檢查黑名單狀態（應該返回 False）
        result = is_token_blacklisted(token)
        assert result is False
    
    @patch('jwt_auth_middleware.jwt_utils.init_blacklist_manager')
    def test_initialize_blacklist_system(self, mock_init):
        """測試初始化黑名單系統"""
        mock_init.return_value = None
        
        result = initialize_blacklist_system("http://test-api.com", "test_collection")
        
        assert result is True
        mock_init.assert_called_once()

if __name__ == "__main__":
    pytest.main([__file__]) 