"""
JWT Authentication Middleware for Flask Applications

A lightweight, easy-to-use JWT authentication middleware that can be integrated
into any Flask application or deployed as a standalone service.
"""

from .middleware import JWTManager, token_required, admin_required, role_required
from .jwt_utils import (
    create_access_token, 
    verify_token, 
    revoke_token,
    is_token_blacklisted,
    remove_from_blacklist,
    cleanup_expired_blacklist_tokens,
    get_blacklist_statistics,
    initialize_blacklist_system
)
from .config import JWTConfig
from .blacklist import BlacklistManager, init_blacklist_manager, get_blacklist_manager

__version__ = "1.1.0"
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
    "JWTConfig",
    "BlacklistManager",
    "init_blacklist_manager",
    "get_blacklist_manager",
    "is_token_blacklisted",
    "remove_from_blacklist",
    "cleanup_expired_blacklist_tokens",
    "get_blacklist_statistics",
    "initialize_blacklist_system"
] 