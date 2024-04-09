.PHONY: ci
ci: install

.PHONY: install
install:
	poetry install

format:
	poetry run black src
	poetry run ruff check src --fix-only --unsafe-fixes

.PHONY: lint
lint:
	# Python
	poetry run black src --check
	poetry run ruff check src
