# JWT 認證中間件配置系統遷移指南

## 概述

本指南將幫助您從舊的環境變數配置方式遷移到新的分離式配置系統。

## 舊配置方式

在舊版本中，所有配置都存放在 `.env` 檔案中：

```bash
# 舊的 .env 檔案
JWT_SECRET_KEY=n{*lfHz.mQp?v<>7q3)[e%QcHr|??PY8U*XF6noDYfykG.nso1zBW{_*Y)KT);:C
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRES=120
JWT_REFRESH_TOKEN_EXPIRES=1440
MONGODB_API_URL=https://db-operation-xbbbehjawk.cn-shanghai-vpc.fcapp.run
JWT_BLACKLIST_COLLECTION=jwt_blacklist
JWT_ENABLE_BLACKLIST=true
```

## 新配置方式

新版本將配置分離為兩個部分：

### 1. 應用端密鑰管理

應用端負責提供 JWT_SECRET_KEY：

```python
# 從環境變數獲取密鑰（推薦做法）
import os
secret_key = os.getenv('JWT_SECRET_KEY')
if not secret_key:
    raise ValueError("請設定 JWT_SECRET_KEY 環境變數")

# 或者從其他安全來源獲取
secret_key = "your_super_secret_jwt_key_here"
```

### 2. 非敏感配置 (config.yaml)

存放其他配置：

```yaml
# 新的 config.yaml 檔案
jwt:
  algorithm: HS256
  access_token_expires: 120
  refresh_token_expires: 1440

mongodb:
  api_url: https://db-operation-xbbbehjawk.cn-shanghai-vpc.fcapp.run
  blacklist:
    collection: jwt_blacklist
    enabled: true

app:
  load_dotenv: true
  debug: false
```

## 遷移步驟

### 步驟 1：備份現有配置

```bash
# 備份現有的 .env 檔案
cp .env .env.backup
```

### 步驟 2：創建新的配置檔案

#### 2.1 應用端密鑰管理

應用端負責管理 JWT_SECRET_KEY，建議從環境變數獲取：

```python
# 從環境變數獲取密鑰
import os
secret_key = os.getenv('JWT_SECRET_KEY')
if not secret_key:
    raise ValueError("請設定 JWT_SECRET_KEY 環境變數")
```

#### 2.2 創建 config.yaml 檔案

在專案根目錄創建 `config.yaml` 檔案：

```yaml
# JWT 認證中間件配置檔案
jwt:
  algorithm: HS256
  access_token_expires: 120
  refresh_token_expires: 1440

mongodb:
  api_url: https://db-operation-xbbbehjawk.cn-shanghai-vpc.fcapp.run
  blacklist:
    collection: jwt_blacklist
    enabled: true

app:
  debug: false
```

### 步驟 3：更新 .gitignore

確保敏感配置被忽略，但 `config.yaml` 可以提交：

```gitignore
# 忽略敏感配置
.env
*.key
secrets/

# 允許提交非敏感配置
!config.yaml
```

### 步驟 4：更新程式碼（可選）

如果您在程式碼中直接使用環境變數，可以更新為使用新的配置系統：

#### 舊方式：
```python
import os
algorithm = os.getenv('JWT_ALGORITHM', 'HS256')
```

#### 新方式：
```python
from jwt_auth_middleware.config import JWTConfig, create_jwt_config
from jwt_auth_middleware import set_jwt_config

# 應用端提供密鑰
secret_key = os.getenv('JWT_SECRET_KEY')
config = JWTConfig(secret_key=secret_key)

# 設定全域配置
set_jwt_config(config)

# 使用配置
algorithm = config.algorithm
```

### 步驟 5：測試配置

運行測試確保配置正確：

```bash
# 測試新的配置系統
python -m pytest tests/test_new_config.py -v

# 測試整個套件
python -m pytest tests/ -v
```

## 配置優先順序

新配置系統的優先順序如下：

1. **直接傳入的參數**（最高優先級）
2. **環境變數**（僅用於敏感資訊）
3. **YAML 配置檔案**（用於非敏感配置）
4. **預設值**（最低優先級）

## 向後相容性

新版本保持向後相容性：

- 如果沒有 `config.yaml` 檔案，會使用預設值
- 環境變數仍然可以覆蓋 YAML 配置
- 舊的程式碼仍然可以正常工作

## 故障排除

### 問題 1：找不到配置檔案

**錯誤訊息**：`警告：未找到配置檔案，將使用預設值`

**解決方案**：
- 確認 `config.yaml` 檔案位於專案根目錄
- 檢查檔案名稱是否正確（支援 `.yaml` 和 `.yml` 副檔名）

### 問題 2：YAML 語法錯誤

**錯誤訊息**：`警告：無法載入配置檔案 config.yaml`

**解決方案**：
- 檢查 YAML 語法是否正確
- 使用 YAML 驗證工具檢查檔案
- 參考範例配置檔案

### 問題 3：缺少 JWT 密鑰

**錯誤訊息**：`JWT_SECRET_KEY 未設定`

**解決方案**：
- 確認 `.env` 檔案包含 `JWT_SECRET_KEY`
- 檢查 `.env` 檔案是否被正確載入
- 確認 `JWT_LOAD_DOTENV` 設定

### 問題 4：配置驗證失敗

**錯誤訊息**：`配置無效`

**解決方案**：
- 使用 `config.validate()` 檢查配置
- 確認所有必要欄位都有值
- 檢查數值是否在有效範圍內

## 範例配置檔案

### 開發環境 (config.dev.yaml)

```yaml
jwt:
  algorithm: HS256
  access_token_expires: 60
  refresh_token_expires: 720

mongodb:
  api_url: https://dev-mongodb-api.example.com
  blacklist:
    collection: jwt_blacklist_dev
    enabled: true

app:
  load_dotenv: true
  debug: true
```

### 生產環境 (config.prod.yaml)

```yaml
jwt:
  algorithm: HS512
  access_token_expires: 30
  refresh_token_expires: 1440

mongodb:
  api_url: https://prod-mongodb-api.example.com
  blacklist:
    collection: jwt_blacklist_prod
    enabled: true

app:
  load_dotenv: true
  debug: false
```

## 總結

新的配置系統提供了：

- ✅ **更好的安全性**：敏感資訊與非敏感資訊分離
- ✅ **更好的版本控制**：非敏感配置可以安全提交
- ✅ **更靈活的配置**：支援多環境配置
- ✅ **向後相容性**：舊程式碼仍然可以正常工作
- ✅ **更好的可維護性**：配置結構更清晰

如果您在遷移過程中遇到任何問題，請參考故障排除部分或提交 issue。 