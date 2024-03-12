.DEFAULT_GOAL := help

.PHONY: help
help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

.PHONY: clean
clean: clean_pyc ## Clean all PYC in the system

.PHONY: clean_pyc
clean_pyc: ## Cleans all *.pyc in the system
	find . -type f -name "*.pyc" -delete || true

.PHONY: clean_pycache
clean_pycache: ## Removes the __pycaches__
	find . -type d -name "*__pycache__*" -delete

.PHONY: serve-docs
serve-docs: ## Runs the local docs
	mike serve

.PHONY: build-docs
build-docs: ## Runs the local docs
	mkdocs build

.PHONY: test
test: ## Runs the tests
	ESMERALD_SETTINGS_MODULE='tests.settings.TestSettings' pytest $(TESTONLY) --disable-pytest-warnings -s -vv

.PHONY: coverage
coverage: ## Run tests and coverage
	ESMERALD_SETTINGS_MODULE='tests.settings.TestSettings' pytest --cov=esmerald --cov=tests --cov-report=term-missing:skip-covered --cov-report=html tests

# .PHONY: cov
# cov: ## Run tests and coverage only for specific ones
# 	ESMERALD_SETTINGS_MODULE='tests.settings.TestSettings' pytest --cov=esmerald --cov=${ONLY} --cov-report=term-missing:skip-covered --cov-report=html ${ONLY}

.PHONY: cov
cov: ## Run tests and coverage only for specific ones
	ESMERALD_SETTINGS_MODULE='tests.settings.TestSettings' coverage run -m pytest tests
	ESMERALD_SETTINGS_MODULE='tests.settings.TestSettings' coverage combine
	ESMERALD_SETTINGS_MODULE='tests.settings.TestSettings' coverage report --show-missing
	ESMERALD_SETTINGS_MODULE='tests.settings.TestSettings' coverage html


.PHONY: requirements
requirements: ## Install requirements for development
	pip install -e .[dev,test,doc,templates,jwt,encoders,schedulers,ipython,ptpython]


ifndef VERBOSE
.SILENT:
endif
