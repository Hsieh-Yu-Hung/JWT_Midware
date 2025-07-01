"""
JWT Authentication Middleware

Provides decorators for JWT token validation and role-based access control.
"""

from functools import wraps
from flask import request, jsonify
from .jwt_utils import verify_token
from .config import JWTConfig

class JWTManager:
    """
    JWT Manager for Flask applications
    
    Initializes JWT configuration and provides utility methods for token management.
    """
    
    def __init__(self, app=None):
        """
        Initialize JWT Manager
        
        Args:
            app: Flask application instance
        """
        self.app = app
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """
        Initialize JWT configuration with Flask app
        
        Args:
            app: Flask application instance
        """
        # Set default JWT configuration
        app.config.setdefault('JWT_SECRET_KEY', app.config.get('SECRET_KEY'))
        app.config.setdefault('JWT_ALGORITHM', 'HS256')
        app.config.setdefault('JWT_ACCESS_TOKEN_EXPIRES', 3600)  # 1 hour
        app.config.setdefault('JWT_REFRESH_TOKEN_EXPIRES', 86400)  # 24 hours
        
        # Create JWT config instance
        self.jwt_config = JWTConfig(
            secret_key=app.config['JWT_SECRET_KEY'],
            algorithm=app.config['JWT_ALGORITHM'],
            access_token_expires=app.config['JWT_ACCESS_TOKEN_EXPIRES'],
            refresh_token_expires=app.config['JWT_REFRESH_TOKEN_EXPIRES']
        )

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
            return jsonify({'error': 'Token is missing'}), 401

        try:
            current_user = verify_token(token)
        except Exception as e:
            return jsonify({'error': str(e)}), 401

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
            return jsonify({'error': 'Token is missing'}), 401

        try:
            current_user = verify_token(token)
            
            # 檢查是否為管理員
            user_roles = current_user.get("roles", [])
            if "admin" not in user_roles:
                return jsonify({'error': 'Admin access required'}), 403
                
        except Exception as e:
            return jsonify({'error': str(e)}), 401

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
                return jsonify({'error': 'Token is missing'}), 401

            try:
                current_user = verify_token(token)
                
                # 將 required_roles 轉換為列表
                if isinstance(required_roles, str):
                    roles_list = [required_roles]
                else:
                    roles_list = required_roles
                
                # 檢查使用者角色
                user_roles = current_user.get("roles", [])
                if not any(role in user_roles for role in roles_list):
                    return jsonify({
                        'error': f'Access denied. Required roles: {roles_list}'
                    }), 403
                    
            except Exception as e:
                return jsonify({'error': str(e)}), 401

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
                return jsonify({'error': 'Token is missing'}), 401

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
                        'error': f'Access denied. Required permissions: {permissions_list}'
                    }), 403
                    
            except Exception as e:
                return jsonify({'error': str(e)}), 401

            return f(current_user, *args, **kwargs)

        return decorated
    return decorator 