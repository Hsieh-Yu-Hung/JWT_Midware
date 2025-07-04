# JWT Auth Middleware API 參考

## 核心類別

### JWTConfig

JWT 配置類別，用於設定 JWT 相關參數。

```python
from jwt_auth_middleware import JWTConfig

config = JWTConfig(
    secret_key="your-secret-key",
    algorithm="HS256",
    access_token_expires=30,
    refresh_token_expires=1440,
    mongodb_api_url="http://your-mongodb-api.com",
    blacklist_collection="jwt_blacklist",
    enable_blacklist=True
)
```

#### 參數

| 參數 | 類型 | 預設值 | 說明 |
|------|------|--------|------|
| `secret_key` | str | 環境變數 `SECRET_KEY` | JWT 簽名密鑰 |
| `algorithm` | str | "HS256" | JWT 演算法 |
| `access_token_expires` | int | 30 | Access token 過期時間（分鐘） |
| `refresh_token_expires` | int | 1440 | Refresh token 過期時間（分鐘） |
| `mongodb_api_url` | str | 環境變數 `MONGODB_API_URL` | MongoDB API URL |
| `blacklist_collection` | str | "jwt_blacklist" | 黑名單集合名稱 |
| `enable_blacklist` | bool | True | 是否啟用黑名單功能 |

### JWTManager

JWT 管理器，用於初始化和管理 JWT 功能。

```python
from jwt_auth_middleware import JWTManager

app = Flask(__name__)
jwt_manager = JWTManager(app)
```

## 裝飾器

### @token_required

驗證 JWT access token 的裝飾器。

```python
from jwt_auth_middleware import token_required

@app.route('/protected')
@token_required
def protected_route(current_user):
    return jsonify({"user": current_user})
```

### @refresh_token_required

驗證 JWT refresh token 的裝飾器。

```python
from jwt_auth_middleware import refresh_token_required

@app.route('/refresh', methods=['POST'])
@refresh_token_required
def refresh_token(current_user):
    new_token = create_access_token(current_user)
    return jsonify({"access_token": new_token})
```

### @admin_required

要求管理員權限的裝飾器。

```python
from jwt_auth_middleware import admin_required

@app.route('/admin')
@admin_required
def admin_route(current_user):
    return jsonify({"message": "Admin access granted"})
```

### @role_required(roles)

要求特定角色的裝飾器。

```python
from jwt_auth_middleware import role_required

@app.route('/user-only')
@role_required(["user"])
def user_only_route(current_user):
    return jsonify({"message": "User access granted"})

@app.route('/admin-or-user')
@role_required(["admin", "user"])
def admin_or_user_route(current_user):
    return jsonify({"message": "Access granted"})
```

### @permission_required(permissions)

要求特定權限的裝飾器。

```python
from jwt_auth_middleware import permission_required

@app.route('/delete-user')
@permission_required("delete_user")
def delete_user_route(current_user):
    return jsonify({"message": "User deletion allowed"})

@app.route('/manage-users')
@permission_required(["create_user", "update_user"])
def manage_users_route(current_user):
    return jsonify({"message": "User management allowed"})
```

## Token 管理函數

### Token 結構

JWT token 包含以下標準欄位：

| 欄位 | 類型 | 說明 |
|------|------|------|
| `exp` | datetime | Token 過期時間 |
| `iat` | datetime | Token 發行時間 |
| `type` | str | Token 類型（"access" 或 "refresh"） |
| `jti` | str | JWT ID，確保每個 token 的唯一性 |

### create_access_token(payload)

建立 JWT access token。

```python
from jwt_auth_middleware import create_access_token

token_data = {
    "sub": "user123",
    "email": "user@example.com",
    "roles": ["user"],
    "permissions": ["read", "write"]
}
token = create_access_token(token_data)
```

### create_refresh_token(payload)

建立 JWT refresh token。

```python
from jwt_auth_middleware import create_refresh_token

refresh_token = create_refresh_token(token_data)
```

### verify_token(token)

驗證 JWT token。

```python
from jwt_auth_middleware import verify_token

try:
    payload = verify_token(token)
    print("Token 有效:", payload)
except Exception as e:
    print("Token 無效:", e)
```

### verify_refresh_token(token)

驗證 JWT refresh token。

```python
from jwt_auth_middleware import verify_refresh_token

try:
    payload = verify_refresh_token(token)
    print("Refresh token 有效:", payload)
except Exception as e:
    print("Refresh token 無效:", e)
```

