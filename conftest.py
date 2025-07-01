"""
Pytest configuration file for jwt_auth_middleware tests
"""

import sys
import os

# Add the package directory to Python path
package_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, package_dir) 