"""
測試配置示例

展示如何在測試環境中使用 JWT 配置系統，而不需要載入 .env 檔案
"""

from jwt_auth_middleware import JWTConfig, set_jwt_config, create_access_token, verify_token

def main():
    """主函數 - 展示測試配置的使用"""
    
    print("=== JWT 測試配置示例 ===")
    
    # 1. 創建測試配置（不需要 .env 檔案）
    test_config = JWTConfig(
        secret_key="test-secret-key-for-testing-only",
        algorithm="HS256",
        access_token_expires=30,  # 30 分鐘
        refresh_token_expires=1440,  # 24 小時
        mongodb_api_url="http://localhost:3001",
        blacklist_collection="jwt_blacklist_test",
        enable_blacklist=False  # 測試時通常不需要黑名單
    )
    
    print(f"✅ 測試配置創建成功")
    print(f"   - 演算法: {test_config.algorithm}")
    print(f"   - Access Token 過期時間: {test_config.access_token_expires} 分鐘")
    print(f"   - Refresh Token 過期時間: {test_config.refresh_token_expires} 分鐘")
    print(f"   - 黑名單功能: {'啟用' if test_config.enable_blacklist else '停用'}")
    
    # 2. 設置全域配置
    set_jwt_config(test_config)
    print("✅ 全域配置設置完成")
    
    # 3. 測試 token 創建和驗證
    test_user_data = {
        "sub": "test@example.com",
        "email": "test@example.com",
        "name": "測試用戶",
        "roles": ["user"]
    }
    
    # 創建 access token
    token = create_access_token(test_user_data)
    print(f"✅ Access Token 創建成功")
    print(f"   Token: {token[:50]}...")
    
    # 驗證 token
    try:
        payload = verify_token(token)
        print("✅ Token 驗證成功")
        print(f"   用戶: {payload['name']}")
        print(f"   郵箱: {payload['email']}")
        print(f"   角色: {payload['roles']}")
    except Exception as e:
        print(f"❌ Token 驗證失敗: {e}")
    
    # 4. 測試配置驗證
    if test_config.validate():
        print("✅ 配置驗證通過")
    else:
        print("❌ 配置驗證失敗")
    
    # 5. 顯示配置字典
    config_dict = test_config.to_dict()
    print("📋 配置摘要:")
    for key, value in config_dict.items():
        print(f"   {key}: {value}")

if __name__ == "__main__":
    main() 