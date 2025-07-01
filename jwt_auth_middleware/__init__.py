"""
JWT Authentication Middleware for Flask Applications

A lightweight, easy-to-use JWT authentication middleware that can be integrated
into any Flask application or deployed as a standalone service.
"""

from .middleware import JWTManager, token_required, admin_required, role_required
from .jwt_utils import create_access_token, verify_token, revoke_token
from .config import JWTConfig

__version__ = "1.0.3"
__author__ = "Your Name"
__email__ = "your.email@example.com"

__all__ = [
    "JWTManager",
    "token_required",
    "admin_required", 
    "role_required",
    "create_access_token",
    "verify_token",
    "revoke_token",
    "JWTConfig"
] 