check_dirs := ko_lm_dataformat/ tests/
test_dirs := ko_lm_dataformat/

.PHONY: style
style:
	black $(check_dirs)
	isort $(check_dirs)
	flake8 $(check_dirs)

.PHONY: quality
quality:
	black --check $(check_dirs)
	isort --check-only $(check_dirs)
	flake8 $(check_dirs)

.PHONY: test
test:
	pytest

.PHONY: test-cov
test-cov:
	pytest --cov-branch --cov $(test_dirs)

.PHONY: build-remove
build-remove:
	rm -rf build/ dist/

.PHONY: pycache-remove
pycache-remove:
	find . | grep -E "(__pycache__|\.pyc|\.pyo$$)" | xargs rm -rf

.PHONY: clean-all
clean-all: pycache-remove build-remove
