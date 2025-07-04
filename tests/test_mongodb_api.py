#!/usr/bin/env python3
"""
測試 MongoDB API 連接
"""

import requests
import json

# MongoDB API 設定
MONGODB_API_URL = "https://db-operation-xbbbehjawk.cn-shanghai.fcapp.run"
COLLECTION_NAME = "jwt_blacklist"

def test_mongodb_api():
    """測試 MongoDB API 連接"""
    
    print("🔍 測試 MongoDB API 連接...")
    
    # 1. 健康檢查
    print("\n[1] 健康檢查...")
    try:
        response = requests.get(f"{MONGODB_API_URL}/health_check", timeout=10)
        print(f"狀態碼: {response.status_code}")
        print(f"回應: {response.json()}")
    except Exception as e:
        print(f"❌ 健康檢查失敗: {e}")
        assert False
    
    # 2. 測試新增文件
    print("\n[2] 測試新增文件...")
    test_document = {
        "token_hash": "test_hash_123",
        "reason": "test_revocation",
        "revoked_at": "2024-01-01T00:00:00Z",
        "expires_at": "2024-01-01T01:00:00Z"
    }
    
    try:
        response = requests.post(
            f"{MONGODB_API_URL}/add/document/{COLLECTION_NAME}",
            json={"data": test_document},
            timeout=10
        )
        print(f"狀態碼: {response.status_code}")
        print(f"回應: {response.json()}")
        
        if response.status_code == 200:
            result = response.json()
            inserted_id = result.get("inserted_id")
            print(f"✅ 新增成功，文件 ID: {inserted_id}")
        else:
            print("❌ 新增失敗")
            assert False
            
    except Exception as e:
        print(f"❌ 新增文件失敗: {e}")
        assert False
    
    # 3. 測試查詢文件
    print("\n[3] 測試查詢文件...")
    try:
        response = requests.get(
            f"{MONGODB_API_URL}/search/documents/{COLLECTION_NAME}",
            params={"token_hash": "test_hash_123"},
            timeout=10
        )
        print(f"狀態碼: {response.status_code}")
        print(f"回應: {response.json()}")
        
        if response.status_code == 200:
            result = response.json()
            documents = result.get("data", [])
            print(f"✅ 查詢成功，找到 {len(documents)} 筆文件")
        else:
            print("❌ 查詢失敗")
            assert False
            
    except Exception as e:
        print(f"❌ 查詢文件失敗: {e}")
        assert False
    
    # 4. 測試統計查詢
    print("\n[4] 測試統計查詢...")
    try:
        response = requests.get(
            f"{MONGODB_API_URL}/search/documents/{COLLECTION_NAME}/count",
            timeout=10
        )
        print(f"狀態碼: {response.status_code}")
        print(f"回應: {response.json()}")
        
        if response.status_code == 200:
            result = response.json()
            count = result.get("count", 0)
            print(f"✅ 統計成功，總文件數: {count}")
        else:
            print("❌ 統計失敗")
            assert False
            
    except Exception as e:
        print(f"❌ 統計查詢失敗: {e}")
        assert False
    
    # 5. 清理測試資料
    print("\n[5] 清理測試資料...")
    try:
        # 先查詢文件 ID
        response = requests.get(
            f"{MONGODB_API_URL}/search/documents/{COLLECTION_NAME}",
            params={"token_hash": "test_hash_123"},
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            documents = result.get("data", [])
            
            if documents:
                doc_id = documents[0].get("_id")
                if doc_id:
                    # 刪除文件
                    delete_response = requests.delete(
                        f"{MONGODB_API_URL}/delete/document/{COLLECTION_NAME}/{doc_id}",
                        timeout=10
                    )
                    print(f"刪除狀態碼: {delete_response.status_code}")
                    print(f"刪除回應: {delete_response.json()}")
                    
                    if delete_response.status_code == 200:
                        print("✅ 清理成功")
                    else:
                        print("❌ 清理失敗")
                        assert False
                else:
                    print("❌ 找不到文件 ID")
                    assert False
            else:
                print("❌ 找不到測試文件")
                assert False
        else:
            print("❌ 查詢文件失敗")
            assert False
            
    except Exception as e:
        print(f"❌ 清理測試資料失敗: {e}")
        assert False
    
    print("\n🎉 所有測試通過！MongoDB API 連接正常")
    assert True

if __name__ == "__main__":
    success = test_mongodb_api()
    if success:
        print("\n✅ MongoDB API 測試成功，可以開始使用黑名單功能")
    else:
        print("\n❌ MongoDB API 測試失敗，請檢查連接設定") 