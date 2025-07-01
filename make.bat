@echo off
setlocal enabledelayedexpansion

if "%1"=="" goto help
if "%1"=="help" goto help
if "%1"=="install" goto install
if "%1"=="test" goto test
if "%1"=="build" goto build
if "%1"=="clean" goto clean
if "%1"=="bump-patch" goto bump-patch
if "%1"=="bump-minor" goto bump-minor
if "%1"=="bump-major" goto bump-major
if "%1"=="release" goto release
if "%1"=="version" goto version
goto help

:help
echo 可用的命令:
echo   install     - 安裝套件（開發模式）
echo   test        - 運行測試
echo   build       - 構建套件
echo   clean       - 清理構建檔案
echo   bump-patch  - 更新 patch 版本 (1.0.0 -^> 1.0.1)
echo   bump-minor  - 更新 minor 版本 (1.0.0 -^> 1.1.0)
echo   bump-major  - 更新 major 版本 (1.0.0 -^> 2.0.0)
echo   release     - 創建新的 release
echo   version     - 顯示當前版本
goto end

:install
echo 安裝套件（開發模式）...
pip install -e .
goto end

:test
echo 運行測試...
python -m pytest tests/ -v
goto end

:build
echo 構建套件...
python -m build
goto end

:clean
echo 清理構建檔案...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
for /d %%i in (*.egg-info) do rmdir /s /q "%%i"
goto end

:bump-patch
echo 更新 patch 版本...
python scripts/bump_version.py patch
goto end

:bump-minor
echo 更新 minor 版本...
python scripts/bump_version.py minor
goto end

:bump-major
echo 更新 major 版本...
python scripts/bump_version.py major
goto end

:release
echo 請選擇版本更新類型:
echo 1. patch (1.0.0 -^> 1.0.1)
echo 2. minor (1.0.0 -^> 1.1.0)
echo 3. major (1.0.0 -^> 2.0.0)
set /p choice="請輸入選擇 (1-3): "
if "%choice%"=="1" goto bump-patch
if "%choice%"=="2" goto bump-minor
if "%choice%"=="3" goto bump-major
echo 無效選擇
goto end

:version
echo 顯示當前版本...
python -c "import jwt_auth_middleware; print(jwt_auth_middleware.__version__)"
goto end

:end 