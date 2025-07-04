# JWT 黑名單系統使用指南

## 概述

JWT 黑名單系統允許您撤銷已發行的 JWT tokens，即使它們尚未過期。這對於實現登出功能、處理安全事件或管理使用者會話非常有用。

## 功能特點

- 🔒 **安全撤銷**: 立即撤銷 JWT tokens
- 🗄️ **MongoDB 儲存**: 使用您的 MongoDB API 進行持久化儲存
- 🔐 **Token 雜湊**: 保護 token 隱私，只儲存雜湊值
- ⏰ **自動清理**: 自動清理已過期的黑名單項目
- 📊 **統計資訊**: 提供詳細的黑名單統計資料
- ⚙️ **可配置**: 可選擇啟用或停用黑名單功能

## 安裝與設定

### 1. 安裝依賴

```bash
pip install -r requirements.txt
```

### 2. 環境變數設定

```bash
# JWT 配置
export SECRET_KEY="your-super-secret-key"
export MONGODB_API_URL="http://your-mongodb-api-url.com"

# 可選配置
export JWT_ACCESS_TOKEN_EXPIRES=30
export JWT_REFRESH_TOKEN_EXPIRES=1440
```

### 3. 初始化黑名單系統

```python
from jwt_auth_middleware import initialize_blacklist_system, JWTConfig

# 方法 1: 使用環境變數
config = JWTConfig()
initialize_blacklist_system()

# 方法 2: 直接指定 URL
initialize_blacklist_system(
    mongodb_api_url="http://your-mongodb-api-url.com",
    collection_name="jwt_blacklist"
)
```

## 基本使用

### 建立和撤銷 Token

```python
from jwt_auth_middleware import (
    create_access_token,
    revoke_token,
    verify_token,
    is_token_blacklisted
)

# 建立 token
token_data = {"sub": "user123", "role": "admin"}
token = create_access_token(token_data)

# 撤銷 token
success = revoke_token(token, reason="user_logout")
print(f"Token 撤銷成功: {success}")

# 驗證 token（會自動檢查黑名單）
try:
    payload = verify_token(token)
    print("Token 有效")
except Exception as e:
    print(f"Token 無效: {e}")

# 檢查 token 是否在黑名單中
is_blacklisted = is_token_blacklisted(token)
print(f"Token 在黑名單中: {is_blacklisted}")
```

### Flask 應用程式整合

```python
from flask import Flask, request, jsonify
from jwt_auth_middleware import JWTConfig, token_required, create_access_token, revoke_token

app = Flask(__name__)

# 配置 JWT
jwt_config = JWTConfig(
    secret_key="your-secret-key",
    mongodb_api_url="http://your-mongodb-api-url.com",
    enable_blacklist=True
)

# 初始化黑名單系統
@app.before_first_request
def setup_blacklist():
    from jwt_auth_middleware import initialize_blacklist_system
    initialize_blacklist_system()

# 登入端點
@app.route('/login', methods=['POST'])
def login():
    # ... 驗證使用者憑證 ...
    token = create_access_token({"sub": "user123"})
    return jsonify({"access_token": token})

# 登出端點
@app.route('/logout', methods=['POST'])
@token_required
def logout(current_user):
    auth_header = request.headers.get('Authorization')
    if auth_header and auth_header.startswith('Bearer '):
        token = auth_header.split(' ')[1]
        revoke_token(token, reason="user_logout")
    return jsonify({"message": "Logged out successfully"})
```

## 進階功能

### 管理員功能

```python
from jwt_auth_middleware import (
    remove_from_blacklist,
    cleanup_expired_blacklist_tokens,
    get_blacklist_statistics
)

# 從黑名單中移除 token
success = remove_from_blacklist(token)
print(f"從黑名單移除成功: {success}")

# 清理過期的 tokens
cleaned_count = cleanup_expired_blacklist_tokens()
print(f"清理了 {cleaned_count} 個過期 tokens")

# 取得統計資訊
stats = get_blacklist_statistics()
print(f"總 tokens: {stats['total_tokens']}")
print(f"過期 tokens: {stats['expired_tokens']}")
print(f"活躍 tokens: {stats['active_tokens']}")
```

### 自定義黑名單管理器

```python
from jwt_auth_middleware import BlacklistManager, JWTConfig

# 建立自定義配置
config = JWTConfig(
    secret_key="your-secret-key",
    config_file="path/to/config.yaml"
)

# 建立黑名單管理器
blacklist_mgr = BlacklistManager(
    jwt_config=config,
    collection_name="custom_blacklist"  # 可選，預設使用配置中的值
)

# 使用管理器
blacklist_mgr.add_to_blacklist(token, "custom_reason")
is_blacklisted = blacklist_mgr.is_blacklisted(token)
```

