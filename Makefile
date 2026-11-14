PYTHON      ?= python
POETRY      ?= poetry
BACKEND_DIR := backend
FRONTEND_DIR := frontend
NPM         ?= npm
APP         := app.main:app
HOST        ?= 0.0.0.0
PORT        ?= 8000

# Stack isolada usada pelos testes E2E: outro nome de projeto e outras portas,
# para não conflitar com o ambiente de desenvolvimento (make up).
E2E_PROJECT       := lab-e2e
E2E_COMPOSE       := docker compose -p $(E2E_PROJECT)
E2E_API_PORT      := 18000
E2E_FRONTEND_PORT := 15173
E2E_DB_PORT       := 55432

.DEFAULT_GOAL := help
.PHONY: help install run format lint test test-unit test-integration db migrate migration \
	docker-build up up-build ps down logs clean db-upgrade db-current \
	frontend-install frontend-dev frontend-check frontend-format frontend-test frontend-build \
	e2e e2e-up e2e-run e2e-down check-all

help:
	@echo Alvos disponiveis:
	@echo   help     Mostra esta mensagem
	@echo   install  Instala as dependencias com o poetry
	@echo   run      Sobe a API em http://$(HOST):$(PORT)
	@echo   format   Formata o codigo e corrige o lint com o Ruff
	@echo   lint     Verifica lint e formatacao com o Ruff
	@echo   test     Executa os testes automatizados com Pytest, subindo o banco antes
	@echo   test-unit         Executa apenas os testes unitarios
	@echo   test-integration  Executa apenas os testes de integracao, subindo o banco antes
	@echo   db       Sobe apenas o PostgreSQL com Docker Compose
	@echo   migrate  Aplica as migrations no banco local
	@echo   migration  Gera uma migration a partir dos modelos. Uso: make migration m=mensagem
	@echo   docker-build  Constroi as imagens da api e do frontend
	@echo   up       Sobe db, api e frontend com Docker Compose
	@echo   up-build Reconstroi as imagens e sobe db, api e frontend
	@echo   ps       Mostra o estado dos servicos do Docker Compose
	@echo   down     Para os servicos do Docker Compose
	@echo   logs     Exibe os logs da api e do frontend
	@echo   clean    Para os servicos e remove os volumes
	@echo   db-upgrade  Aplica as migrations no banco do container da api
	@echo   db-current  Mostra a revisao atual do banco do container da api
	@echo   frontend-install  Instala as dependencias do frontend com npm ci
	@echo   frontend-dev      Sobe o frontend em modo de desenvolvimento
	@echo   frontend-check    Verifica lint e formatacao do frontend com o Biome
	@echo   frontend-format   Formata o codigo do frontend com o Biome
	@echo   frontend-test     Executa os testes unitarios e de integracao do frontend
	@echo   frontend-build    Gera o build de producao do frontend
	@echo   e2e      Sobe a stack $(E2E_PROJECT), executa os testes E2E e remove os containers
	@echo   check-all  Executa o checklist completo: backend, frontend e E2E

install:
	cd $(BACKEND_DIR) && $(POETRY) install

run:
	cd $(BACKEND_DIR) && $(POETRY) run uvicorn $(APP) --host $(HOST) --port $(PORT) --reload

format:
	cd $(BACKEND_DIR) && $(POETRY) run ruff format . && $(POETRY) run ruff check --fix .

lint:
	cd $(BACKEND_DIR) && $(POETRY) run ruff check . && $(POETRY) run ruff format --check .

test: db
	cd $(BACKEND_DIR) && $(POETRY) run pytest

test-unit:
	cd $(BACKEND_DIR) && $(POETRY) run pytest -m unit

test-integration: db
	cd $(BACKEND_DIR) && $(POETRY) run pytest -m integration

db:
	docker compose up -d --wait db

migrate: db
	cd $(BACKEND_DIR) && $(POETRY) run alembic upgrade head

migration: db
	cd $(BACKEND_DIR) && $(POETRY) run alembic revision --autogenerate -m "$(m)"

docker-build:
	docker compose build api frontend

up:
	docker compose up -d --wait

up-build:
	docker compose up -d --build --wait

ps:
	docker compose ps

down:
	docker compose down

logs:
	docker compose logs -f api frontend

clean:
	docker compose down --volumes --remove-orphans

db-upgrade:
	docker compose exec api alembic upgrade head

db-current:
	docker compose exec api alembic current

frontend-install:
	cd $(FRONTEND_DIR) && $(NPM) ci

frontend-dev:
	cd $(FRONTEND_DIR) && $(NPM) run dev

frontend-check:
	cd $(FRONTEND_DIR) && $(NPM) run lint && $(NPM) run format:check

frontend-format:
	cd $(FRONTEND_DIR) && $(NPM) run format

frontend-test:
	cd $(FRONTEND_DIR) && $(NPM) test

frontend-build:
	cd $(FRONTEND_DIR) && $(NPM) run build

# Variáveis lidas pelo compose.yml e pelo playwright.config.js durante o E2E.
e2e e2e-up e2e-run e2e-down: export API_PORT := $(E2E_API_PORT)
e2e e2e-up e2e-run e2e-down: export FRONTEND_PORT := $(E2E_FRONTEND_PORT)
e2e e2e-up e2e-run e2e-down: export DB_PORT := $(E2E_DB_PORT)
e2e e2e-up e2e-run e2e-down: export VITE_API_URL := http://localhost:$(E2E_API_PORT)
e2e e2e-up e2e-run e2e-down: export CORS_ORIGINS := http://localhost:$(E2E_FRONTEND_PORT)
e2e e2e-up e2e-run e2e-down: export E2E_BASE_URL := http://localhost:$(E2E_FRONTEND_PORT)
e2e e2e-up e2e-run e2e-down: export E2E_API_URL := http://localhost:$(E2E_API_PORT)

# Remove a stack mesmo quando a subida ou os testes falham, sem deixar containers ativos.
e2e:
	$(MAKE) e2e-up || ($(MAKE) e2e-down && exit 1)
	$(MAKE) e2e-run || ($(MAKE) e2e-down && exit 1)
	$(MAKE) e2e-down

e2e-up:
	$(E2E_COMPOSE) up -d --build --wait

e2e-run:
	cd $(FRONTEND_DIR) && $(NPM) run test:e2e

e2e-down:
	$(E2E_COMPOSE) down --volumes --remove-orphans

check-all: lint test frontend-install frontend-check frontend-test frontend-build e2e
