"""
Pytest configuration file for jwt_auth_middleware tests
"""

import sys
import os

# 禁用 .env 檔案載入，避免測試時載入實際的環境變數
os.environ['JWT_LOAD_DOTENV'] = 'false'

# 設置測試環境變數
os.environ['JWT_SECRET_KEY'] = 'test-secret-key'
os.environ['JWT_ALGORITHM'] = 'HS256'
os.environ['JWT_ACCESS_TOKEN_EXPIRES'] = '30'
os.environ['JWT_REFRESH_TOKEN_EXPIRES'] = '1440'
os.environ['MONGODB_API_URL'] = 'http://localhost:3001'
os.environ['JWT_BLACKLIST_COLLECTION'] = 'jwt_blacklist_test'
os.environ['JWT_ENABLE_BLACKLIST'] = 'false'

# Add the package directory to Python path
package_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, package_dir) 