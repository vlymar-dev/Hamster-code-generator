ifneq (,$(wildcard ./${ENV}))
    include ${ENV}
    export
endif

# Docker configurations
DC = docker compose
ENV = --env-file .env

# Docker Compose files
LOCAL_DB_FILE = docker_compose/local.yaml
SERVICES_FILE = docker_compose/docker-compose.services.yaml
STORAGES_FILE = docker_compose/docker-compose.storages.yaml

# Babel
MESSAGES_FILE = bot/locales/messages.pot

.DEFAULT_GOAL := help


.PHONY: run-main  ## Run the main application (bot, keygen, or both) via main.py
run-main:
	python main.py


.PHONY: prod-build  ## Build and start production services with Docker Compose
prod-build:
	${DC} -f ${STORAGES_FILE} -f ${SERVICES_FILE} ${ENV} up -d --build

.PHONY: prod-up  ## Start production services without rebuilding
prod-up:
	${DC} -f ${STORAGES_FILE} -f ${SERVICES_FILE} ${ENV} up -d

.PHONY: prod-down  ## Stop production services
prod-down:
	${DC} -f ${STORAGES_FILE} -f ${SERVICES_FILE} ${ENV} down

.PHONY: prod-clear-all  ## Stop and remove production services, including volumes and orphaned containers
prod-clear-all:
	${DC} -f ${STORAGES_FILE} -f ${SERVICES_FILE} ${ENV} down --volumes --remove-orphans


.PHONY: lint  ## Run code quality checks: ruff linting, formatting and pre-commit hooks
lint:
	ruff format .
	ruff check . --fix
	pre-commit run --all-files


.PHONY: tests-run  ## Run the tests with coverage (optionally generate an HTML report if HTML=true is passed)
tests-run:
	if [ "$(HTML)" = "true" ]; then \
		pytest --cov --cov-report=html:hamster_cov; \
	else \
		pytest --cov; \
	fi


.PHONY: babel-input  ## Extract translatable strings into messages.pot
babel-input:
	pybabel extract --input-dirs=. -o ${MESSAGES_FILE}

.PHONY: babel-init  ## Initialize new language catalog, e.g. make babel-init LANG=fr
babel-init:
ifndef LANG
	$(error LANG is not set. Usage: make babel-init LANG=fr)
endif
	pybabel init -i ${MESSAGES_FILE} -d bot/locales -D messages -l $(LANG)

.PHONY: babel-update  ## Update all language catalogs with new messages
babel-update:
	pybabel update -i ${MESSAGES_FILE} -d bot/locales -D messages

.PHONY: babel-compile  ## Compile translation files to MO format
babel-compile:
	pybabel compile -d bot/locales -D messages


.PHONY: migrate-apply  ## Apply all pending database migrations using Alembic
migrate-apply:
	alembic upgrade head


.PHONY: services-up  ## Start all application services (bot, databases with migrations (without app)!)
services-up:
	${DC} -f ${STORAGES_FILE} -f ${SERVICES_FILE} ${ENV} up -d postgres redis migrate bot

.PHONY: services-down  ## Stop all application services
services-down:
	${DC} -f ${STORAGES_FILE} -f ${SERVICES_FILE} ${ENV} down

.PHONY: storages-clear  ## Completely remove storage containers and volumes (warning: deletes all data)
storages-clear:
	${DC} -f ${STORAGES_FILE} ${ENV} down --volumes --remove-orphans


.PHONY: local-up  ## Start local development databases (Postgres, Redis) in detached mode
local-up:
	${DC} -f ${LOCAL_DB_FILE} ${ENV} up -d

.PHONY: local-down  ## Stop local development databases
local-down:
	${DC} -f ${LOCAL_DB_FILE} ${ENV} down


.PHONY: help  ## Display this help message with all available commands
help:
	@echo "Usage: make [command]"
	@echo ""
	@echo "Commands:"
	@grep -E \
		'^.PHONY: .*?## .*$$' $(MAKEFILE_LIST) | \
		sort | \
		awk 'BEGIN {FS = ".PHONY: |## "}; {printf "\033[36m%-19s\033[0m %s\n", $$2, $$3}'
