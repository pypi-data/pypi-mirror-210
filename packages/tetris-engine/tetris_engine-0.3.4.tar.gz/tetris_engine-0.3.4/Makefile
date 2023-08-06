.DEFAULT_GOAL := help
.SILENT: help
.PHONY: help build


help: ## Show a list of available commands
	grep "##.*" $(MAKEFILE_LIST) | grep -v ".*MAKEFILE_LIST.*" | sed -E "s/:.*##/:/g" | column -t -s :


build-lib-darwin: ## Build the rust library for macOS
	cargo build --lib --target x86_64-apple-darwin --package tetris_engine_backend

rustup-list-targets: ## List available rustup targets
	rustup target list
	# rustup target add <specific target from list>

build-python-linux: ## Build the python package for a particular platform
	# https://cibuildwheel.readthedocs.io/en/stable/setup/
	# pip install cibuildwheel
	cibuildwheel --platform linux

build-bin-darwin: ## Build the rust binary app for macOS
	cargo build --bin tetris_engine_backend --target x86_64-apple-drawin --package tetris_engine_backend

test-rust: ## Run the rust unit tests
	cargo test --lib --package=tetris_engine_backend

test-python: ## Run the python unit tests
	python setup.py install
	python -m pytest --log-cli-level=DEBUG -s tests/

bumpversion: ## Increment the package version
	# pip install -r requirements.txt -r requirements-test.txt
	read -p "Enter the new version: " new_version && \
		bumpversion --new-version $$new_version --allow-dirty --no-commit --tag \
		pyproject.toml \
		tetris_engine/__init__.py \
		.bumpversion.cfg