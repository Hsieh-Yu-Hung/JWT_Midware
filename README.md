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
pip install git+https://github.com/Hsieh-Yu-Hung/JWT_Midware.git@v1.0.0
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

# Refresh Token 端點
@app.route('/refresh', methods=['POST'])
@refresh_token_required
def refresh_token(current_user):
    new_token = create_access_token(current_user)
    return jsonify({"access_token": new_token})

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

## 🎯 裝飾器

| 裝飾器                          | 說明           | 範例                                    |
| ------------------------------- | -------------- | --------------------------------------- |
| `@token_required`             | 驗證 JWT token | `@token_required`                     |
| `@admin_required`             | 要求管理員權限 | `@admin_required`                     |
| `@role_required(roles)`       | 要求特定角色   | `@role_required(["admin", "user"])`   |
| `@permission_required(perms)` | 要求特定權限   | `@permission_required("delete_user")` |
| `@refresh_token_required`     | 驗證 Refresh token | `@refresh_token_required`           |

## ⚙️ 配置

### 環境變數

⚠️ **重要注意事項**：本套件會自動載入專案根目錄的 `.env` 檔案。請確保在專案根目錄建立 `.env` 檔案並設定以下必要的環境變數：

```bash
# 必要的環境變數
JWT_SECRET_KEY=your-super-secret-key-here
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRES=30
JWT_REFRESH_TOKEN_EXPIRES=1440
MONGODB_API_URL=https://your-mongodb-api-url.com
JWT_BLACKLIST_COLLECTION=jwt_blacklist
JWT_ENABLE_BLACKLIST=true
```

#### 環境變數說明

| 變數名稱 | 說明 | 預設值 | 是否必要 |
|---------|------|--------|----------|
| `JWT_SECRET_KEY` | JWT 簽名密鑰 | 無 | ✅ 必要 |
| `JWT_ALGORITHM` | JWT 演算法 | HS256 | ✅ 必要 |
| `JWT_ACCESS_TOKEN_EXPIRES` | Access token 過期時間（分鐘） | 30 | ✅ 必要 |
| `JWT_REFRESH_TOKEN_EXPIRES` | Refresh token 過期時間（分鐘） | 1440 | ✅ 必要 |
| `MONGODB_API_URL` | MongoDB API URL（用於黑名單功能） | 無 | ✅ 必要 |
| `JWT_BLACKLIST_COLLECTION` | 黑名單集合名稱 | jwt_blacklist | ✅ 必要 |
| `JWT_ENABLE_BLACKLIST` | 是否啟用黑名單功能 | true | ✅ 必要 |

#### 建立 .env 檔案

在專案根目錄建立 `.env` 檔案：

```bash
# 專案根目錄
touch .env  # Linux/macOS
# 或在 Windows 中手動建立 .env 檔案
```

然後在 `.env` 檔案中加入上述環境變數。

#### 故障排除

如果遇到 `ValueError: 環境變數 'XXX' 未設定。請檢查 .env 檔案是否正確配置。` 錯誤：

1. 確認 `.env` 檔案位於專案根目錄
2. 確認所有必要的環境變數都已設定
3. 確認 `.env` 檔案格式正確（無空格、正確的變數名稱）
4. 重新啟動應用程式或測試

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

- [快速開始指南](docs/quickstart.md) - 5 分鐘快速上手
- [API 參考](docs/api_reference.md) - 完整的 API 文檔
- [黑名單系統使用指南](docs/blacklist_usage.md) - 詳細的黑名單功能說明
- [完整範例](examples/complete_example.py) - 包含所有功能的完整應用程式範例
- [Refresh Token 範例](examples/refresh_token_example.py) - Token 重新整理功能範例
- [基本使用範例](examples/general_example.py) - 基本認證功能範例

## 🔗 相關連結

- [GitHub 專案](https://github.com/Hsieh-Yu-Hung/JWT_Midware)
- [問題回報](https://github.com/Hsieh-Yu-Hung/JWT_Midware/issues)
- [最新版本](https://github.com/Hsieh-Yu-Hung/JWT_Midware/releases)
