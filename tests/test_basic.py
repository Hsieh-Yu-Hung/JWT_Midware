"""
Basic tests for jwt_auth_middleware package (v2.0.0)

Tests the middleware functionality only, as business logic has been moved to main projects.
"""

def test_import_decorators():
    """Test that the middleware decorators can be imported"""
    try:
        from jwt_auth_middleware import token_required, admin_required, role_required, permission_required
        assert token_required is not None
        assert admin_required is not None
        assert role_required is not None
        assert permission_required is not None
        print("✅ Middleware decorators imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import decorators: {e}")
        raise

def test_import_verification_functions():
    """Test that JWT verification functions can be imported"""
    try:
        from jwt_auth_middleware import verify_token, verify_access_token, verify_refresh_token
        assert verify_token is not None
        assert verify_access_token is not None
        assert verify_refresh_token is not None
        print("✅ JWT verification functions imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import verification functions: {e}")
        raise

def test_import_config():
    """Test that JWTConfig can be imported"""
    try:
        from jwt_auth_middleware import JWTConfig, create_jwt_config, set_jwt_config
        assert JWTConfig is not None
        assert create_jwt_config is not None
        assert set_jwt_config is not None
        print("✅ JWT configuration functions imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import JWT configuration: {e}")
        raise

def test_business_logic_not_available():
    """Test that business logic functions are no longer available from the package"""
    try:
        from jwt_auth_middleware import create_access_token
        print("❌ create_access_token should not be available in v2.0.0")
        assert False
    except ImportError:
        print("✅ Business logic functions correctly removed from package")
    
    try:
        from jwt_auth_middleware import revoke_token
        print("❌ revoke_token should not be available in v2.0.0")
        assert False
    except ImportError:
        print("✅ Business logic functions correctly removed from package")

def test_package_version():
    """Test that the package version is correct"""
    try:
        from jwt_auth_middleware import __version__
        assert __version__ == "2.0.0"
        print(f"✅ Package version is correct: {__version__}")
    except ImportError as e:
        print(f"❌ Failed to import version: {e}")
        raise

if __name__ == "__main__":
    print("🧪 Running basic tests for jwt_auth_middleware v2.0.0...")
    
    test_import_decorators()
    test_import_verification_functions()
    test_import_config()
    test_business_logic_not_available()
    test_package_version()
    
    print("✅ All basic tests passed!") 