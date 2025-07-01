#!/bin/bash

# 顏色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 顯示幫助訊息
show_help() {
    echo -e "${BLUE}可用的命令:${NC}"
    echo -e "${GREEN}  install     ${NC}- 安裝套件（開發模式）"
    echo -e "${GREEN}  test        ${NC}- 運行測試"
    echo -e "${GREEN}  build       ${NC}- 構建套件"
    echo -e "${GREEN}  clean       ${NC}- 清理構建檔案"
    echo -e "${GREEN}  bump-patch  ${NC}- 更新 patch 版本 (1.0.0 -> 1.0.1)"
    echo -e "${GREEN}  bump-minor  ${NC}- 更新 minor 版本 (1.0.0 -> 1.1.0)"
    echo -e "${GREEN}  bump-major  ${NC}- 更新 major 版本 (1.0.0 -> 2.0.0)"
    echo -e "${GREEN}  release     ${NC}- 創建新的 release"
    echo -e "${GREEN}  publish     ${NC}- 自動推送並標記版本"
    echo -e "${GREEN}  version     ${NC}- 顯示當前版本"
}

# 安裝套件
install() {
    echo -e "${BLUE}安裝套件（開發模式）...${NC}"
    pip install -e .
}

# 運行測試
test() {
    echo -e "${BLUE}運行測試...${NC}"
    python -m pytest tests/ -v
}

# 構建套件
build() {
    echo -e "${BLUE}構建套件...${NC}"
    python -m build
}

# 清理構建檔案
clean() {
    echo -e "${BLUE}清理構建檔案...${NC}"
    rm -rf build/ dist/ *.egg-info/
}

# 更新版本
bump_version() {
    local bump_type=$1
    echo -e "${BLUE}更新 ${bump_type} 版本...${NC}"
    python scripts/bump_version.py $bump_type
}

# 互動式 release
release() {
    echo -e "${BLUE}請選擇版本更新類型:${NC}"
    echo "1. patch (1.0.0 -> 1.0.1)"
    echo "2. minor (1.0.0 -> 1.1.0)"
    echo "3. major (1.0.0 -> 2.0.0)"
    read -p "請輸入選擇 (1-3): " choice
    
    case $choice in
        1) bump_version "patch" ;;
        2) bump_version "minor" ;;
        3) bump_version "major" ;;
        *) echo -e "${RED}無效選擇${NC}" ;;
    esac
}

publish() {
    TAG="v$(python -c 'import jwt_auth_middleware; print(jwt_auth_middleware.__version__)')"
    echo -e "${BLUE}自動推送並標記版本: $TAG${NC}"

    # git add/commit/push
    git add .
    git commit -m "release: JWT Auth Middleware $TAG"
    git push -u origin main

    # tag & push tag
    git tag -a $TAG -m "Release $TAG"
    git push origin $TAG

    echo ""
    echo "🎉 推送完成！"
    echo ""
    echo "📋 下一步："
    echo "1. 檢查 GitHub 倉庫：https://github.com/Hsieh-Yu-Hung/JWT_Midware"
    echo "2. 創建 GitHub Release（可選）"
}

# 顯示版本
version() {
    echo -e "${BLUE}顯示當前版本...${NC}"
    python -c "import jwt_auth_middleware; print(jwt_auth_middleware.__version__)"
}

# 主函數
main() {
    case "${1:-help}" in
        "help"|"") show_help ;;
        "install") install ;;
        "test") test ;;
        "build") build ;;
        "clean") clean ;;
        "bump-patch") bump_version "patch" ;;
        "bump-minor") bump_version "minor" ;;
        "bump-major") bump_version "major" ;;
        "release") release ;;
        "publish") publish ;;
        "version") version ;;
        *) 
            echo -e "${RED}未知命令: $1${NC}"
            show_help
            exit 1
            ;;
    esac
}

# 執行主函數
main "$@" 