SHELL := /bin/bash
PYTHON_COVERAGE_FAIL_UNDER_PERCENT = 100
PYTHON_VERSION = $(shell head -1 .python-version)
PIP_PIPENV_VERSION = $(shell head -1 .pipenv-version)
GROUP_ID ?= $(shell id -g)
USER_ID ?= $(shell id -u)
PYTHON_SRC = *.py src/ tests/
PROJECT_ROOT = $(PWD)

ifdef CI_MODE
	DOCKER = docker build \
		--target dev \
		--file lambda.Dockerfile \
		--tag test-run:ci . \
		--build-arg PYTHON_VERSION=$(PYTHON_VERSION) \
		--build-arg PIP_PIPENV_VERSION=$(PIP_PIPENV_VERSION) \
		&& docker run test-run:ci
else
	DOCKER = docker build \
		--file Dockerfile \
                --build-arg PYTHON_VERSION=$(PYTHON_VERSION) \
                --build-arg PIP_PIPENV_VERSION=$(PIP_PIPENV_VERSION) \
                --build-arg "user_id=${USER_ID}" \
                --build-arg "group_id=${GROUP_ID}" \
                --build-arg "home=${HOME}" \
                --build-arg "workdir=${PWD}" \
		--tag test-run:local . \
		&& docker run \
		--interactive \
		--rm \
		--env "PYTHONWARNINGS=ignore:ResourceWarning" \
		--volume "$(PWD):${PWD}:z" \
		--workdir "${PWD}" \
		test-run:local
endif

.PHONY: fmt
fmt:
	@$(DOCKER) pipenv run black --line-length=120 $(PYTHON_SRC)

.PHONY:
fmt-check:
	@$(DOCKER) pipenv run black --line-length=120 --check $(PYTHON_SRC)

.PHONY: static-check
static-check:
	$(DOCKER) pipenv run flake8 --max-line-length=120 --max-complexity=10 $(PYTHON_SRC)
	$(DOCKER) pipenv run mypy --show-error-codes --namespace-packages --strict $(PYTHON_SRC)

.PHONY: all-checks test
all-checks test: python-test fmt-check static-check md-check clean-up

.PHONY: python-test
python-test:
	$(DOCKER) pipenv run pytest \
		--cov=src \
		--cov-fail-under=$(PYTHON_COVERAGE_FAIL_UNDER_PERCENT) \
		--no-cov-on-fail \
		--cov-report "term-missing:skip-covered" \
		--no-header \
		tests

REMARK_LINT_VERSION = 0.3.5
md-check:
	@docker run --pull missing --rm -i -v $(PWD):/lint/input:ro ghcr.io/zemanlx/remark-lint:${REMARK_LINT_VERSION} --frail .

# Update (to best of tools ability) md linter findings
.PHONY: md-fix
md-fix:
	@docker run --pull missing --rm -i -v $(PWD):/lint/input:rw ghcr.io/zemanlx/remark-lint:${REMARK_LINT_VERSION} . -o

container-release:
	docker build \
		--file lambda.Dockerfile \
		--tag container-release:local . \
		--build-arg PYTHON_VERSION=$(PYTHON_VERSION) \
		--build-arg PIP_PIPENV_VERSION=$(PIP_PIPENV_VERSION)

.PHONY: clean-up
clean-up:
	@rm -f .coverage
	@rm -f coverage.xml
