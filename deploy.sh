#!/bin/bash

# JWT Auth Middleware 部署腳本

set -e

echo "🚀 開始部署 JWT Auth Middleware 套件..."

# 檢查是否在正確的目錄
if [ ! -f "setup.py" ]; then
    echo "❌ 錯誤：請在套件根目錄執行此腳本"
    exit 1
fi

# 清理舊的構建文件
echo "🧹 清理舊的構建文件..."
rm -rf build/ dist/ *.egg-info/

# 安裝構建依賴
echo "📦 安裝構建依賴..."
pip install --upgrade build twine

# 構建套件
echo "🔨 構建套件..."
python -m build

# 檢查構建結果
echo "✅ 構建完成！"
echo "📁 構建文件："
ls -la dist/

# 檢查套件
echo "🔍 檢查套件..."
twine check dist/*

echo ""
echo "🎉 套件構建成功！"
echo ""
echo "📋 下一步："
echo "1. 測試套件：python -m twine upload --repository testpypi dist/*"
echo "2. 發布到 PyPI：python -m twine upload dist/*"
echo "3. 或者推送到 GitHub 並創建 release tag"
echo ""
echo "💡 提示："
echo "- 發布前請確保版本號已更新"
echo "- 確保所有測試都通過"
echo "- 檢查 README.md 是否完整" 