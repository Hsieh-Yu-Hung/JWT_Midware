#!/usr/bin/env python3
"""
Simple test script to verify package import
"""

import sys
import os

print("=== Package Import Test ===")
print(f"Python version: {sys.version}")
print(f"Python executable: {sys.executable}")
print(f"Current directory: {os.getcwd()}")
print(f"Python path: {sys.path}")

print("\n=== Files in current directory ===")
for file in os.listdir('.'):
    print(f"  {file}")

print("\n=== Testing import ===")
try:
    from jwt_auth_middleware import JWTManager, token_required, admin_required
    print("✅ Successfully imported jwt_auth_middleware")
    print(f"JWTManager: {JWTManager}")
    print(f"token_required: {token_required}")
    print(f"admin_required: {admin_required}")
except ImportError as e:
    print(f"❌ Failed to import jwt_auth_middleware: {e}")
    print(f"Error type: {type(e)}")
    print(f"Error args: {e.args}")
    
    # Try to find the package
    print("\n=== Looking for package ===")
    for path in sys.path:
        if os.path.exists(path):
            try:
                files = os.listdir(path)
                jwt_files = [f for f in files if 'jwt' in f.lower()]
                if jwt_files:
                    print(f"Found JWT-related files in {path}: {jwt_files}")
            except (OSError, PermissionError):
                pass 