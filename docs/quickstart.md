# JWT Auth Middleware 快速開始指南

## 🚀 5 分鐘快速開始

這個指南將幫助您在 5 分鐘內建立一個基本的 JWT 認證系統。

### 步驟 1: 安裝套件

```bash
pip install git+https://github.com/Hsieh-Yu-Hung/JWT_Midware.git
```

### 步驟 2: 建立基本應用程式

建立 `app.py` 檔案：

```python
from flask import Flask, request, jsonify
from jwt_auth_middleware import (
    JWTManager, 
    token_required, 
    create_access_token,
    revoke_token
)

app = Flask(__name__)

# 基本配置
app.config['JWT_SECRET_KEY'] = 'your-super-secret-key-here'
jwt_manager = JWTManager(app)

# 模擬使用者資料庫
users_db = {
    "admin@example.com": {
        "password": "admin123",
        "roles": ["admin"],
        "permissions": ["read", "write", "delete"]
    },
    "user@example.com": {
        "password": "user123", 
        "roles": ["user"],
        "permissions": ["read"]
    }
}

# 登入端點
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    if email in users_db and users_db[email]['password'] == password:
        user = users_db[email]
        token_data = {
            "sub": email,
            "email": email,
            "roles": user['roles'],
            "permissions": user['permissions']
        }
        token = create_access_token(token_data)
        return jsonify({"access_token": token, "message": "Login successful"})
    
    return jsonify({"error": "Invalid credentials"}), 401

# 受保護的端點
@app.route('/protected')
@token_required
def protected_route(current_user):
    return jsonify({
        "message": "Access granted",
        "user": current_user
    })

# 登出端點
@app.route('/logout', methods=['POST'])
@token_required
def logout(current_user):
    auth_header = request.headers.get('Authorization')
    if auth_header and auth_header.startswith('Bearer '):
        token = auth_header.split(' ')[1]
        revoke_token(token, reason="user_logout")
    return jsonify({"message": "Logged out successfully"})

if __name__ == '__main__':
    app.run(debug=True)
```

### 步驟 3: 測試應用程式

1. 啟動應用程式：
```bash
python app.py
```

2. 登入（使用 curl 或 Postman）：
```bash
curl -X POST http://localhost:5000/login \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@example.com", "password": "admin123"}'
```

3. 使用取得的 token 存取受保護的端點：
```bash
curl http://localhost:5000/protected \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

4. 登出：
```bash
curl -X POST http://localhost:5000/logout \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

## 🔧 進階功能

### 啟用黑名單功能

如果您想要啟用 token 撤銷功能，需要設定 MongoDB API：

```python
from jwt_auth_middleware import initialize_blacklist_system

# 在應用程式啟動時初始化
@app.before_first_request
def setup_blacklist():
    initialize_blacklist_system(
        mongodb_api_url="http://your-mongodb-api.com"
    )
```

### 角色基礎存取控制

```python
from jwt_auth_middleware import role_required

@app.route('/admin-only')
@role_required(["admin"])
def admin_only(current_user):
    return jsonify({"message": "Admin only access"})

@app.route('/user-or-admin')
@role_required(["user", "admin"])
def user_or_admin(current_user):
    return jsonify({"message": "User or admin access"})
```

### 權限基礎存取控制

```python
from jwt_auth_middleware import permission_required

@app.route('/delete-resource')
@permission_required("delete")
def delete_resource(current_user):
    return jsonify({"message": "Resource deleted"})

@app.route('/manage-users')
@permission_required(["read", "write"])
def manage_users(current_user):
    return jsonify({"message": "User management access"})
```

## 📋 完整範例

查看 `examples/` 目錄中的完整範例：

- `general_example.py` - 基本認證功能
- `refresh_token_example.py` - Token 重新整理功能
- `complete_example.py` - 包含所有功能的完整範例

## 🔍 故障排除

### 常見問題

1. **ImportError: No module named 'jwt_auth_middleware'**
   - 確保套件已正確安裝
   - 檢查 Python 環境

2. **ConfigurationError: JWT_SECRET_KEY not set**
   - 在 `app.config` 中設定 `JWT_SECRET_KEY`

3. **Token validation failed**
   - 檢查 token 格式是否正確
   - 確認 secret key 一致

### 除錯模式

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# 您的應用程式代碼...
```

## 📚 下一步

- 閱讀 [API 參考](api_reference.md) 了解所有可用功能
- 查看 [黑名單系統指南](blacklist_usage.md) 了解進階功能
- 探索 `examples/` 目錄中的完整範例
- 查看 [GitHub 專案](https://github.com/Hsieh-Yu-Hung/JWT_Midware) 獲取最新更新 