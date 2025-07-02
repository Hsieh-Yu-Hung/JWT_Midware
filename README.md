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

### 從 GitHub 安裝（推薦）

```bash
# 安裝最新版本
pip install git+https://github.com/Hsieh-Yu-Hung/JWT_Midware.git

# 安裝特定版本
pip install git+https://github.com/Hsieh-Yu-Hung/JWT_Midware.git@v1.0.0
```

### 本地開發

```bash
# 克隆專案
git clone https://github.com/Hsieh-Yu-Hung/JWT_Midware.git
cd JWT_Midware

# 安裝開發依賴
pip install -e .
```

## 🔧 快速開始

### 1. 初始化

```python
from flask import Flask
from jwt_auth_middleware import JWTManager

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'your-secret-key'
jwt_manager = JWTManager(app)
```

### 2. 使用裝飾器

```python
from jwt_auth_middleware import token_required, admin_required, create_access_token

# 登入端點
@app.route('/login', methods=['POST'])
def login():
    # 驗證使用者邏輯...
    token_data = {
        "sub": user["email"],
        "email": user["email"],
        "roles": user["roles"]
    }
    token = create_access_token(token_data)
    return jsonify({"access_token": token})

# 受保護的端點
@app.route('/protected')
@token_required
def protected_route(current_user):
    return jsonify({"user": current_user})

# 管理員端點
@app.route('/admin')
@admin_required
def admin_route(current_user):
    return jsonify({"message": "Admin access granted"})
```

## 🎯 裝飾器

| 裝飾器                          | 說明           | 範例                                    |
| ------------------------------- | -------------- | --------------------------------------- |
| `@token_required`             | 驗證 JWT token | `@token_required`                     |
| `@admin_required`             | 要求管理員權限 | `@admin_required`                     |
| `@role_required(roles)`       | 要求特定角色   | `@role_required(["admin", "user"])`   |
| `@permission_required(perms)` | 要求特定權限   | `@permission_required("delete_user")` |

## ⚙️ 配置

### 環境變數

```bash
SECRET_KEY=your-super-secret-key-here
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRES=30
JWT_REFRESH_TOKEN_EXPIRES=1440
```

### 自定義配置

```python
from jwt_auth_middleware import JWTConfig

config = JWTConfig(
    secret_key="your-custom-secret",
    algorithm="HS256",
    access_token_expires=60,
    refresh_token_expires=1440
)
```

## 🔄 從現有專案遷移

### 1. 更新 requirements.txt

```txt
git+https://github.com/Hsieh-Yu-Hung/JWT_Midware.git
```

### 2. 更新導入

```python
from jwt_auth_middleware import JWTManager, token_required, admin_required
```

## 🗄️ MongoDB 整合

```python
# 配置資料庫
app.config['MONGODB_URI'] = 'mongodb://localhost:27017/your_db'

# 使用黑名單功能
from jwt_auth_middleware import BlacklistManager
blacklist_manager = BlacklistManager(app)

@app.route('/logout', methods=['POST'])
def logout():
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    blacklist_manager.add_to_blacklist(token)
    return {"message": "Logged out successfully"}
```

## 🧪 測試

```bash
# 使用 pytest
python -m pytest tests/ -v
```

## 📋 版本管理

### 自動化版本更新

#### Linux/macOS

```bash
# 顯示所有命令
make help

# 更新 patch 版本 (1.0.0 -> 1.0.1)
make bump-patch

# 更新 minor 版本 (1.0.0 -> 1.1.0)
make bump-minor

# 更新 major 版本 (1.0.0 -> 2.0.0)
make bump-major

# 互動式 release
make release
```

#### Windows (Git Bash)

```bash
# 顯示所有命令
bash make.sh help

# 更新 patch 版本 (1.0.0 -> 1.0.1)
bash make.sh bump-patch

# 更新 minor 版本 (1.0.0 -> 1.1.0)
bash make.sh bump-minor

# 更新 major 版本 (1.0.0 -> 2.0.0)
bash make.sh bump-major

# 互動式 release
bash make.sh release
```

### 手動版本更新

```bash
# 使用 Python 腳本
python scripts/bump_version.py patch
```

### 創建 Release

```bash
# 1. 更新版本號
make bump-patch

# 2. 提交更改
git add .
git commit -m "Bump version"
git push origin main

# 3. 創建標籤
git tag v1.0.1
git push origin v1.0.1
```

推送標籤後，GitHub Actions 會自動：

- 構建套件
- 創建 GitHub Release
- 上傳構建檔案

## 🔍 故障排除

### 常見問題

| 問題                                                   | 解決方案                                    |
| ------------------------------------------------------ | ------------------------------------------- |
| `ImportError: No module named 'jwt_auth_middleware'` | 確保套件已正確安裝：`pip list \| grep jwt` |
| `ConfigurationError: JWT_SECRET_KEY not set`         | 在 app.config 中設定 JWT_SECRET_KEY         |
| `Token validation failed`                            | 檢查 token 格式和 secret key                |

## 📝 注意事項

- 此套件不再自動發布到 PyPI
- 所有版本都通過 GitHub Releases 管理
- 建議使用 GitHub 安裝方式以獲得最新功能和修復
