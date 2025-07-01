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

### 方式一：從 GitHub 安裝（推薦）

```bash
# 安裝最新版本
pip install git+https://github.com/Hsieh-Yu-Hung/JWT_Midware.git

# 安裝特定版本
pip install git+https://github.com/Hsieh-Yu-Hung/JWT_Midware.git@v1.0.0

# 安裝開發版本
pip install git+https://github.com/Hsieh-Yu-Hung/JWT_Midware.git@develop
```

### 方式二：從本地安裝

```bash
# 在專案根目錄執行
pip install -e .
```

### 方式三：複製檔案到新專案

```bash
# 複製必要檔案
cp -r jwt_auth_middleware/ /path/to/your/project/
cp requirements.txt /path/to/your/project/
```

### 在 requirements.txt 中使用

```txt
# 安裝最新版本
git+https://github.com/Hsieh-Yu-Hung/JWT_Midware.git

# 安裝特定版本
git+https://github.com/Hsieh-Yu-Hung/JWT_Midware.git@v1.0.0

# 安裝開發版本
git+https://github.com/Hsieh-Yu-Hung/JWT_Midware.git@develop
```

### 本地開發安裝

如果您想要修改套件或進行開發：

```bash
# 克隆專案
git clone https://github.com/Hsieh-Yu-Hung/JWT_Midware.git
cd JWT_Midware

# 安裝開發依賴
pip install -e .
```

### 驗證安裝

安裝完成後，您可以在 Python 中測試：

```python
from jwt_auth_middleware import JWTManager, token_required, admin_required
print("JWT Auth Middleware 安裝成功！")
```

## 🔧 基本使用

### 1. 設定環境變數

```bash
export SECRET_KEY="your-super-secret-key-here"
```

### 2. 初始化 JWT Manager

```python
from flask import Flask
from jwt_auth_middleware import JWTManager

app = Flask(__name__)

# 配置
app.config['JWT_SECRET_KEY'] = 'your-secret-key'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(hours=1)

# 初始化 JWT Manager
jwt_manager = JWTManager(app)
```

### 3. 在 Flask 應用程式中使用

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
        "roles": user["roles"]
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

### 4. 手動驗證 Token

```python
from jwt_auth_middleware import verify_token

@app.route('/verify')
def verify_route():
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    try:
        user_data = verify_token(token)
        return {"valid": True, "user": user_data}
    except Exception as e:
        return {"valid": False, "error": str(e)}
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
    "roles": user["roles"],
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

## 🔄 從現有專案遷移

### 1. 更新 requirements.txt

```txt
# 移除舊的 JWT 相關依賴
# PyJWT==2.8.0  # 保留，因為套件會依賴它

# 添加新的套件
git+https://github.com/Hsieh-Yu-Hung/JWT_Midware.git
```

### 2. 更新 app.py

```python
# 舊的導入方式
# from middleware.jwt_middleware import token_required
# from core.jwt_utils import create_access_token, verify_token

# 新的導入方式
from jwt_auth_middleware import JWTManager, token_required, admin_required
from jwt_auth_middleware import create_access_token, verify_token

app = Flask(__name__)

# 配置 JWT
app.config['JWT_SECRET_KEY'] = 'your-secret-key'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(hours=1)

# 初始化
jwt_manager = JWTManager(app)

# 路由保持不變
@app.route('/protected')
@token_required
def protected(current_user):
    return {"message": "Hello", "user": current_user}
```

### 3. 更新路由文件

```python
# routes/auth_routes.py
from jwt_auth_middleware import create_access_token, verify_token

@auth_bp.route('/login', methods=['POST'])
def login():
    # ... 驗證邏輯 ...
  
    # 使用套件中的函數
    token = create_access_token(token_data)
    return jsonify({"access_token": token})
```

## 🗄️ MongoDB 整合

### 1. 配置資料庫

```python
app.config['MONGODB_URI'] = 'mongodb://localhost:27017/your_db'
app.config['MONGODB_DB_NAME'] = 'your_db_name'
```

### 2. 使用黑名單功能

```python
from jwt_auth_middleware import BlacklistManager

# 初始化黑名單管理器
blacklist_manager = BlacklistManager(app)

# 在登出時使用
@auth_bp.route('/logout', methods=['POST'])
def logout():
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    blacklist_manager.add_to_blacklist(token)
    return {"message": "Logged out successfully"}
```

## 🧪 測試

### 1. 運行套件測試

```bash
cd package/jwt_auth_middleware
pytest
```

### 2. 測試整合

```bash
# 在主專案中測試
python -c "
from jwt_auth_middleware import JWTManager
print('✅ 套件導入成功')
"
```

## 🔍 故障排除

### 常見問題

1. **ImportError: No module named 'jwt_auth_middleware'**

   - 確保套件已正確安裝：`pip list | grep jwt-auth-middleware`
2. **ConfigurationError: JWT_SECRET_KEY not set**

   - 確保在 app.config 中設定了 JWT_SECRET_KEY
3. **Token validation failed**

   - 檢查 token 格式是否正確
   - 確認 JWT_SECRET_KEY 與生成 token 時使用的相同

### 調試模式

```python
app.config['JWT_DEBUG'] = True  # 啟用詳細日誌
```

## 📚 更多資源

- [範例代碼](examples/)
- [GitHub 倉庫](https://github.com/Hsieh-Yu-Hung/JWT_Midware)
- [問題回報](https://github.com/Hsieh-Yu-Hung/JWT_Midware/issues)

## 📝 注意事項

- 此套件不再自動發布到 PyPI
- 所有版本都通過 GitHub Releases 管理
- 建議使用 GitHub 安裝方式以獲得最新功能和修復
