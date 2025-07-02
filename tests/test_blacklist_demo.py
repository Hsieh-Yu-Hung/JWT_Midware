#!/usr/bin/env python3
"""
JWT 黑名單系統演示腳本

這個腳本展示了如何使用黑名單功能來撤銷 JWT tokens
"""

import os
import sys
from datetime import datetime

# 添加專案路徑
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from jwt_auth_middleware import (
    JWTConfig,
    create_access_token,
    verify_token,
    revoke_token,
    is_token_blacklisted,
    remove_from_blacklist,
    cleanup_expired_blacklist_tokens,
    get_blacklist_statistics,
    initialize_blacklist_system
)

def print_separator(title):
    """印出分隔線"""
    print("\n" + "="*50)
    print(f" {title}")
    print("="*50)

def demo_basic_blacklist():
    """演示基本黑名單功能"""
    print_separator("基本黑名單功能演示")
    
    # 建立測試配置
    config = JWTConfig(
        secret_key="demo-secret-key",
        access_token_expires=30,
        mongodb_api_url="http://localhost:3000",  # 請替換為您的 MongoDB API URL
        enable_blacklist=True
    )
    
    print("1. 建立測試 JWT token...")
    token_data = {
        "sub": "demo_user",
        "role": "user",
        "created_at": datetime.now().isoformat()
    }
    token = create_access_token(token_data)
    print(f"   Token: {token[:50]}...")
    
    print("\n2. 驗證 token...")
    try:
        payload = verify_token(token)
        print(f"   Token 有效，使用者: {payload['sub']}")
    except Exception as e:
        print(f"   Token 驗證失敗: {e}")
    
    print("\n3. 檢查 token 是否在黑名單中...")
    is_blacklisted = is_token_blacklisted(token)
    print(f"   Token 在黑名單中: {is_blacklisted}")
    
    print("\n4. 撤銷 token...")
    success = revoke_token(token, reason="demo_revocation")
    print(f"   Token 撤銷成功: {success}")
    
    print("\n5. 再次檢查 token 是否在黑名單中...")
    is_blacklisted = is_token_blacklisted(token)
    print(f"   Token 在黑名單中: {is_blacklisted}")
    
    print("\n6. 嘗試驗證已撤銷的 token...")
    try:
        payload = verify_token(token)
        print("   Token 仍然有效（這不應該發生）")
    except Exception as e:
        print(f"   Token 驗證失敗（預期行為）: {e}")
    
    print("\n7. 從黑名單中移除 token...")
    success = remove_from_blacklist(token)
    print(f"   從黑名單移除成功: {success}")
    
    print("\n8. 最終檢查 token 是否在黑名單中...")
    is_blacklisted = is_token_blacklisted(token)
    print(f"   Token 在黑名單中: {is_blacklisted}")

def demo_blacklist_statistics():
    """演示黑名單統計功能"""
    print_separator("黑名單統計功能演示")
    
    print("取得黑名單統計資訊...")
    stats = get_blacklist_statistics()
    
    print(f"   總 tokens: {stats['total_tokens']}")
    print(f"   過期 tokens: {stats['expired_tokens']}")
    print(f"   活躍 tokens: {stats['active_tokens']}")
    
    print("\n清理過期的 tokens...")
    cleaned_count = cleanup_expired_blacklist_tokens()
    print(f"   清理了 {cleaned_count} 個過期 tokens")

def demo_blacklist_disabled():
    """演示黑名單功能停用時的行為"""
    print_separator("黑名單功能停用演示")
    
    # 建立停用黑名單的配置
    config = JWTConfig(
        secret_key="demo-secret-key",
        enable_blacklist=False
    )
    
    print("1. 建立測試 token...")
    token_data = {"sub": "demo_user", "role": "user"}
    token = create_access_token(token_data)
    
    print("2. 嘗試撤銷 token（黑名單已停用）...")
    success = revoke_token(token, reason="demo_revocation")
    print(f"   Token 撤銷結果: {success}")
    
    print("3. 檢查 token 是否在黑名單中...")
    is_blacklisted = is_token_blacklisted(token)
    print(f"   Token 在黑名單中: {is_blacklisted}")
    
    print("4. 驗證 token...")
    try:
        payload = verify_token(token)
        print("   Token 仍然有效（因為黑名單已停用）")
    except Exception as e:
        print(f"   Token 驗證失敗: {e}")

def main():
    """主函數"""
    print("JWT 黑名單系統演示")
    print("請確保您的 MongoDB API 正在運行")
    print("並更新腳本中的 MongoDB API URL")
    
    try:
        # 初始化黑名單系統
        print("\n初始化黑名單系統...")
        success = initialize_blacklist_system("http://localhost:3000")
        if success:
            print("✓ 黑名單系統初始化成功")
        else:
            print("✗ 黑名單系統初始化失敗")
            print("請檢查 MongoDB API URL 和網路連線")
            return
        
        # 執行演示
        demo_basic_blacklist()
        demo_blacklist_statistics()
        demo_blacklist_disabled()
        
        print_separator("演示完成")
        print("✓ 所有演示功能執行完成")
        
    except Exception as e:
        print(f"\n✗ 演示過程中發生錯誤: {e}")
        print("請檢查配置和網路連線")

if __name__ == "__main__":
    main() 