## MongoDB API 需求

您的 MongoDB API 需要支援以下端點：

### 1. 插入文件 (`POST /insert`)

```json
{
  "collection": "jwt_blacklist",
  "document": {
    "token_hash": "sha256_hash_of_token",
    "reason": "revocation_reason",
    "revoked_at": "2024-01-01T00:00:00Z",
    "expires_at": "2024-01-01T00:30:00Z"
  }
}
```

### 2. 查詢文件 (`POST /find`)

```json
{
  "collection": "jwt_blacklist",
  "filter": {
    "token_hash": "sha256_hash_of_token"
  }
}
```

回應格式：
```json
{
  "documents": [
    {
      "token_hash": "sha256_hash_of_token",
      "reason": "revocation_reason",
      "revoked_at": "2024-01-01T00:00:00Z",
      "expires_at": "2024-01-01T00:30:00Z"
    }
  ]
}
```

### 3. 刪除文件 (`POST /delete`)

```json
{
  "collection": "jwt_blacklist",
  "filter": {
    "token_hash": "sha256_hash_of_token"
  }
}
```

回應格式：
```json
{
  "deleted_count": 1
}
```

### 4. 計數文件 (`POST /count`)

```json
{
  "collection": "jwt_blacklist",
  "filter": {
    "expires_at": {
      "$lt": "2024-01-01T00:00:00Z"
    }
  }
}
```

回應格式：
```json
{
  "count": 5
}
```

## 配置選項

### JWTConfig 參數

| 參數 | 類型 | 必要 | 說明 |
|------|------|------|------|
| `secret_key` | str | 是 | JWT 密鑰 |
| `config_file` | str | 是 | YAML 配置檔案路徑 |
| `algorithm` | str | 否 | JWT 演算法（可覆蓋配置檔案） |
| `access_token_expires` | int | 否 | Access token 過期時間（分鐘，可覆蓋配置檔案） |
| `refresh_token_expires` | int | 否 | Refresh token 過期時間（分鐘，可覆蓋配置檔案） |
| `blacklist_collection` | str | 否 | 黑名單集合名稱（可覆蓋配置檔案） |
| `enable_blacklist` | bool | 否 | 是否啟用黑名單功能（可覆蓋配置檔案） |

### 配置檔案結構

配置檔案必須包含以下結構：

```yaml
jwt:
  algorithm: HS256
  access_token_expires: 720
  refresh_token_expires: 1440

api:
  mode: internal  # 或 public

mongodb:
  internal_api_url: https://internal-api.example.com
  public_api_url: https://public-api.example.com
  blacklist:
    collection: jwt_blacklist
    enabled: true
```

系統會根據 `api.mode` 的值自動選擇對應的 MongoDB API URL。

## 安全考量

1. **Token 雜湊**: 系統只儲存 token 的 SHA256 雜湊值，保護原始 token
2. **過期清理**: 自動清理已過期的黑名單項目，減少儲存空間
3. **錯誤處理**: 完善的錯誤處理機制，避免系統崩潰
4. **配置驗證**: 驗證配置參數的有效性

## 故障排除

### 常見問題

1. **黑名單系統初始化失敗**
   - 檢查 MongoDB API URL 是否正確
   - 確認 API 端點是否可訪問
   - 檢查網路連線

2. **Token 撤銷失敗**
   - 確認黑名單功能已啟用
   - 檢查 MongoDB API 回應
   - 查看錯誤日誌

3. **驗證 token 時出現錯誤**
   - 確認 token 格式正確
   - 檢查 JWT 密鑰是否一致
   - 確認 token 未過期

### 除錯模式

```python
import logging

# 啟用詳細日誌
logging.basicConfig(level=logging.DEBUG)

# 測試黑名單功能
from jwt_auth_middleware import initialize_blacklist_system
success = initialize_blacklist_system()
print(f"初始化結果: {success}")
```

## 範例專案

完整的範例請參考 `examples/blacklist_example.py`，其中包含：

- 完整的 Flask 應用程式
- 登入/登出功能
- 管理員端點
- 測試端點
- 錯誤處理

## 測試

執行測試：

```bash
# 執行所有測試
pytest

# 執行黑名單相關測試
pytest tests/test_blacklist.py

# 執行測試並顯示覆蓋率
pytest --cov=jwt_auth_middleware
``` 