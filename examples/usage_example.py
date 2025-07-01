"""
JWT Auth Middleware 使用範例

展示如何在其他 Flask 專案中使用 JWT 認證中間件
"""

from flask import Flask, request, jsonify
from jwt_auth_middleware import (
    token_required, 
    admin_required, 
    role_required,
    create_access_token, 
    verify_token,
    JWTConfig
)

app = Flask(__name__)

# 設定 JWT 配置
jwt_config = JWTConfig(
    secret_key="your-super-secret-key-here",
    access_token_expires=60  # 1 小時
)

# 模擬使用者資料庫
users_db = {
    "admin@example.com": {
        "password": "admin123",
        "role": "admin",
        "permissions": ["read", "write", "delete"]
    },
    "user@example.com": {
        "password": "user123", 
        "role": "user",
        "permissions": ["read"]
    }
}

@app.route('/login', methods=['POST'])
def login():
    """登入端點"""
    data = request.json
    
    if not data or not data.get("email") or not data.get("password"):
        return jsonify({"message": "Email and password required"}), 400
    
    email = data.get("email")
    password = data.get("password")
    
    # 驗證使用者
    if email not in users_db or users_db[email]["password"] != password:
        return jsonify({"message": "Invalid credentials"}), 401
    
    user = users_db[email]
    
    # 建立 JWT token
    token_data = {
        "sub": email,
        "email": email,
        "role": user["role"],
        "permissions": user["permissions"]
    }
    
    token = create_access_token(token_data)
    
    return jsonify({
        "access_token": token,
        "user": {
            "email": email,
            "role": user["role"]
        }
    })

@app.route('/public', methods=['GET'])
def public_route():
    """公開端點 - 不需要認證"""
    return jsonify({"message": "This is a public endpoint"})

@app.route('/protected', methods=['GET'])
@token_required
def protected_route(current_user):
    """受保護的端點 - 需要有效的 JWT token"""
    return jsonify({
        "message": "This is a protected endpoint",
        "user": current_user
    })

@app.route('/admin-only', methods=['GET'])
@admin_required
def admin_only_route(current_user):
    """管理員專用端點 - 需要管理員角色"""
    return jsonify({
        "message": "This is an admin-only endpoint",
        "user": current_user
    })

@app.route('/user-role', methods=['GET'])
@role_required("user")
def user_role_route(current_user):
    """使用者角色端點 - 需要 user 角色"""
    return jsonify({
        "message": "This endpoint requires user role",
        "user": current_user
    })

@app.route('/multi-role', methods=['GET'])
@role_required(["admin", "moderator"])
def multi_role_route(current_user):
    """多角色端點 - 需要 admin 或 moderator 角色"""
    return jsonify({
        "message": "This endpoint requires admin or moderator role",
        "user": current_user
    })

@app.route('/profile', methods=['GET'])
@token_required
def get_profile(current_user):
    """取得使用者資料"""
    email = current_user.get("email")
    if email in users_db:
        user_data = users_db[email]
        return jsonify({
            "email": email,
            "role": user_data["role"],
            "permissions": user_data["permissions"]
        })
    else:
        return jsonify({"message": "User not found"}), 404

@app.route('/logout', methods=['POST'])
@token_required
def logout(current_user):
    """登出端點"""
    # 在實際應用中，這裡會將 token 加入黑名單
    return jsonify({"message": "Logout successful"})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 