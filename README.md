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
- ✅ MongoDB 黑名單系統

## 📋 系統需求

- Python 3.8 或更高版本
- Flask 3.0.0 或更高版本
- MongoDB API（用於黑名單功能）
- 網路連線（用於 MongoDB API 存取）

## 📦 安裝

```bash
# 安裝最新版本
pip install git+https://github.com/Hsieh-Yu-Hung/JWT_Midware.git

# 安裝特定版本
pip install git+https://github.com/Hsieh-Yu-Hung/JWT_Midware.git@v1.3.2
```

### 本地開發

```bash
# 克隆專案
git clone https://github.com/Hsieh-Yu-Hung/JWT_Midware.git
cd JWT_Midware

# 建立虛擬環境
python -m venv venv

# 進入虛擬環境 (Windows)
venv\Scripts\activate

# 進入虛擬環境 (Linux/Mac)
source venv/bin/activate

# 安裝開發依賴
pip install -r requirements.txt
pip install -e .
```

## 🔧 快速開始

### 1. 初始化

```python
from flask import Flask
from jwt_auth_middleware import JWTConfig, set_jwt_config

app = Flask(__name__)

# 創建 JWT 配置
secret_key = "your-super-secret-jwt-key-here"  # 實際應用中應從環境變數獲取
config = JWTConfig(secret_key=secret_key, config_file="config_example.yaml")

# 設定全域配置
set_jwt_config(config)
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

# 角色驗證端點
@app.route('/manager')
@role_required(['manager', 'admin'])
def manager_route(current_user):
    return jsonify({"message": "Manager access granted"})

# 權限驗證端點
@app.route('/delete-user')
@permission_required('delete_user')
def delete_user_route(current_user):
    return jsonify({"message": "User deletion access granted"})

# 登出端點（撤銷 token）
@app.route('/logout', methods=['POST'])
@token_required
def logout(current_user):
    from jwt_auth_middleware import revoke_token
    auth_header = request.headers.get('Authorization')
    if auth_header and auth_header.startswith('Bearer '):
        token = auth_header.split(' ')[1]
        revoke_token(token, reason="user_logout")
    return jsonify({"message": "Logged out successfully"})
```

## 🎯 裝飾器

| 裝飾器                          | 說明           | 範例                                    |
| ------------------------------- | -------------- | --------------------------------------- |
| `@token_required`             | 驗證 JWT token | `@token_required`                     |
| `@admin_required`             | 要求管理員權限 | `@admin_required`                     |
| `@role_required(roles)`       | 要求特定角色   | `@role_required(["admin", "user"])`   |
| `@permission_required(perms)` | 要求特定權限   | `@permission_required("delete_user")` |

## ⚙️ 配置

### 新的配置系統

本套件現在支援更靈活的配置管理，將敏感和非敏感配置分離：

- **敏感配置**：由應用端提供（如 JWT 密鑰）
- **非敏感配置**：存放在 `config.yaml` 檔案中（如演算法、過期時間等）

**重要**：應用端必須提供 JWT_SECRET_KEY，套件本身不預設任何密鑰。

### 配置檔案

#### 1. 應用端密鑰管理

⚠️ **重要**：應用端必須提供 JWT_SECRET_KEY，建議從環境變數獲取！

```python
# 從環境變數獲取密鑰（推薦做法）
import os
secret_key = os.getenv('JWT_SECRET_KEY')
if not secret_key:
    raise ValueError("請設定 JWT_SECRET_KEY 環境變數")

# 或者從其他安全來源獲取
secret_key = "your_super_secret_jwt_key_here"
```

#### 2. YAML 配置檔案 (config.yaml)

✅ **安全**：可以安全地提交到版本控制

```yaml
# JWT 認證中間件配置檔案
jwt:
  # JWT 演算法
  algorithm: HS256
  
  # Token 過期時間（分鐘）
  access_token_expires: 120
  refresh_token_expires: 1440

mongodb:
  # MongoDB API URL（用於黑名單功能）
  api_url: https://db-operation-xbbbehjawk.cn-shanghai-vpc.fcapp.run
  
  # 黑名單相關配置
  blacklist:
    collection: jwt_blacklist
    enabled: true

# 其他配置選項
app:
  # 是否載入 .env 檔案（預設為 true）
  load_dotenv: true
  
  # 除錯模式
  debug: false
```

### 配置載入優先順序

1. **直接傳入的參數**（最高優先級）
2. **YAML 配置檔案**（用於非敏感配置）
3. **預設值**（最低優先級）

**注意**：JWT_SECRET_KEY 必須由應用端提供，不會從環境變數自動載入。

### 使用方式

#### 基本使用

