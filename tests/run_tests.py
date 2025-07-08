#!/usr/bin/env python3
"""
Test runner for jwt_auth_middleware package (v2.0.0)

Runs all tests for the refactored middleware package.
"""

import sys
import os
import subprocess
import importlib.util

def run_basic_tests():
    """運行基本測試"""
    print("🧪 Running basic tests...")
    try:
        from test_basic import test_import_decorators, test_import_verification_functions, test_import_config, test_business_logic_not_available, test_package_version
        
        test_import_decorators()
        test_import_verification_functions()
        test_import_config()
        test_business_logic_not_available()
        test_package_version()
        
        print("✅ Basic tests passed!")
        return True
    except Exception as e:
        print(f"❌ Basic tests failed: {e}")
        return False

def run_config_tests():
    """運行配置測試"""
    print("🧪 Running configuration tests...")
    try:
        from test_config import (
            test_config_without_dotenv, test_config_validation, test_config_to_dict,
            test_config_creation, test_config_string_representation, test_config_repr,
            test_config_with_different_algorithms, test_config_api_mode, test_config_blacklist_settings
        )
        
        test_config_without_dotenv()
        test_config_validation()
        test_config_to_dict()
        test_config_creation()
        test_config_string_representation()
        test_config_repr()
        test_config_with_different_algorithms()
        test_config_api_mode()
        test_config_blacklist_settings()
        
        print("✅ Configuration tests passed!")
        return True
    except Exception as e:
        print(f"❌ Configuration tests failed: {e}")
        return False

def run_verification_tests():
    """運行驗證測試"""
    print("🧪 Running verification tests...")
    try:
        from test_verification import (
            test_verify_token_valid, test_verify_token_invalid_signature,
            test_verify_token_expired, test_verify_access_token_valid,
            test_verify_access_token_wrong_type, test_verify_refresh_token_valid,
            test_verify_refresh_token_wrong_type, test_verify_token_missing_type,
            test_verify_token_with_roles, test_verify_token_with_permissions,
            test_verify_token_malformed, test_verify_token_empty,
            test_verify_token_none, test_config_not_initialized
        )
        
        # 設置測試配置
        from jwt_auth_middleware import JWTConfig, set_jwt_config
        test_config = JWTConfig(
            secret_key="test-jwt-secret",
            config_file="test_config.yaml"
        )
        set_jwt_config(test_config)
        
        test_verify_token_valid(test_config)
        test_verify_token_invalid_signature(test_config)
        test_verify_token_expired(test_config)
        test_verify_access_token_valid(test_config)
        test_verify_access_token_wrong_type(test_config)
        test_verify_refresh_token_valid(test_config)
        test_verify_refresh_token_wrong_type(test_config)
        test_verify_token_missing_type(test_config)
        test_verify_token_with_roles(test_config)
        test_verify_token_with_permissions(test_config)
        test_verify_token_malformed(test_config)
        test_verify_token_empty(test_config)
        test_verify_token_none(test_config)
        test_config_not_initialized()
        
        print("✅ Verification tests passed!")
        return True
    except Exception as e:
        print(f"❌ Verification tests failed: {e}")
        return False

def run_middleware_tests():
    """運行中間件測試"""
    print("🧪 Running middleware tests...")
    try:
        # 使用 pytest 運行中間件測試
        result = subprocess.run([
            sys.executable, "-m", "pytest", "test_middleware.py", "-v"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Middleware tests passed!")
            return True
        else:
            print(f"❌ Middleware tests failed:")
            print(result.stdout)
            print(result.stderr)
            return False
    except Exception as e:
        print(f"❌ Middleware tests failed: {e}")
        return False

def run_pytest_all():
    """使用 pytest 運行所有測試"""
    print("🧪 Running all tests with pytest...")
    try:
        result = subprocess.run([
            sys.executable, "-m", "pytest", ".", "-v", "--tb=short"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ All pytest tests passed!")
            return True
        else:
            print(f"❌ Some pytest tests failed:")
            print(result.stdout)
            print(result.stderr)
            return False
    except Exception as e:
        print(f"❌ Pytest execution failed: {e}")
        return False

def main():
    """主測試執行器"""
    print("🚀 Starting jwt_auth_middleware v2.0.0 tests...")
    print("=" * 60)
    
    # 確保在正確的目錄中
    test_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(test_dir)
    
    # 添加當前目錄到 Python 路徑
    sys.path.insert(0, os.path.dirname(test_dir))
    
    results = []
    
    # 運行基本測試
    results.append(("Basic Tests", run_basic_tests()))
    
    # 運行配置測試
    results.append(("Configuration Tests", run_config_tests()))
    
    # 運行驗證測試
    results.append(("Verification Tests", run_verification_tests()))
    
    # 運行中間件測試
    results.append(("Middleware Tests", run_middleware_tests()))
    
    # 運行 pytest 所有測試
    results.append(("Pytest All Tests", run_pytest_all()))
    
    # 顯示結果
    print("\n" + "=" * 60)
    print("📊 Test Results Summary:")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:<25} {status}")
        if result:
            passed += 1
    
    print("=" * 60)
    print(f"Total: {passed}/{total} test suites passed")
    
    if passed == total:
        print("🎉 All tests passed! The middleware package is working correctly.")
        return 0
    else:
        print("⚠️  Some tests failed. Please check the output above.")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 