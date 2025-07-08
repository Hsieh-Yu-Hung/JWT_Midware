# JWT Auth Middleware

一個輕量級的 JWT 認證中間件，可以輕鬆整合到任何 Flask 應用程式中。

## 🚀 特色

- ✅ 簡單易用的裝飾器語法
- ✅ 支援角色基礎存取控制 (RBAC)
- ✅ 支援權限基礎存取控制 (PBAC)
- ✅ 可自定義配置
- ✅ 完整的 JWT token 驗證
- ✅ MongoDB 黑名單系統
- ✅ 支援內網/公網 API 模式
- ✅ 嚴格的配置驗證

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
pip install git+https://github.com/Hsieh-Yu-Hung/JWT_Midware.git@v2.0.0
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
from jwt_auth_middleware import token_required, admin_required, role_required, permission_required

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
```

## 🎯 裝飾器

| 裝飾器                          | 說明           | 範例                                    |
| ------------------------------- | -------------- | --------------------------------------- |
| `@token_required`             | 驗證 JWT token | `@token_required`                     |
| `@admin_required`             | 要求管理員權限 | `@admin_required`                     |
| `@role_required(roles)`       | 要求特定角色   | `@role_required(["admin", "user"])`   |
| `@permission_required(perms)` | 要求特定權限   | `@permission_required("delete_user")` |

## ⚙️ 配置

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
  access_token_expires: 720  # 12 小時
  refresh_token_expires: 1440  # 24 小時

# API 模式配置
api:
  # API 模式選擇 (internal 或 public)
  mode: internal  # 可選值: internal, public

mongodb:
  # MongoDB API URL（用於黑名單功能）內網API
  internal_api_url: https://db-operation-xbbbehjawk.cn-shanghai-vpc.fcapp.run
  # MongoDB API URL（用於黑名單功能）公網API
  public_api_url: https://db-operation-xbbbehjawk.cn-shanghai.fcapp.run
  
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

1. **YAML 配置檔案**（主要配置來源）
2. **預設值**（備用）

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
3. 檢查配置檔案的結構
4. 使用 `config.validate()` 驗證配置
5. 確認已使用 `set_jwt_config()` 設定全域配置

## 🔄 版本 2.0.0 重要變更

### 架構重構

- **業務邏輯分離**：Token 創建、刷新等業務邏輯函數已移至主專案
- **專注中間件**：本套件現在專注於 JWT 驗證和存取控制
- **簡化 API**：移除了 `create_access_token`、`refresh_access_token` 等函數

### 新功能

- **API 模式支援**：支援內網（internal）和公網（public）API 模式
- **嚴格配置驗證**：更完善的配置檔案結構驗證
- **改進錯誤處理**：更清晰的錯誤訊息和異常處理

### 配置變更

- **必要參數**：`secret_key` 和 `config_file` 現在都是必要參數
- **API 模式**：新增 `api.mode` 配置，自動選擇對應的 MongoDB API URL
- **結構驗證**：配置檔案必須包含所有必要區段和欄位

### 遷移指南

從 v1.x 升級到 v2.0.0：

1. **更新配置檔案**：確保包含 `api.mode` 和對應的 API URL
2. **移除業務邏輯**：將 token 創建邏輯移至主專案
3. **更新導入**：移除不再提供的函數導入
4. **測試驗證**：確保所有端點正常工作

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

# 更新 patch 版本 (2.0.0 -> 2.0.1)
make bump-patch

# 更新 minor 版本 (2.0.0 -> 2.1.0)
make bump-minor

# 更新 major 版本 (2.0.0 -> 3.0.0)
make bump-major

# 互動式 release
make release
```

#### Windows (Git Bash)

```bash
# 顯示所有命令
bash make.sh help

# 更新 patch 版本 (2.0.0 -> 2.0.1)
bash make.sh bump-patch

# 更新 minor 版本 (2.0.0 -> 2.1.0)
bash make.sh bump-minor

# 更新 major 版本 (2.0.0 -> 3.0.0)
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
git tag v2.0.1
git push origin v2.0.1
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
| `ValueError: JWT_SECRET_KEY 是必要參數`              | 在創建 JWTConfig 時提供 secret_key 參數     |
| `FileNotFoundError: 配置檔案不存在`                  | 確認配置檔案路徑正確                        |
| `ValueError: 無效的 API 模式`                        | 確認 api.mode 設定為 internal 或 public     |
| `Token validation failed`                            | 檢查 token 格式和 secret key                |

## 📝 注意事項

- Release 機制, 合併分支之前務必要更新版本號.
- 此套件不再自動發布到 PyPI
- 所有版本都通過 GitHub Releases 管理
- 建議使用 GitHub 安裝方式以獲得最新功能和修復
- **v2.0.0 重構**：業務邏輯函數已移至主專案，本套件專注於中間件功能
