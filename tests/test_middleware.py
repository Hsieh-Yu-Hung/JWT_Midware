import pytest
from flask import Flask, jsonify
from jwt_auth_middleware import token_required, admin_required, create_access_token, JWTConfig, set_jwt_config
import datetime

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
    
    @app.route('/public')
    def public():
        return jsonify({"message": "Public route"})
    
    return app

@pytest.fixture
def client(app):
    return app.test_client()

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

def test_protected_route_with_valid_token(client, app):
    """測試有效 token 訪問受保護路由"""
    # 創建測試 token
    test_user = {"sub": "test@example.com", "email": "test@example.com", "roles": ["user"]}
    token = create_access_token(test_user)
    
    response = client.get('/protected', headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == 200
    assert response.json['message'] == 'Protected route'
    assert response.json['user']['sub'] == 'test@example.com'

def test_admin_route_with_user_token(client, app):
    """測試普通用戶訪問管理員路由"""
    # 創建普通用戶 token
    test_user = {"sub": "test@example.com", "email": "test@example.com", "roles": ["user"]}
    token = create_access_token(test_user)
    
    response = client.get('/admin', headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == 403
    assert 'admin' in response.json['error'].lower()

def test_admin_route_with_admin_token(client, app):
    """測試管理員訪問管理員路由"""
    # 創建管理員 token
    test_user = {"sub": "admin@example.com", "email": "admin@example.com", "roles": ["admin"]}
    token = create_access_token(test_user)
    
    response = client.get('/admin', headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == 200
    assert response.json['message'] == 'Admin route'
    assert response.json['user']['sub'] == 'admin@example.com' 