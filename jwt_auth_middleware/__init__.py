"""
JWT Authentication Middleware for Flask Applications

A lightweight, easy-to-use JWT authentication middleware that provides
decorators for JWT token validation and role-based access control.
Business logic functions have been moved to main projects.
"""

from .middleware import token_required, admin_required, role_required, permission_required
from .jwt_utils import (
    verify_token,
    verify_access_token,
    verify_refresh_token,
    set_jwt_config
)
from .config import JWTConfig, create_jwt_config

__version__ = "2.0.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

__all__ = [
    # Middleware decorators
    "token_required",
    "admin_required", 
    "role_required",
    "permission_required",
    
    # Token verification functions
    "verify_token",
    "verify_access_token",
    "verify_refresh_token",
    
    # Configuration
    "JWTConfig",
    "create_jwt_config",
    "set_jwt_config"
] 