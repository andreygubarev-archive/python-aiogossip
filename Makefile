MAKEFILE_DIR := $(realpath $(dir $(firstword $(MAKEFILE_LIST))))

.PHONY: help
help: ## Show this help
	@egrep -h '\s##\s' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

.PHONY: format
format: ## Format Python Package
	python -m isort .
	python -m black .

.PHONY: lint
lint: ## Lint Python Package
	python -m flake8

.PHONY: test
test: ## Test Python Package
ifeq ($(MODULE),)
	python -m pytest --pdb
else
	python -m pytest --pdb --no-cov $(MAKEFILE_DIR)/tests/test_$(MODULE).py
endif

.PHONY: run
run: ## Run Python Package
	bash tests/test_orchestrator.sh

.PHONY: build
build: ## Build Python Package
	python -m build --sdist --wheel

.PHONY: install
install: ## Install Python Package
	python -m pip install -e .

.PHONY: clean
clean: ## Clean Python Package
	git clean -fdX
