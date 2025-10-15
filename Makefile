clean: clean-pyc clean-test clean-uv clean-lint-and-formatter
quality: set-style-dep check-quality
style: set-style-dep set-style
setup: set-git set-dev set-style-dep set-test-dep set-precommit
test: set-test-dep set-test


##### basic #####
set-git:
	git config --local commit.template .gitmessage

set-style-dep:
	uv sync --only-group quality --frozen --no-install-project --inexact

set-test-dep:
	uv sync --only-group test --frozen --no-install-project --inexact

set-precommit:
	uv run --frozen pre-commit install

set-dev:
	uv sync --frozen --no-install-project

set-test:
	uv run --frozen --only-group test pytest --force-sugar --memray tests/

set-style:
	uv run --frozen --only-group quality ruff check --fix .
	uv run --frozen --only-group quality ruff format .

check-quality:
	uv run --frozen --only-group quality ruff check .
	uv run --frozen --only-group quality ruff format --check .

check-lock:
	uv lock --check

#####  clean  #####
clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-test:
	rm -f .coverage
	rm -f .coverage.*
	rm -rf .pytest_cache
	rm -rf .mypy_cache

clean-lint-and-formatter:
	rm -rf .ruff_cache

clean-uv:
	uv cache clean
	uv cache prune
