#!/usr/bin/env python3
"""
完整的 JWT Authentication 使用範例

展示如何使用所有功能，包括 Refresh Token 機制
"""

import os
import sys
from datetime import datetime

# 添加專案路徑
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, request, jsonify
from jwt_auth_middleware import (
    JWTConfig,
    create_token_pair,
    verify_access_token,
    refresh_access_token,
    revoke_token_pair,
    token_required,
    admin_required,
    role_required,
    is_token_blacklisted,
    cleanup_expired_blacklist_tokens,
    get_blacklist_statistics,
    set_jwt_config
)

app = Flask(__name__)

# 模擬使用者資料庫
users_db = {
    "user1": {"password": "password1", "role": "user", "user_id": 1},
    "admin1": {"password": "adminpass", "role": "admin", "user_id": 2},
    "manager1": {"password": "managerpass", "role": "manager", "user_id": 3}
}

# 模擬使用者 session 儲存（實際應用中應使用 Redis 或資料庫）
user_sessions = {}

@app.route('/login', methods=['POST'])
def login():
    """使用者登入"""
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({"error": "Username and password required"}), 400
    
    user = users_db.get(username)
    if not user or user['password'] != password:
        return jsonify({"error": "Invalid credentials"}), 401
    
    # 建立 token 對
    token_data = {
        "user_id": user['user_id'],
        "username": username,
        "role": user['role'],
        "login_time": datetime.now().isoformat()
    }
    
    tokens = create_token_pair(token_data)
    
    # 儲存 refresh token（實際應用中應儲存在資料庫）
    user_sessions[user['user_id']] = tokens['refresh_token']
    
    return jsonify({
        "access_token": tokens["access_token"],
        "refresh_token": tokens["refresh_token"],
        "user": {
            "user_id": user['user_id'],
            "username": username,
            "role": user['role']
        }
    })

@app.route('/refresh', methods=['POST'])
def refresh():
    """使用 Refresh Token 取得新的 Access Token"""
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"error": "Refresh token required"}), 401
    
    refresh_token = auth_header.split(' ')[1]
    
    # 驗證 refresh token
    try:
        payload = verify_access_token(refresh_token)
        user_id = payload['user_id']
        
        # 檢查儲存的 refresh token 是否匹配
        stored_refresh_token = user_sessions.get(user_id)
        if not stored_refresh_token or stored_refresh_token != refresh_token:
            return jsonify({"error": "Invalid refresh token"}), 401
        
        # 取得新的 access token
        new_access_token = refresh_access_token(refresh_token)
        if new_access_token:
            return jsonify({"access_token": new_access_token})
        else:
            return jsonify({"error": "Failed to refresh token"}), 401
            
    except Exception as e:
        return jsonify({"error": str(e)}), 401

@app.route('/logout', methods=['POST'])
@token_required
def logout(current_user):
    """使用者登出"""
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"error": "Access token required"}), 401
    
    access_token = auth_header.split(' ')[1]
    user_id = current_user['user_id']
    
    # 取得儲存的 refresh token
    refresh_token = user_sessions.get(user_id)
    
    if refresh_token:
        # 撤銷兩個 token
        success = revoke_token_pair(access_token, refresh_token, "user_logout")
        if success:
            # 清除 session
            user_sessions.pop(user_id, None)
            return jsonify({"message": "Logged out successfully"})
        else:
            return jsonify({"error": "Failed to logout"}), 500
    else:
        return jsonify({"error": "No refresh token found"}), 400

@app.route('/protected', methods=['GET'])
@token_required
def protected_route(current_user):
    """受保護的路由"""
    return jsonify({
        "message": "Access granted",
        "user": current_user
    })

@app.route('/admin', methods=['GET'])
@admin_required
def admin_route(current_user):
    """管理員專用路由"""
    return jsonify({
        "message": "Admin access granted",
        "user": current_user
    })

@app.route('/manager', methods=['GET'])
@role_required(['manager', 'admin'])
def manager_route(current_user):
    """管理員或經理專用路由"""
    return jsonify({
        "message": "Manager access granted",
        "user": current_user
    })

@app.route('/check-token', methods=['POST'])
def check_token():
    """檢查 token 狀態"""
    data = request.get_json()
    token = data.get('token')
    
    if not token:
        return jsonify({"error": "Token required"}), 400
    
    # 檢查是否在黑名單中
    is_blacklisted = is_token_blacklisted(token)
    
    try:
        payload = verify_access_token(token)
        return jsonify({
            "valid": True,
            "blacklisted": is_blacklisted,
            "payload": payload
        })
    except Exception as e:
        return jsonify({
            "valid": False,
            "blacklisted": is_blacklisted,
            "error": str(e)
        })

@app.route('/admin/blacklist-stats', methods=['GET'])
@admin_required
def blacklist_stats(current_user):
    """取得黑名單統計資訊（管理員專用）"""
    stats = get_blacklist_statistics()
    return jsonify(stats)

@app.route('/admin/cleanup-blacklist', methods=['POST'])
@admin_required
def cleanup_blacklist(current_user):
    """清理過期的黑名單記錄（管理員專用）"""
    cleaned_count = cleanup_expired_blacklist_tokens()
    return jsonify({
        "message": f"Cleaned {cleaned_count} expired tokens",
        "cleaned_count": cleaned_count
    })

@app.route('/health', methods=['GET'])
def health_check():
    """健康檢查端點"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.2.0"
    })

if __name__ == '__main__':
    # 使用新的配置系統
    config = JWTConfig(
        secret_key="your-super-secret-key",
        config_file="../jwt_auth_middleware/config_example.yaml"
    )
    
    # 設定全域配置
    set_jwt_config(config)
    
    print("🚀 啟動 JWT Authentication 範例伺服器...")
    print("📝 可用的測試帳號:")
    print("   - user1 / password1 (一般使用者)")
    print("   - admin1 / adminpass (管理員)")
    print("   - manager1 / managerpass (經理)")
    print("🌐 伺服器運行在: http://localhost:5000")
    print("📖 API 端點:")
    print("   POST /login - 登入")
    print("   POST /refresh - 重新整理 token")
    print("   POST /logout - 登出")
    print("   GET /protected - 受保護的路由")
    print("   GET /admin - 管理員路由")
    print("   GET /manager - 經理路由")
    
    app.run(debug=True, port=5000) 