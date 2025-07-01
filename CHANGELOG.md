# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.0.0] - 2024-01-15

### Added
- Initial release of JWT Authentication Middleware
- Flask integration with JWT token validation
- MongoDB support for token blacklisting
- Role-based access control (RBAC)
- Token expiration and cleanup functionality
- Comprehensive error handling and logging
- Easy-to-use decorators for route protection
- Support for custom claims and user data
- Automatic token refresh capabilities
- Built-in security features (CSRF protection, rate limiting)

### Features
- `@token_required` decorator for protecting routes
- `@admin_required` decorator for admin-only routes
- Automatic token validation and user extraction
- MongoDB integration for persistent storage
- Configurable JWT settings and expiration times
- Comprehensive logging and error messages
- Support for multiple user roles and permissions

### Documentation
- Complete API documentation
- Usage examples and best practices
- Installation and setup instructions
- Troubleshooting guide 