DOCKER = docker run \
	--interactive \
	--rm \
	--env "PYTHONWARNINGS=ignore:ResourceWarning" \
	--volume "$(PWD):${PWD}" \
	--workdir "${PWD}"
PYTHON_COVERAGE_FAIL_UNDER_PERCENT = 100
PYTHON_VERSION = $(shell head -1 .python-version)
SHELL := /bin/bash

.PHONY: pipenv
pipenv:
	docker build \
		--tag $@ \
		--build-arg PYTHON_VERSION=$(PYTHON_VERSION) \
		--build-arg "user_id=$(shell id -u)" \
		--build-arg "group_id=$(shell id -g)" \
		--build-arg "home=${HOME}" \
		--build-arg "workdir=${PWD}" \
		--target $@ .

.PHONY: fmt
fmt: pipenv
	@$(DOCKER) pipenv run black --line-length=120 .

.PHONY: fmt-check
fmt-check: pipenv
	@$(DOCKER) pipenv run black --line-length=120 --check .

.PHONY: static-check
static-check: pipenv
	$(DOCKER) pipenv run flake8 --max-line-length=120 --max-complexity=10
	$(DOCKER) pipenv run mypy --show-error-codes --namespace-packages --strict ./**/*.py

.PHONY: all-checks test
all-checks test: python-test fmt-check static-check md-check clean-up

.PHONY: python-test
python-test: pipenv
	$(DOCKER) pipenv run pytest \
		--cov=src \
		--cov-fail-under=$(PYTHON_COVERAGE_FAIL_UNDER_PERCENT) \
		--no-cov-on-fail \
		--cov-report "term-missing:skip-covered" \
		--no-header \
		tests

.PHONY: md-check
md-check:
	@docker pull zemanlx/remark-lint:0.2.0
	@docker run --rm -i -v $(PWD):/lint/input:ro zemanlx/remark-lint:0.2.0 --frail .

.PHONY: build-lambda-image
build-lambda-image:
	@docker build \
		--file lambda.Dockerfile \
		--tag platsec_compliance_alerting_lambda:local . \
		--build-arg PYTHON_VERSION=$(PYTHON_VERSION) \
		>/dev/null

.PHONY: push-lambda-image
push-lambda-image: build-lambda-image
	@aws --profile $(ROLE) ecr get-login-password | docker login --username AWS --password-stdin $(ECR)
	@docker tag  platsec_compliance_alerting_lambda:local $(ECR)/platsec-compliance-alerting:latest
	@docker push $(ECR)/platsec-compliance-alerting:latest

.PHONY: clean-up
clean-up:
	@rm -f .coverage
	@rm -f coverage.xml
