.PHONY: help up down logs build test test-api dev api-dev migrate revision docker-up docker-down

COMPOSE   = docker compose -f deploy/docker-compose/docker-compose.yml
API_DIR   = apps/api
PYTHON    = $(API_DIR)/.venv/bin/python
ALEMBIC   = $(API_DIR)/.venv/bin/alembic

help:
	@echo "DevOpsLedger"
	@echo ""
	@echo "  up / docker-up     Start all services (Docker Compose)"
	@echo "  down / docker-down Stop all services"
	@echo "  logs               Tail service logs"
	@echo "  build              Build all Docker images"
	@echo "  test               Run all tests"
	@echo "  test-api           Run API tests only"
	@echo "  dev / api-dev      Start API locally with hot-reload"
	@echo "  migrate            Run pending Alembic migrations"
	@echo "  revision           Create new migration: make revision message=\"add foo\""

up docker-up:
	$(COMPOSE) up -d

down docker-down:
	$(COMPOSE) down

logs:
	$(COMPOSE) logs -f

build:
	$(COMPOSE) build

test: test-api

test-api:
	cd $(API_DIR) && python -m pytest tests/ -v

dev api-dev:
	cd $(API_DIR) && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

migrate:
	cd $(API_DIR) && python -m alembic upgrade head

revision:
	cd $(API_DIR) && python -m alembic revision --autogenerate -m "$(message)"
