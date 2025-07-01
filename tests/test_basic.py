"""
Basic tests for jwt_auth_middleware package
"""

def test_import():
    """Test that the package can be imported"""
    try:
        from jwt_auth_middleware import JWTManager
        assert JWTManager is not None
        print("✅ JWTManager imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import JWTManager: {e}")
        raise

def test_decorators_import():
    """Test that decorators can be imported"""
    try:
        from jwt_auth_middleware import token_required, admin_required
        assert token_required is not None
        assert admin_required is not None
        print("✅ Decorators imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import decorators: {e}")
        raise

def test_utils_import():
    """Test that utility functions can be imported"""
    try:
        from jwt_auth_middleware import create_access_token, verify_token
        assert create_access_token is not None
        assert verify_token is not None
        print("✅ Utility functions imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import utility functions: {e}")
        raise 