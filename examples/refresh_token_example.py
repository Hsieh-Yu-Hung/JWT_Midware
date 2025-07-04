#!/usr/bin/env python3
"""
Refresh Token 機制使用範例

展示如何使用 Refresh Token 功能
"""

import os
import sys
from datetime import datetime

# 添加專案路徑
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from jwt_auth_middleware import (
    JWTConfig,
    create_token_pair,
    verify_access_token,
    verify_refresh_token,
    refresh_access_token,
    revoke_token_pair,
    is_token_blacklisted
)

def print_separator(title):
    """印出分隔線"""
    print("\n" + "="*50)
    print(f" {title}")
    print("="*50)

def demo_refresh_token():
    """演示 Refresh Token 功能"""
    print_separator("Refresh Token 功能演示")
    
    # 建立測試配置
    config = JWTConfig(
        secret_key="demo-secret-key",
        access_token_expires=30,      # 30分鐘
        refresh_token_expires=1440,   # 24小時
        mongodb_api_url="http://localhost:3000",
        enable_blacklist=True
    )
    
    print("1. 建立 Access Token 和 Refresh Token 對...")
    token_data = {
        "sub": "demo_user",
        "role": "user",
        "created_at": datetime.now().isoformat()
    }
    
    tokens = create_token_pair(token_data)
    access_token = tokens["access_token"]
    refresh_token = tokens["refresh_token"]
    
    print(f"   Access Token: {access_token[:50]}...")
    print(f"   Refresh Token: {refresh_token[:50]}...")
    
    print("\n2. 驗證 Access Token...")
    try:
        payload = verify_access_token(access_token)
        print(f"   Access Token 有效，使用者: {payload['sub']}")
    except Exception as e:
        print(f"   Access Token 驗證失敗: {e}")
    
    print("\n3. 驗證 Refresh Token...")
    try:
        payload = verify_refresh_token(refresh_token)
        print(f"   Refresh Token 有效，使用者: {payload['sub']}")
    except Exception as e:
        print(f"   Refresh Token 驗證失敗: {e}")
    
    print("\n4. 使用 Refresh Token 取得新的 Access Token...")
    new_access_token = refresh_access_token(refresh_token)
    if new_access_token:
        print(f"   新的 Access Token: {new_access_token[:50]}...")
        
        # 驗證新的 Access Token
        try:
            payload = verify_access_token(new_access_token)
            print(f"   新的 Access Token 有效，使用者: {payload['sub']}")
        except Exception as e:
            print(f"   新的 Access Token 驗證失敗: {e}")
    else:
        print("   無法取得新的 Access Token")
    
    print("\n5. 撤銷 Token 對...")
    success = revoke_token_pair(access_token, refresh_token, "demo_logout")
    print(f"   Token 對撤銷成功: {success}")
    
    print("\n6. 檢查 Token 是否在黑名單中...")
    access_blacklisted = is_token_blacklisted(access_token)
    refresh_blacklisted = is_token_blacklisted(refresh_token)
    print(f"   Access Token 在黑名單中: {access_blacklisted}")
    print(f"   Refresh Token 在黑名單中: {refresh_blacklisted}")
    
    print("\n7. 嘗試使用已撤銷的 Refresh Token...")
    new_token = refresh_access_token(refresh_token)
    if new_token:
        print("   成功取得新 Token（這不應該發生）")
    else:
        print("   無法取得新 Token（預期行為）")

if __name__ == "__main__":
    demo_refresh_token() 