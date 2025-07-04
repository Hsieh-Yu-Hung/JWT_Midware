#!/usr/bin/env python3
"""
Flask 應用範例 - 展示新的 JWT 配置系統

此範例展示如何在實際的 Flask 應用中使用新的配置系統：
1. 應用端負責管理 JWT_SECRET_KEY
2. 使用 config.yaml 管理非敏感配置
3. 初始化 JWT 中間件
"""

import os
from flask import Flask, request, jsonify
from jwt_auth_middleware import (
    JWTConfig, set_jwt_config, create_access_token, 
    create_refresh_token, verify_access_token, revoke_token,
    token_required, admin_required, role_required
)

# 創建 Flask 應用
app = Flask(__name__)

def initialize_jwt_system():
    """初始化 JWT 系統"""
    # 從環境變數獲取密鑰（推薦做法）
    secret_key = os.getenv('JWT_SECRET_KEY')
    if not secret_key:
        print("警告：未設定 JWT_SECRET_KEY 環境變數，使用預設密鑰（僅用於開發）")
        secret_key = "dev_secret_key_change_in_production"
    
    # 創建 JWT 配置
    config = JWTConfig(
        secret_key=secret_key,
        # 其他配置會從 config.yaml 載入，或使用預設值
        algorithm="HS256",
        access_token_expires=30,  # 30 分鐘
        refresh_token_expires=1440,  # 24 小時
        mongodb_api_url="https://your-mongodb-api.com",  # 實際應用中應從 config.yaml 載入
        blacklist_collection="jwt_blacklist",
        enable_blacklist=True
    )
    
    # 設定全域配置
    set_jwt_config(config)
    
    print(f"JWT 系統已初始化")
    print(f"演算法: {config.algorithm}")
    print(f"Access Token 過期時間: {config.access_token_expires} 分鐘")
    print(f"Refresh Token 過期時間: {config.refresh_token_expires} 分鐘")
    print(f"啟用黑名單: {config.enable_blacklist}")

# 模擬使用者資料庫
users_db = {
    "admin@example.com": {
        "password": "admin123",
        "roles": ["admin", "user"],
        "permissions": ["read", "write", "delete"]
    },
    "user@example.com": {
        "password": "user123",
        "roles": ["user"],
        "permissions": ["read", "write"]
    }
}

@app.route('/login', methods=['POST'])
def login():
    """登入端點"""
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return jsonify({"error": "請提供 email 和 password"}), 400
    
    user = users_db.get(email)
    if not user or user['password'] != password:
        return jsonify({"error": "無效的憑證"}), 401
    
    # 創建 token 資料
    token_data = {
        "sub": email,
        "email": email,
        "roles": user['roles'],
        "permissions": user['permissions']
    }
    
    # 創建 token 對
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)
    
    return jsonify({
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "Bearer",
        "expires_in": 1800  # 30 分鐘
    })

@app.route('/refresh', methods=['POST'])
def refresh():
    """重新整理 token 端點"""
    data = request.get_json()
    refresh_token = data.get('refresh_token')
    
    if not refresh_token:
        return jsonify({"error": "請提供 refresh_token"}), 400
    
    try:
        # 驗證 refresh token
        payload = verify_access_token(refresh_token)
        
        # 移除過期時間和類型標記
        payload.pop("exp", None)
        payload.pop("type", None)
        payload.pop("iat", None)
        
        # 創建新的 access token
        new_access_token = create_access_token(payload)
        
        return jsonify({
            "access_token": new_access_token,
            "token_type": "Bearer",
            "expires_in": 1800
        })
    except Exception as e:
        return jsonify({"error": f"Token 重新整理失敗: {str(e)}"}), 401

@app.route('/logout', methods=['POST'])
@token_required
def logout(current_user):
    """登出端點"""
    auth_header = request.headers.get('Authorization')
    if auth_header and auth_header.startswith('Bearer '):
        token = auth_header.split(' ')[1]
        revoke_token(token, reason="user_logout")
    
    return jsonify({"message": "登出成功"})

@app.route('/profile', methods=['GET'])
@token_required
def get_profile(current_user):
    """獲取使用者資料（需要認證）"""
    return jsonify({
        "message": "認證成功",
        "user": current_user
    })

@app.route('/admin', methods=['GET'])
@admin_required
def admin_only(current_user):
    """管理員專用端點"""
    return jsonify({
        "message": "管理員存取成功",
        "user": current_user
    })

@app.route('/user', methods=['GET'])
@role_required(["user"])
def user_only(current_user):
    """使用者專用端點"""
    return jsonify({
        "message": "使用者存取成功",
        "user": current_user
    })

@app.route('/health', methods=['GET'])
def health_check():
    """健康檢查端點"""
    return jsonify({
        "status": "healthy",
        "message": "JWT 認證中間件運行正常"
    })

if __name__ == '__main__':
    # 初始化 JWT 系統
    initialize_jwt_system()
    
    # 啟動應用
    print("\n啟動 Flask 應用...")
    print("測試端點:")
    print("  POST /login - 登入")
    print("  POST /refresh - 重新整理 token")
    print("  POST /logout - 登出")
    print("  GET  /profile - 獲取使用者資料")
    print("  GET  /admin - 管理員端點")
    print("  GET  /user - 使用者端點")
    print("  GET  /health - 健康檢查")
    print("\n範例登入資料:")
    print("  admin@example.com / admin123")
    print("  user@example.com / user123")
    
    app.run(debug=True, host='0.0.0.0', port=5000) 