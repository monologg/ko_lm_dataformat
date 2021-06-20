.PHONY: style quality test

check_dirs := ko_lm_dataformat/ tests/
test_dirs := ko_lm_dataformat/

style:
	black $(check_dirs)
	isort $(check_dirs)
	flake8 $(check_dirs)

quality:
	black --check $(check_dirs)
	isort --check-only $(check_dirs)
	flake8 $(check_dirs)

test:
	pytest

test-cov:
	pytest --cov-branch --cov $(test_dirs)