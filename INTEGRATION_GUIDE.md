# JWT Auth Middleware 整合指南

## 📦 安裝套件

### 從 PyPI 安裝（推薦）

```bash
pip install jwt-auth-middleware
```

### 從 GitHub 安裝

```bash
pip install git+https://github.com/yourusername/jwt-auth-middleware.git
```

### 本地開發安裝

```bash
# 在套件目錄中
pip install -e .
```

## 🔧 基本使用

### 1. 初始化 JWT Manager

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

### 2. 使用裝飾器保護路由

```python
from jwt_auth_middleware import token_required, admin_required

@app.route('/protected')
@token_required
def protected_route(current_user):
    return {"message": "This is protected", "user": current_user}

@app.route('/admin')
@admin_required
def admin_route(current_user):
    return {"message": "Admin only", "user": current_user}
```

### 3. 手動驗證 Token

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

## 🔄 從現有專案遷移

### 1. 更新 requirements.txt

```txt
# 移除舊的 JWT 相關依賴
# PyJWT==2.8.0  # 保留，因為套件會依賴它

# 添加新的套件
jwt-auth-middleware==1.0.0
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

- [完整 API 文檔](README.md)
- [範例代碼](examples/)
- [GitHub 倉庫](https://github.com/yourusername/jwt-auth-middleware)
- [問題回報](https://github.com/yourusername/jwt-auth-middleware/issues)
