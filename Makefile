ifneq (,$(wildcard ./${ENV}))
    include ${ENV}
    export
endif

# Docker configurations
DC = docker compose
ENV = --env-file .env

# Docker Compose files
LOCAL_DB_FILE = docker_compose/storages.yaml

.DEFAULT_GOAL := help


.PHONY: linting  ## Check linting
linting:
	ruff check .
	ruff format .


.PHONY: run-bot  ## Run bot
run-bot:
	python -m bot.bot


.PHONY: run-bot  ## Run app
run-app:
	python -m app.main


.PHONY: migrate-apply  ## Apply all pending Alembic migrations
migrate-apply:
	alembic upgrade head


.PHONY: local-up  ## Start local storage services in detached mode
local-up:
	${DC} -f ${LOCAL_DB_FILE} ${ENV} up -d


.PHONY: local-down  ## Stop local storage services
local-down:
	${DC} -f ${LOCAL_DB_FILE} ${ENV} down


.PHONY: local-clear  ## Stop local storage services and clear volumes
local-clear:
	${DC} -f ${LOCAL_DB_FILE} ${ENV} down --volumes


.PHONY: help  ## Show this help message
help:
	@echo "Usage: make [command]"
	@echo ""
	@echo "Commands:"
	@grep -E \
		'^.PHONY: .*?## .*$$' $(MAKEFILE_LIST) | \
		sort | \
		awk 'BEGIN {FS = ".PHONY: |## "}; {printf "\033[36m%-19s\033[0m %s\n", $$2, $$3}'
