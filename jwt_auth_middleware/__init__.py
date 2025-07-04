"""
JWT Authentication Middleware for Flask Applications

A lightweight, easy-to-use JWT authentication middleware that can be integrated
into any Flask application or deployed as a standalone service.
"""

from .middleware import token_required, admin_required, role_required
from .jwt_utils import (
    create_access_token, 
    create_refresh_token,
    create_token_pair,
    verify_token,
    verify_access_token,
    verify_refresh_token,
    refresh_access_token,
    revoke_token,
    revoke_token_pair,
    is_token_blacklisted,
    remove_from_blacklist,
    cleanup_expired_blacklist_tokens,
    get_blacklist_statistics,
    initialize_blacklist_system
)
from .config import JWTConfig
from .blacklist import BlacklistManager

__version__ = "1.3.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

__all__ = [
    "token_required",
    "admin_required", 
    "role_required",
    "create_access_token",
    "create_refresh_token",
    "create_token_pair",
    "verify_token",
    "verify_access_token",
    "verify_refresh_token",
    "refresh_access_token",
    "revoke_token",
    "revoke_token_pair",
    "JWTConfig",
    "BlacklistManager",
    "is_token_blacklisted",
    "remove_from_blacklist",
    "cleanup_expired_blacklist_tokens",
    "get_blacklist_statistics",
    "initialize_blacklist_system"
] 