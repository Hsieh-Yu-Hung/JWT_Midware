"""
JWT Authentication Middleware

Provides decorators for JWT token validation and role-based access control.
"""

from functools import wraps
from flask import request, jsonify
from .jwt_utils import verify_token

def token_required(f):
    """
    驗證 JWT token 的裝飾器
    
    Args:
        f: 被裝飾的函數
        
    Returns:
        裝飾後的函數，會自動驗證 token 並傳入 current_user 參數
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if 'Authorization' in request.headers:
            bearer = request.headers['Authorization']
            if bearer.startswith("Bearer "):
                token = bearer.split(" ")[1]

        if not token:
            return jsonify({'message': 'Token is missing'}), 403

        try:
            current_user = verify_token(token)
        except Exception as e:
            return jsonify({'message': str(e)}), 403

        return f(current_user, *args, **kwargs)

    return decorated

def admin_required(f):
    """
    要求管理員權限的裝飾器
    
    Args:
        f: 被裝飾的函數
        
    Returns:
        裝飾後的函數，會驗證 token 並檢查是否為管理員
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if 'Authorization' in request.headers:
            bearer = request.headers['Authorization']
            if bearer.startswith("Bearer "):
                token = bearer.split(" ")[1]

        if not token:
            return jsonify({'message': 'Token is missing'}), 403

        try:
            current_user = verify_token(token)
            
            # 檢查是否為管理員
            if current_user.get("role") != "admin":
                return jsonify({'message': 'Admin access required'}), 403
                
        except Exception as e:
            return jsonify({'message': str(e)}), 403

        return f(current_user, *args, **kwargs)

    return decorated

def role_required(required_roles):
    """
    要求特定角色的裝飾器
    
    Args:
        required_roles: 字串或列表，指定需要的角色
        
    Returns:
        裝飾器函數
    """
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            token = None

            if 'Authorization' in request.headers:
                bearer = request.headers['Authorization']
                if bearer.startswith("Bearer "):
                    token = bearer.split(" ")[1]

            if not token:
                return jsonify({'message': 'Token is missing'}), 403

            try:
                current_user = verify_token(token)
                
                # 將 required_roles 轉換為列表
                if isinstance(required_roles, str):
                    roles_list = [required_roles]
                else:
                    roles_list = required_roles
                
                # 檢查使用者角色
                user_role = current_user.get("role")
                if user_role not in roles_list:
                    return jsonify({
                        'message': f'Access denied. Required roles: {roles_list}'
                    }), 403
                    
            except Exception as e:
                return jsonify({'message': str(e)}), 403

            return f(current_user, *args, **kwargs)

        return decorated
    return decorator

def permission_required(required_permissions):
    """
    要求特定權限的裝飾器
    
    Args:
        required_permissions: 字串或列表，指定需要的權限
        
    Returns:
        裝飾器函數
    """
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            token = None

            if 'Authorization' in request.headers:
                bearer = request.headers['Authorization']
                if bearer.startswith("Bearer "):
                    token = bearer.split(" ")[1]

            if not token:
                return jsonify({'message': 'Token is missing'}), 403

            try:
                current_user = verify_token(token)
                
                # 將 required_permissions 轉換為列表
                if isinstance(required_permissions, str):
                    permissions_list = [required_permissions]
                else:
                    permissions_list = required_permissions
                
                # 檢查使用者權限（假設權限存在於 token 中）
                user_permissions = current_user.get("permissions", [])
                if not all(perm in user_permissions for perm in permissions_list):
                    return jsonify({
                        'message': f'Access denied. Required permissions: {permissions_list}'
                    }), 403
                    
            except Exception as e:
                return jsonify({'message': str(e)}), 403

            return f(current_user, *args, **kwargs)

        return decorated
    return decorator 