## 黑名單管理函數

### initialize_blacklist_system()

初始化黑名單系統。

```python
from jwt_auth_middleware import initialize_blacklist_system

success = initialize_blacklist_system()
if success:
    print("黑名單系統初始化成功")
else:
    print("黑名單系統初始化失敗")
```

### revoke_token(token, reason="")

將 token 加入黑名單。

```python
from jwt_auth_middleware import revoke_token

success = revoke_token(token, reason="user_logout")
if success:
    print("Token 已撤銷")
else:
    print("Token 撤銷失敗")
```

### is_token_blacklisted(token)

檢查 token 是否在黑名單中。

```python
from jwt_auth_middleware import is_token_blacklisted

is_blacklisted = is_token_blacklisted(token)
if is_blacklisted:
    print("Token 在黑名單中")
else:
    print("Token 不在黑名單中")
```

### remove_from_blacklist(token)

從黑名單中移除 token。

```python
from jwt_auth_middleware import remove_from_blacklist

success = remove_from_blacklist(token)
if success:
    print("Token 已從黑名單移除")
else:
    print("移除失敗")
```

### cleanup_expired_blacklist_tokens()

清理過期的黑名單 tokens。

```python
from jwt_auth_middleware import cleanup_expired_blacklist_tokens

cleaned_count = cleanup_expired_blacklist_tokens()
print(f"清理了 {cleaned_count} 個過期 tokens")
```

### get_blacklist_statistics()

取得黑名單統計資訊。

```python
from jwt_auth_middleware import get_blacklist_statistics

stats = get_blacklist_statistics()
print(f"總 tokens: {stats['total_tokens']}")
print(f"過期 tokens: {stats['expired_tokens']}")
print(f"活躍 tokens: {stats['active_tokens']}")
```

## 黑名單管理器

### BlacklistManager

自定義黑名單管理器。

```python
from jwt_auth_middleware import BlacklistManager, JWTConfig

config = JWTConfig(
    secret_key="your-secret-key",
    mongodb_api_url="http://your-api.com"
)

blacklist_mgr = BlacklistManager(
    mongodb_api_url="http://your-api.com",
    collection_name="custom_blacklist",
    jwt_config=config
)

# 使用管理器
blacklist_mgr.add_to_blacklist(token, "custom_reason")
is_blacklisted = blacklist_mgr.is_blacklisted(token)
```

#### 方法

- `add_to_blacklist(token, reason)`: 將 token 加入黑名單
- `is_blacklisted(token)`: 檢查 token 是否在黑名單中
- `remove_from_blacklist(token)`: 從黑名單中移除 token
- `cleanup_expired_tokens()`: 清理過期 tokens
- `get_statistics()`: 取得統計資訊

## 錯誤處理

### 自定義異常

```python
from jwt_auth_middleware import (
    JWTError,
    TokenExpiredError,
    TokenInvalidError,
    ConfigurationError
)

try:
    payload = verify_token(token)
except TokenExpiredError:
    print("Token 已過期")
except TokenInvalidError:
    print("Token 無效")
except ConfigurationError:
    print("配置錯誤")
except JWTError as e:
    print(f"JWT 錯誤: {e}")
```

## 配置範例

### 基本配置

```python
from flask import Flask
from jwt_auth_middleware import JWTManager

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'your-secret-key'
app.config['JWT_ALGORITHM'] = 'HS256'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 30
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = 1440

jwt_manager = JWTManager(app)
```

### 進階配置

```python
from flask import Flask
from jwt_auth_middleware import JWTManager, JWTConfig

app = Flask(__name__)

config = JWTConfig(
    secret_key="your-super-secret-key",
    algorithm="HS256",
    access_token_expires=60,
    refresh_token_expires=1440,
    mongodb_api_url="http://your-mongodb-api.com",
    blacklist_collection="jwt_blacklist",
    enable_blacklist=True
)

jwt_manager = JWTManager(app, config=config)
```

### 環境變數配置

```bash
# .env 檔案
SECRET_KEY=your-super-secret-key
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRES=30
JWT_REFRESH_TOKEN_EXPIRES=1440
MONGODB_API_URL=http://your-mongodb-api.com
```

```python
from flask import Flask
from jwt_auth_middleware import JWTManager
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
jwt_manager = JWTManager(app)
``` 