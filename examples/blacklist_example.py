"""
JWT 黑名單系統使用範例

展示如何使用 MongoDB API 實作的黑名單功能
"""

from flask import Flask, request, jsonify
from jwt_auth_middleware import (
    JWTManager, 
    create_access_token, 
    verify_token, 
    revoke_token,
    is_token_blacklisted,
    remove_from_blacklist,
    cleanup_expired_blacklist_tokens,
    get_blacklist_statistics,
    initialize_blacklist_system,
    JWTConfig
)

app = Flask(__name__)

# 配置 JWT
jwt_config = JWTConfig(
    secret_key="your-super-secret-key-change-this-in-production",
    access_token_expires=30,  # 30 分鐘
    mongodb_api_url="http://your-mongodb-api-url.com",  # 替換為您的 MongoDB API URL
    blacklist_collection="jwt_blacklist",
    enable_blacklist=True
)

# 初始化 JWT 管理器
jwt_manager = JWTManager(app, jwt_config)

# 初始化黑名單系統
@app.before_first_request
def setup_blacklist():
    """在第一次請求前初始化黑名單系統"""
    success = initialize_blacklist_system()
    if success:
        print("黑名單系統初始化成功")
    else:
        print("黑名單系統初始化失敗")

# 登入端點
@app.route('/login', methods=['POST'])
def login():
    """使用者登入並取得 JWT token"""
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    # 這裡應該驗證使用者憑證
    if username == "admin" and password == "password":
        # 建立 token
        token_data = {"sub": username, "role": "admin"}
        token = create_access_token(token_data)
        
        return jsonify({
            "access_token": token,
            "token_type": "bearer"
        })
    else:
        return jsonify({"error": "Invalid credentials"}), 401

# 受保護的端點
@app.route('/protected', methods=['GET'])
@jwt_manager.token_required
def protected_route(current_user):
    """需要有效 JWT token 的端點"""
    return jsonify({
        "message": "This is a protected route",
        "user": current_user
    })

# 撤銷 token 端點
@app.route('/logout', methods=['POST'])
@jwt_manager.token_required
def logout(current_user):
    """登出並撤銷 token"""
    auth_header = request.headers.get('Authorization')
    if auth_header and auth_header.startswith('Bearer '):
        token = auth_header.split(' ')[1]
        
        # 撤銷 token
        success = revoke_token(token, reason="user_logout")
        
        if success:
            return jsonify({"message": "Successfully logged out"})
        else:
            return jsonify({"error": "Failed to revoke token"}), 500
    
    return jsonify({"error": "No token provided"}), 400

# 檢查 token 是否在黑名單中
@app.route('/check-blacklist', methods=['POST'])
def check_blacklist():
    """檢查 token 是否在黑名單中"""
    data = request.get_json()
    token = data.get('token')
    
    if not token:
        return jsonify({"error": "Token is required"}), 400
    
    is_blacklisted = is_token_blacklisted(token)
    
    return jsonify({
        "token": token,
        "is_blacklisted": is_blacklisted
    })

# 從黑名單中移除 token（管理員功能）
@app.route('/admin/remove-from-blacklist', methods=['POST'])
@jwt_manager.admin_required
def admin_remove_from_blacklist(current_user):
    """從黑名單中移除 token（管理員功能）"""
    data = request.get_json()
    token = data.get('token')
    
    if not token:
        return jsonify({"error": "Token is required"}), 400
    
    success = remove_from_blacklist(token)
    
    if success:
        return jsonify({"message": "Token removed from blacklist"})
    else:
        return jsonify({"error": "Failed to remove token from blacklist"}), 500

# 清理過期 tokens
@app.route('/admin/cleanup-expired', methods=['POST'])
@jwt_manager.admin_required
def admin_cleanup_expired(current_user):
    """清理已過期的黑名單 tokens"""
    cleaned_count = cleanup_expired_blacklist_tokens()
    
    return jsonify({
        "message": f"Cleaned up {cleaned_count} expired tokens"
    })

# 取得黑名單統計資訊
@app.route('/admin/blacklist-stats', methods=['GET'])
@jwt_manager.admin_required
def admin_blacklist_stats(current_user):
    """取得黑名單統計資訊"""
    stats = get_blacklist_statistics()
    
    return jsonify(stats)

# 測試端點
@app.route('/test-token', methods=['POST'])
def test_token():
    """測試 token 驗證"""
    data = request.get_json()
    token = data.get('token')
    
    if not token:
        return jsonify({"error": "Token is required"}), 400
    
    try:
        # 驗證 token
        payload = verify_token(token)
        
        # 檢查是否在黑名單中
        is_blacklisted = is_token_blacklisted(token)
        
        return jsonify({
            "valid": True,
            "payload": payload,
            "is_blacklisted": is_blacklisted
        })
    except Exception as e:
        return jsonify({
            "valid": False,
            "error": str(e),
            "is_blacklisted": is_token_blacklisted(token)
        })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 