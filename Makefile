.PHONY: help up down logs build test test-api dev

COMPOSE = docker compose -f deploy/docker-compose/docker-compose.yml

help:
	@echo "DevOpsLedger"
	@echo ""
	@echo "  up        Start all services (Docker Compose)"
	@echo "  down      Stop all services"
	@echo "  logs      Tail service logs"
	@echo "  build     Build all Docker images"
	@echo "  test      Run all tests"
	@echo "  test-api  Run API tests only"
	@echo "  dev       Start API locally with hot-reload"

up:
	$(COMPOSE) up -d

down:
	$(COMPOSE) down

logs:
	$(COMPOSE) logs -f

build:
	$(COMPOSE) build

test: test-api

test-api:
	cd apps/api && python -m pytest tests/ -v

dev:
	cd apps/api && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
