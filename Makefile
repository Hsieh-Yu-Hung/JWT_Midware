.PHONY: help install test build clean bump-patch bump-minor bump-major release

help: ## 顯示幫助訊息
	@echo "可用的命令:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## 安裝套件（開發模式）
	pip install -e .

test: ## 運行測試
	python -m pytest tests/ -v

build: ## 構建套件
	python -m build

clean: ## 清理構建檔案
	rm -rf build/ dist/ *.egg-info/

bump-patch: ## 更新 patch 版本 (1.0.0 -> 1.0.1)
	python scripts/bump_version.py patch

bump-minor: ## 更新 minor 版本 (1.0.0 -> 1.1.0)
	python scripts/bump_version.py minor

bump-major: ## 更新 major 版本 (1.0.0 -> 2.0.0)
	python scripts/bump_version.py major

release: ## 創建新的 release
	@echo "請選擇版本更新類型:"
	@echo "1. patch (1.0.0 -> 1.0.1)"
	@echo "2. minor (1.0.0 -> 1.1.0)"
	@echo "3. major (1.0.0 -> 2.0.0)"
	@read -p "請輸入選擇 (1-3): " choice; \
	case $$choice in \
		1) make bump-patch ;; \
		2) make bump-minor ;; \
		3) make bump-major ;; \
		*) echo "無效選擇"; exit 1 ;; \
	esac
	@echo "版本已更新，請執行以下命令:"
	@echo "git add ."
	@echo "git commit -m 'Bump version'"
	@echo "git tag v\$$(python -c 'import jwt_auth_middleware; print(jwt_auth_middleware.__version__)')"
	@echo "git push origin main --tags"

version: ## 顯示當前版本
	@python -c 'import jwt_auth_middleware; print(jwt_auth_middleware.__version__)' 