```python
from jwt_auth_middleware.config import JWTConfig, create_jwt_config
from jwt_auth_middleware import set_jwt_config

# 應用端提供密鑰
secret_key = "your_super_secret_jwt_key_here"

# 創建配置
config = JWTConfig(secret_key=secret_key, config_file="config_example.yaml")

# 設定全域配置（讓其他函數使用）
set_jwt_config(config)
```

#### 自訂配置檔案

```python
# 指定自訂配置檔案
config = JWTConfig(secret_key=secret_key, config_file="custom_config.yaml")
```

#### 程式化配置

```python
# 程式化設定配置（優先級最高）
config = JWTConfig(
    secret_key=secret_key,
    config_file="config_example.yaml",
    algorithm="HS512",
    access_token_expires=60,
    refresh_token_expires=720,
    mongodb_api_url="https://custom-mongodb-api.example.com",
    blacklist_collection="custom_blacklist",
    enable_blacklist=False
)
```

### 配置驗證

```python
# 驗證配置是否有效
if config.validate():
    print("配置有效")
else:
    print("配置無效")
```

### 故障排除

如果遇到配置錯誤：

1. 確認應用端提供了 `JWT_SECRET_KEY`
2. 確認 `config.yaml` 檔案格式正確
3. 檢查配置檔案的優先順序
4. 使用 `config.validate()` 驗證配置
5. 確認已使用 `set_jwt_config()` 設定全域配置

## 🧪 運行測試

```bash
# 使用 pytest
python -m pytest tests/ -v

# 執行特定測試
python -m pytest tests/test_blacklist.py -v
python -m pytest tests/test_refresh_token.py -v

# 執行測試並顯示覆蓋率
python -m pytest --cov=jwt_auth_middleware --cov-report=html

# 執行測試並生成覆蓋率報告
python -m pytest --cov=jwt_auth_middleware --cov-report=term-missing
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

本專案使用 Pull Request 合併到 main 分支時自動觸發 release 流程。

#### 標準工作流程

```bash
# 1. 建立功能分支
git checkout -b feature/new-feature

# 2. 進行開發和測試
# ... 開發工作 ...

# 3. 更新版本號（如果需要）
make bump-patch  # 或 bump-minor, bump-major

# 4. 提交更改
git add .
git commit -m "Add new feature and bump version"

# 5. 推送分支並建立 Pull Request
git push origin feature/new-feature
# 在 GitHub 上建立 PR 到 main 分支

# 6. 合併 Pull Request
# 當 PR 被合併到 main 分支時，GitHub Actions 會自動：
# - 構建套件
# - 創建 GitHub Release
# - 上傳構建檔案
```

#### 手動觸發（如果需要）

如果您需要手動觸發 release，可以：

```bash
# 1. 更新版本號
make bump-patch

# 2. 提交並推送
git add .
git commit -m "Bump version"
git push origin main

# 3. 建立標籤
git tag v1.0.1
git push origin v1.0.1
```

#### 自動化觸發條件

- ✅ **Pull Request 合併到 main 分支**：自動觸發 release
- ❌ **直接推送到 main 分支**：不會觸發 release
- ❌ **推送到其他分支**：不會觸發 release
- ❌ **關閉但未合併的 PR**：不會觸發 release

## 🔍 故障排除

### 常見問題

| 問題                                                   | 解決方案                                    |
| ------------------------------------------------------ | ------------------------------------------- |
| `ImportError: No module named 'jwt_auth_middleware'` | 確保套件已正確安裝：`pip list \| grep jwt` |
| `ConfigurationError: JWT_SECRET_KEY not set`         | 在 app.config 中設定 JWT_SECRET_KEY         |
| `Token validation failed`                            | 檢查 token 格式和 secret key                |

## 📝 注意事項

- Release 機制, 合併分支之前務必要更新版本號.
- 此套件不再自動發布到 PyPI
- 所有版本都通過 GitHub Releases 管理
- 建議使用 GitHub 安裝方式以獲得最新功能和修復

## 📚 更多文檔

- [完整範例](examples/complete_example.py) - 包含所有功能的完整應用程式範例
- [基本使用範例](examples/general_example.py) - 基本認證功能範例
- [配置範例](examples/config_example.py) - 配置系統使用範例
- [Flask 應用範例](examples/flask_app_example.py) - Flask 應用整合範例

## 🔗 相關連結

- [GitHub 專案](https://github.com/Hsieh-Yu-Hung/JWT_Midware)
- [問題回報](https://github.com/Hsieh-Yu-Hung/JWT_Midware/issues)
- [最新版本](https://github.com/Hsieh-Yu-Hung/JWT_Midware/releases)
