"""
Basic tests for jwt_auth_middleware package
"""

def test_import():
    """Test that the package can be imported"""
    try:
        from jwt_auth_middleware import token_required, admin_required, role_required
        assert token_required is not None
        assert admin_required is not None
        assert role_required is not None
        print("✅ Decorators imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import decorators: {e}")
        raise

def test_jwt_utils_import():
    """Test that JWT utilities can be imported"""
    try:
        from jwt_auth_middleware import create_access_token, verify_token, revoke_token
        assert create_access_token is not None
        assert verify_token is not None
        assert revoke_token is not None
        print("✅ JWT utilities imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import JWT utilities: {e}")
        raise

def test_config_import():
    """Test that JWTConfig can be imported"""
    try:
        from jwt_auth_middleware import JWTConfig
        assert JWTConfig is not None
        print("✅ JWTConfig imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import JWTConfig: {e}")
        raise 