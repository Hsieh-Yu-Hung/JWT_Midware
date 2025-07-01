#!/usr/bin/env python3
"""
自動化版本管理腳本

使用方法:
    python scripts/bump_version.py patch   # 1.0.0 -> 1.0.1
    python scripts/bump_version.py minor   # 1.0.0 -> 1.1.0
    python scripts/bump_version.py major   # 1.0.0 -> 2.0.0
"""

import re
import sys
import os
from pathlib import Path

def read_version_from_file(file_path, pattern):
    """從檔案中讀取版本號"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        match = re.search(pattern, content)
        if match:
            return match.group(1)
    return None

def update_version_in_file(file_path, pattern, new_version):
    """更新檔案中的版本號"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 使用 lambda 函數來避免正則表達式組引用問題
    def replace_func(match):
        groups = list(match.groups())
        if len(groups) >= 2:
            return f"{groups[0]}{new_version}{groups[1]}"
        elif len(groups) == 1:
            return f"{groups[0]}{new_version}"
        else:
            return new_version
    
    new_content = re.sub(pattern, replace_func, content)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)

def bump_version(current_version, bump_type):
    """根據 bump_type 更新版本號"""
    major, minor, patch = map(int, current_version.split('.'))
    
    if bump_type == 'major':
        major += 1
        minor = 0
        patch = 0
    elif bump_type == 'minor':
        minor += 1
        patch = 0
    elif bump_type == 'patch':
        patch += 1
    else:
        raise ValueError(f"Invalid bump type: {bump_type}")
    
    return f"{major}.{minor}.{patch}"

def main():
    if len(sys.argv) != 2:
        print("使用方法: python scripts/bump_version.py [patch|minor|major]")
        sys.exit(1)
    
    bump_type = sys.argv[1]
    if bump_type not in ['patch', 'minor', 'major']:
        print("錯誤: bump_type 必須是 patch, minor, 或 major")
        sys.exit(1)
    
    # 讀取當前版本號
    setup_version = read_version_from_file('setup.py', r'version="([^"]+)"')
    init_version = read_version_from_file('jwt_auth_middleware/__init__.py', r'__version__ = "([^"]+)"')
    
    if setup_version != init_version:
        print(f"錯誤: 版本號不一致 - setup.py: {setup_version}, __init__.py: {init_version}")
        sys.exit(1)
    
    current_version = setup_version
    new_version = bump_version(current_version, bump_type)
    
    print(f"更新版本號: {current_version} -> {new_version}")
    
    # 更新檔案
    update_version_in_file('setup.py', r'(version=")[^"]+(")', new_version)
    update_version_in_file('jwt_auth_middleware/__init__.py', r'(__version__ = ")[^"]+(")', new_version)
    update_version_in_file('.bumpversion.cfg', r'(current_version = )[^\n]+', new_version)
    
    print("✅ 版本號更新完成！")
    print(f"新版本: {new_version}")
    print("\n下一步:")
    print(f"1. git add .")
    print(f"2. git commit -m 'Bump version to {new_version}'")
    print(f"3. git tag v{new_version}")
    print(f"4. git push origin main --tags")

if __name__ == "__main__":
    main() 