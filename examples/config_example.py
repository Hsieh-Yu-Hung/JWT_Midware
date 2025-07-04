#!/usr/bin/env python3
"""
JWT 認證中間件配置使用範例

此範例展示如何使用新的配置系統：
1. 應用端必須提供 JWT_SECRET_KEY
2. 從 YAML 檔案載入非敏感配置
3. 程式化設定配置
"""

import os
from jwt_auth_middleware.config import JWTConfig, create_jwt_config
from jwt_auth_middleware import set_jwt_config

def example_basic_usage():
    """基本使用範例"""
    print("=== 基本使用範例 ===")
    
    # 應用端必須提供 JWT_SECRET_KEY
    secret_key = "your_super_secret_jwt_key_here"  # 實際應用中應該從環境變數或安全來源獲取
    
    # 使用預設配置（自動載入 config.yaml）
    config = JWTConfig(secret_key=secret_key, config_file="../jwt_auth_middleware/config_example.yaml")
    
    print(f"演算法: {config.algorithm}")
    print(f"Access Token 過期時間: {config.access_token_expires} 分鐘")
    print(f"Refresh Token 過期時間: {config.refresh_token_expires} 分鐘")
    print(f"MongoDB URL: {config.mongodb_api_url}")
    print(f"黑名單集合: {config.blacklist_collection}")
    print(f"啟用黑名單: {config.enable_blacklist}")
    print(f"配置有效: {config.validate()}")
    print()

def example_custom_config_file():
    """自訂配置檔案範例"""
    print("=== 自訂配置檔案範例 ===")
    
    # 應用端提供 JWT_SECRET_KEY
    secret_key = "your_super_secret_jwt_key_here"
    
    # 指定自訂配置檔案
    config = JWTConfig(secret_key=secret_key, config_file="../jwt_auth_middleware/config_example.yaml")
    
    print(f"使用自訂配置檔案: {config}")
    print()

def example_programmatic_config():
    """程式化配置範例"""
    print("=== 程式化配置範例 ===")
    
    # 應用端提供 JWT_SECRET_KEY
    secret_key = "your_super_secret_jwt_key_here"
    
    # 程式化設定配置（優先級最高）
    config = JWTConfig(
        secret_key=secret_key,
        config_file="../jwt_auth_middleware/config_example.yaml"
    )
    
    print(f"程式化配置: {config}")
    print()

def example_factory_function():
    """使用工廠函數範例"""
    print("=== 工廠函數範例 ===")
    
    # 應用端提供 JWT_SECRET_KEY
    secret_key = "your_super_secret_jwt_key_here"
    
    # 使用工廠函數創建配置
    config = create_jwt_config(
        secret_key=secret_key,
        config_file="../jwt_auth_middleware/config_example.yaml"
    )
    
    print(f"工廠函數配置: {config}")
    print()

def example_environment_secret_key():
    """從環境變數獲取密鑰範例"""
    print("=== 環境變數密鑰範例 ===")
    
    # 從環境變數獲取密鑰（推薦做法）
    secret_key = os.getenv('JWT_SECRET_KEY')
    if not secret_key:
        print("警告：請設定 JWT_SECRET_KEY 環境變數")
        print("例如：export JWT_SECRET_KEY='your_secret_key'")
        secret_key = "fallback_secret_key"  # 僅用於範例
    
    config = JWTConfig(secret_key=secret_key, config_file="../jwt_auth_middleware/config_example.yaml")
    print(f"環境變數配置: {config}")
    print()

def example_initialize_system():
    """初始化系統範例"""
    print("=== 初始化系統範例 ===")
    
    # 1. 創建配置
    secret_key = "your_super_secret_jwt_key_here"
    config = JWTConfig(secret_key=secret_key, config_file="../jwt_auth_middleware/config_example.yaml")
    
    # 2. 設定全域配置（讓其他函數使用）
    set_jwt_config(config)
    
    print("系統已初始化，其他函數現在可以使用此配置")
    print()

def example_config_validation():
    """配置驗證範例"""
    print("=== 配置驗證範例 ===")
    
    # 測試有效配置
    valid_config = JWTConfig(
        secret_key="valid_secret_key",
        config_file="../jwt_auth_middleware/config_example.yaml"
    )
    print(f"有效配置驗證: {valid_config.validate()}")
    
    # 測試無效配置
    try:
        invalid_config = JWTConfig(
            secret_key="",  # 空密鑰
            config_file="../jwt_auth_middleware/config_example.yaml"
        )
        print(f"無效配置驗證: {invalid_config.validate()}")
    except ValueError as e:
        print(f"配置錯誤: {e}")
    
    print()

def example_missing_secret_key():
    """缺少密鑰範例"""
    print("=== 缺少密鑰範例 ===")
    
    try:
        # 嘗試創建沒有密鑰的配置
        config = JWTConfig(secret_key="", config_file="../jwt_auth_middleware/config_example.yaml")
        print("這不應該執行")
    except ValueError as e:
        print(f"正確捕獲錯誤: {e}")
    
    print()

if __name__ == "__main__":
    print("JWT 認證中間件配置系統範例")
    print("=" * 50)
    
    example_basic_usage()
    example_custom_config_file()
    example_programmatic_config()
    example_factory_function()
    example_environment_secret_key()
    example_initialize_system()
    example_config_validation()
    example_missing_secret_key()
    
    print("配置範例完成！")
    print("\n重要提醒：")
    print("1. 應用端必須提供 JWT_SECRET_KEY")
    print("2. 密鑰應該從安全的來源獲取（如環境變數）")
    print("3. 使用 set_jwt_config() 設定全域配置")
    print("4. 配置檔案可以安全地提交到版本控制") 