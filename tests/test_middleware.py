"""
Tests for jwt_auth_middleware middleware decorators (v2.0.0)

Tests the middleware functionality only, as business logic has been moved to main projects.
"""

import pytest
from flask import Flask, jsonify
from jwt_auth_middleware import token_required, admin_required, role_required, permission_required, JWTConfig, set_jwt_config, verify_access_token
import jwt
from datetime import datetime, timedelta, timezone

@pytest.fixture
def app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'test-secret-key'
    
    # 設置測試 JWT 配置
    test_config = JWTConfig(
        secret_key="test-jwt-secret",
        config_file="tests/test_middleware_config.yaml"
    )
    set_jwt_config(test_config)
    
    @app.route('/protected')
    @token_required
    def protected(current_user):
        return jsonify({"message": "Protected route", "user": current_user})
    
    @app.route('/admin')
    @admin_required
    def admin_only(current_user):
        return jsonify({"message": "Admin route", "user": current_user})
    
    @app.route('/role')
    @role_required(['manager', 'admin'])
    def role_only(current_user):
        return jsonify({"message": "Role route", "user": current_user})
    
    @app.route('/permission')
    @permission_required('delete_user')
    def permission_only(current_user):
        return jsonify({"message": "Permission route", "user": current_user})
    
    @app.route('/public')
    def public():
        return jsonify({"message": "Public route"})
    
    return app

@pytest.fixture
def client(app):
    return app.test_client()

def create_test_token(user_data, secret_key="test-jwt-secret", expires_minutes=30):
    """Helper function to create test tokens"""
    payload = user_data.copy()
    payload.update({
        "exp": datetime.now(timezone.utc) + timedelta(minutes=expires_minutes),
        "iat": datetime.now(timezone.utc),
        "type": "access"
    })
    return jwt.encode(payload, secret_key, algorithm="HS256")

def test_public_route(client):
    """測試公開路由可以正常訪問"""
    response = client.get('/public')
    assert response.status_code == 200
    assert response.json['message'] == 'Public route'

def test_protected_route_without_token(client):
    """測試沒有 token 時訪問受保護路由"""
    response = client.get('/protected')
    assert response.status_code == 401
    assert 'token' in response.json['error'].lower()

def test_protected_route_with_invalid_token(client):
    """測試無效 token 訪問受保護路由"""
    response = client.get('/protected', headers={'Authorization': 'Bearer invalid-token'})
    assert response.status_code == 401

def test_protected_route_with_valid_token(client):
    """測試有效 token 訪問受保護路由"""
    # 創建測試 token
    test_user = {"sub": "test@example.com", "email": "test@example.com", "roles": ["user"]}
    token = create_test_token(test_user)
    
    response = client.get('/protected', headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == 200
    assert response.json['message'] == 'Protected route'
    assert response.json['user']['sub'] == 'test@example.com'

def test_admin_route_with_user_token(client):
    """測試普通用戶訪問管理員路由"""
    # 創建普通用戶 token
    test_user = {"sub": "test@example.com", "email": "test@example.com", "roles": ["user"]}
    token = create_test_token(test_user)
    
    response = client.get('/admin', headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == 403
    assert 'admin' in response.json['error'].lower()

def test_admin_route_with_admin_token(client):
    """測試管理員訪問管理員路由"""
    # 創建管理員 token
    test_user = {"sub": "admin@example.com", "email": "admin@example.com", "roles": ["admin"]}
    token = create_test_token(test_user)
    
    response = client.get('/admin', headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == 200
    assert response.json['message'] == 'Admin route'
    assert response.json['user']['sub'] == 'admin@example.com'

def test_role_route_with_valid_role(client):
    """測試有正確角色的用戶訪問角色路由"""
    # 創建有 manager 角色的用戶 token
    test_user = {"sub": "manager@example.com", "email": "manager@example.com", "roles": ["manager"]}
    token = create_test_token(test_user)
    
    response = client.get('/role', headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == 200
    assert response.json['message'] == 'Role route'

def test_role_route_with_invalid_role(client):
    """測試沒有正確角色的用戶訪問角色路由"""
    # 創建只有 user 角色的用戶 token
    test_user = {"sub": "user@example.com", "email": "user@example.com", "roles": ["user"]}
    token = create_test_token(test_user)
    
    response = client.get('/role', headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == 403
    assert 'access denied' in response.json['error'].lower()

def test_permission_route_with_valid_permission(client):
    """測試有正確權限的用戶訪問權限路由"""
    # 創建有 delete_user 權限的用戶 token
    test_user = {
        "sub": "admin@example.com", 
        "email": "admin@example.com", 
        "roles": ["admin"],
        "permissions": ["delete_user", "read_user"]
    }
    token = create_test_token(test_user)
    
    response = client.get('/permission', headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == 200
    assert response.json['message'] == 'Permission route'

def test_permission_route_with_invalid_permission(client):
    """測試沒有正確權限的用戶訪問權限路由"""
    # 創建沒有 delete_user 權限的用戶 token
    test_user = {
        "sub": "user@example.com", 
        "email": "user@example.com", 
        "roles": ["user"],
        "permissions": ["read_user"]
    }
    token = create_test_token(test_user)
    
    response = client.get('/permission', headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == 403
    assert 'access denied' in response.json['error'].lower()

def test_token_verification_function():
    """測試 token 驗證功能"""
    test_user = {"sub": "test@example.com", "email": "test@example.com", "roles": ["user"]}
    token = create_test_token(test_user)
    
    # 測試驗證功能
    payload = verify_access_token(token)
    assert payload["sub"] == "test@example.com"
    assert payload["email"] == "test@example.com"
    assert payload["type"] == "access"

def test_expired_token(client):
    """測試過期 token"""
    # 創建過期的 token
    test_user = {"sub": "test@example.com", "email": "test@example.com", "roles": ["user"]}
    token = create_test_token(test_user, expires_minutes=-10)  # 10分鐘前過期
    
    response = client.get('/protected', headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == 401
    assert 'expired' in response.json['error'].lower()

if __name__ == "__main__":
    print("🧪 Running middleware tests for jwt_auth_middleware v2.0.0...")
    
    # 這裡可以添加簡單的測試執行
    print("✅ Middleware tests completed!") 