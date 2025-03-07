.EXPORT_ALL_VARIABLES:

SHELL = /bin/bash
.SHELLFLAGS = -euo pipefail -c

.PHONY: $(MAKECMDGOALS)

PYTHON_VERSION = $(shell head -1 .python-version)
PYTHON_SRC = *.py src/ tests/

POETRY_DOCKER = docker run \
	--interactive \
	--rm \
	build:local poetry run

POETRY_DOCKER_MOUNT = docker run \
	--interactive \
	--rm \
	--volume "$(PWD)/prowler_scanner:/build/prowler_scanner:z" \
	--volume "$(PWD)/custom_checks:/build/custom_checks:z" \
	--volume "$(PWD)/tests:/build/tests:z" \
	build:local poetry run

python:
	docker build --target dev \
		--file Dockerfile \
		--build-arg PYTHON_VERSION=$(PYTHON_VERSION) \
		--tag build:local .

install-poetry:
	curl -sSL https://install.python-poetry.org | python -

init:
	@echo "if you do not have poetry installed please run 'make install-poetry'"
	poetry install
	poetry run pre-commit autoupdate

lint: python
	@$(POETRY_DOCKER) ruff check $(PYTHON_SRC)

fmt-check: python
	@$(POETRY_DOCKER_MOUNT) ruff format --check --line-length 120 $(PYTHON_SRC)

fmt: python
	@$(POETRY_DOCKER_MOUNT) ruff check --fix $(PYTHON_SRC)
	@$(POETRY_DOCKER_MOUNT) ruff format --line-length 120 $(PYTHON_SRC)

mypy: python
	@$(POETRY_DOCKER) mypy --strict $(PYTHON_SRC)

python-test: python
	@$(POETRY_DOCKER) pytest \
		-v \
		-p no:cacheprovider \
		--no-header \
		--cov=src \
		--cov-report "term-missing:skip-covered" \
		--no-cov-on-fail \
		--cov-fail-under=100

.PHONY: all-checks test
all-checks test: python-test lint fmt-check mypy md-check clean-up

REMARK_LINT_VERSION = 0.3.5
md-check:
	@docker run --pull missing --rm -i -v $(PWD):/lint/input:ro ghcr.io/zemanlx/remark-lint:${REMARK_LINT_VERSION} --frail .

# Update (to best of tools ability) md linter findings
.PHONY: md-fix
md-fix:
	@docker run --pull missing --rm -i -v $(PWD):/lint/input:rw ghcr.io/zemanlx/remark-lint:${REMARK_LINT_VERSION} . -o

container-release:
	docker build --target lambda \
		--file Dockerfile \
		--build-arg PYTHON_VERSION=$(PYTHON_VERSION) \
		--tag container-release:local .

.PHONY: clean-up
clean-up:
	@rm -f .coverage
	@rm -f coverage.xml
