.PHONY: all help install build release docs isort black mypy flake8 linting test coverage clean

all: install clean

help: ## Display this help screen
	@grep -E '^[a-zA-Z0-9_]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

install: ## Install a dependencies for development
	@pip install --requirement requirements-dev.txt --upgrade

build: ## Build a package
	@python -m build --sdist

release: dist/* ## Upload a package to the PyPI
	@twine check --strict $^
	@twine upload --disable-progress-bar $^

docs: ## Build a documentation
	@sphinx-build -aq docs public

isort: ## Run the isort utility
	@isort --check-only jsonrpc tests

black: ## Run the black utility
	@black --check jsonrpc tests

mypy: ## Run the mypy utility
	@mypy jsonrpc tests

flake8: ## Run the flake8 utility
	@flake8 jsonrpc tests

linting: isort black mypy flake8 ## Lint a whole project

test: ## Run the unit tests
	@coverage run -m pytest -xv --junit-xml=pytest.xml

coverage: test ## Report a coverage statistics
	@coverage report
	@coverage xml -qo coverage.xml

clean: ## Delete all temporary files
	@find jsonrpc tests -type f -name '*.py[cod]' -delete
	@find jsonrpc tests -type d -name '__pycache__' -delete
	@rm -rf *.egg *.egg-info build dist public
