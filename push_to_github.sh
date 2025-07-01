#!/bin/bash

# TAG
TAG="v1.0.1"

# 推送 JWT Auth Middleware 到 GitHub 腳本

set -e

echo "🚀 開始推送 JWT Auth Middleware 到 GitHub..."

# 檢查是否在正確的目錄
if [ ! -f "setup.py" ]; then
    echo "❌ 錯誤：請在套件根目錄執行此腳本"
    exit 1
fi

# 檢查 git 是否已初始化
if [ ! -d ".git" ]; then
    echo "📁 初始化 Git 倉庫..."
    git init
    # 設置默認分支為 main
    git branch -M main
fi

# 添加所有文件
echo "📦 添加文件到 Git..."
git add .

# 提交變更
echo "💾 提交變更..."
git commit -m "feat: Initial release of JWT Auth Middleware $TAG"

# 檢查遠端倉庫
if ! git remote get-url origin > /dev/null 2>&1; then
    echo "🔗 添加遠端倉庫..."
    git remote add origin https://github.com/Hsieh-Yu-Hung/JWT_Midware.git
else
    echo "🔄 更新遠端倉庫 URL..."
    git remote set-url origin https://github.com/Hsieh-Yu-Hung/JWT_Midware.git
fi

# 推送到 GitHub
echo "📤 推送到 GitHub..."
git remote set-url origin git@github.com:Hsieh-Yu-Hung/JWT_Midware.git
git push -u origin main

# 創建 release tag
echo "🏷️ 創建 release tag..."
git tag -a $TAG -m "Release $TAG"
git push origin $TAG

echo ""
echo "🎉 推送完成！"
echo ""
echo "📋 下一步："
echo "1. 檢查 GitHub 倉庫：https://github.com/Hsieh-Yu-Hung/JWT_Midware"
echo "2. 創建 GitHub Release（可選）"
echo "3. 發布到 PyPI（可選）：./deploy.sh" 