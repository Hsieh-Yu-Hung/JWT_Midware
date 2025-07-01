#!/usr/bin/env python3
"""
Simple test script to verify package import
"""

try:
    from jwt_auth_middleware import JWTManager, token_required, admin_required
    print("✅ Successfully imported jwt_auth_middleware")
    print(f"JWTManager: {JWTManager}")
    print(f"token_required: {token_required}")
    print(f"admin_required: {admin_required}")
except ImportError as e:
    print(f"❌ Failed to import jwt_auth_middleware: {e}")
    import sys
    print(f"Python path: {sys.path}")
    import os
    print(f"Current directory: {os.getcwd()}")
    print(f"Files in current directory: {os.listdir('.')}") 