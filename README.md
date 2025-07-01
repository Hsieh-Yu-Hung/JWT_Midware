# JWT Auth Middleware

一個輕量級的 JWT 認證中間件，可以輕鬆整合到任何 Flask 應用程式中。

## 🚀 特色

- ✅ 簡單易用的裝飾器語法
- ✅ 支援角色基礎存取控制 (RBAC)
- ✅ 支援權限基礎存取控制 (PBAC)
- ✅ 可自定義配置
- ✅ 完整的 JWT token 管理
- ✅ 支援 token 重新整理
- ✅ 支援 token 撤銷

## 📦 安裝

### 方式一：從本地安裝

```bash
# 在專案根目錄執行
pip install -e .
```

### 方式二：複製檔案到新專案

```bash
# 複製必要檔案
cp -r jwt_auth_middleware/ /path/to/your/project/
cp requirements.txt /path/to/your/project/
```

## 🔧 基本使用

### 1. 設定環境變數

```bash
export SECRET_KEY="your-super-secret-key-here"
```

### 2. 在 Flask 應用程式中使用

```python
from flask import Flask, request, jsonify
from jwt_auth_middleware import (
    token_required, 
    admin_required, 
    role_required,
    create_access_token
)

app = Flask(__name__)

# 登入端點
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    # 驗證使用者邏輯...
  
    # 建立 JWT token
    token_data = {
        "sub": user["email"],
        "email": user["email"],
        "role": user["role"]
    }
    token = create_access_token(token_data)
  
    return jsonify({"access_token": token})

# 受保護的端點
@app.route('/protected', methods=['GET'])
@token_required
def protected_route(current_user):
    return jsonify({"user": current_user})

# 管理員專用端點
@app.route('/admin', methods=['GET'])
@admin_required
def admin_route(current_user):
    return jsonify({"message": "Admin access granted"})

# 特定角色端點
@app.route('/user-only', methods=['GET'])
@role_required("user")
def user_route(current_user):
    return jsonify({"message": "User access granted"})
```

## 🎯 裝飾器說明

### `@token_required`

驗證 JWT token 是否有效

```python
@app.route('/api/data', methods=['GET'])
@token_required
def get_data(current_user):
    # current_user 包含 token 中的使用者資訊
    return jsonify({"data": "some data"})
```

### `@admin_required`

要求管理員權限

```python
@app.route('/api/admin/users', methods=['GET'])
@admin_required
def get_users(current_user):
    # 只有管理員可以訪問
    return jsonify({"users": []})
```

### `@role_required(roles)`

要求特定角色

```python
# 單一角色
@app.route('/api/user/profile', methods=['GET'])
@role_required("user")
def user_profile(current_user):
    return jsonify({"profile": "user profile"})

# 多個角色
@app.route('/api/moderator/content', methods=['GET'])
@role_required(["admin", "moderator"])
def moderate_content(current_user):
    return jsonify({"content": "moderated content"})
```

### `@permission_required(permissions)`

要求特定權限

```python
@app.route('/api/delete/user', methods=['DELETE'])
@permission_required("delete_user")
def delete_user(current_user):
    return jsonify({"message": "User deleted"})
```

## ⚙️ 配置選項

### 自定義 JWT 配置

```python
from jwt_auth_middleware import JWTConfig

# 建立自定義配置
config = JWTConfig(
    secret_key="your-custom-secret",
    algorithm="HS256",
    access_token_expires=60,  # 60 分鐘
    refresh_token_expires=1440  # 24 小時
)

# 使用配置建立 token
token = create_access_token(data, config=config)
```

### 環境變數配置

```bash
# .env 檔案
SECRET_KEY=your-super-secret-key-here
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRES=30
JWT_REFRESH_TOKEN_EXPIRES=1440
```

## 🔐 Token 管理

### 建立 Token

```python
from jwt_auth_middleware import create_access_token

token_data = {
    "sub": user["id"],
    "email": user["email"],
    "role": user["role"],
    "permissions": user["permissions"]
}

token = create_access_token(token_data)
```

### 驗證 Token

```python
from jwt_auth_middleware import verify_token

try:
    payload = verify_token(token)
    print(f"User: {payload['email']}")
except Exception as e:
    print(f"Token invalid: {e}")
```

### 重新整理 Token

```python
from jwt_auth_middleware import refresh_token

new_token = refresh_token(old_token)
if new_token:
    print("Token refreshed successfully")
```

### 撤銷 Token

```python
from jwt_auth_middleware import revoke_token

success = revoke_token(token)
if success:
    print("Token revoked successfully")
```

## 📝 完整範例

參考 `examples/usage_example.py` 查看完整的使用範例。

### 測試 API

```bash
# 登入
curl -X POST https://jwt-autfunctions-ypvdbtxjmv.cn-shanghai-vpc.fcapp.run/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@example.com", "password": "admin123"}'

# 使用 token 訪問受保護的端點
curl -X GET https://jwt-autfunctions-ypvdbtxjmv.cn-shanghai-vpc.fcapp.run/protected \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"

# 訪問管理員端點
curl -X GET https://jwt-autfunctions-ypvdbtxjmv.cn-shanghai-vpc.fcapp.run/admin/stats \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

## 🚀 部署到 Function Compute

這個中間件完全相容於阿里雲 Function Compute：

```python
# function_compute_adapter.py
from flask import Flask
from jwt_auth_middleware import token_required

app = Flask(__name__)

@app.route('/protected', methods=['GET'])
@token_required
def protected_route(current_user):
    return jsonify({"user": current_user})

def handler(event, context):
    # Function Compute 處理邏輯...
    pass
```

## 🔧 自定義擴展

### 自定義驗證邏輯

```python
from functools import wraps
from flask import request, jsonify
from jwt_auth_middleware import verify_token

def custom_auth_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        # 自定義驗證邏輯
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
      
        if not token:
            return jsonify({'message': 'Custom auth required'}), 403
      
        try:
            current_user = verify_token(token)
            # 額外的驗證邏輯...
          
        except Exception as e:
            return jsonify({'message': str(e)}), 403
      
        return f(current_user, *args, **kwargs)
    return decorated
```

## 📚 API 參考

### 裝飾器

- `token_required(f)` - 驗證 JWT token
- `admin_required(f)` - 要求管理員權限
- `role_required(roles)` - 要求特定角色
- `permission_required(permissions)` - 要求特定權限

### 函數

- `create_access_token(data, config=None)` - 建立 JWT token
- `verify_token(token)` - 驗證 JWT token
- `revoke_token(token)` - 撤銷 JWT token
- `refresh_token(token)` - 重新整理 JWT token
- `get_token_expiration(token)` - 取得 token 過期時間
- `is_token_expired(token)` - 檢查 token 是否過期

### 類別

- `JWTConfig` - JWT 配置類別

## 🤝 貢獻

歡迎提交 Issue 和 Pull Request！

## 📄 授權

MIT License

---

這個中間件讓你可以輕鬆地在任何 Flask 專案中實作 JWT 認證，無需重複造輪子！
