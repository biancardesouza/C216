PYTHON      ?= python
POETRY      ?= poetry
BACKEND_DIR := backend
FRONTEND_DIR := frontend
NPM         ?= npm
APP         := app.main:app
HOST        ?= 0.0.0.0
PORT        ?= 8000
.DEFAULT_GOAL := help
.PHONY: help install run format lint test test-unit test-integration db migrate migration docker-build up up-build down logs clean front-install front-dev front-lint front-format front-test front-build front-e2e check-all
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
	@echo   docker-build  Constroi a imagem do backend
	@echo   up       Sobe o backend e o banco com Docker Compose
	@echo   up-build Reconstroi a imagem e sobe o backend e o banco
	@echo   down     Para os servicos do Docker Compose
	@echo   logs     Exibe os logs do backend
	@echo   clean    Para os servicos e remove os volumes
	@echo   front-install  Instala as dependencias do frontend com npm ci
	@echo   front-dev      Sobe o frontend em modo de desenvolvimento
	@echo   front-lint     Verifica lint e formatacao do frontend com o Biome
	@echo   front-format   Formata o codigo do frontend com o Biome
	@echo   front-test     Executa os testes unitarios e de integracao do frontend
	@echo   front-build    Gera o build de producao do frontend
	@echo   front-e2e      Executa os testes E2E do frontend com o Playwright
	@echo   check-all      Executa todo o checklist do frontend: install, lint, format, test, build e e2e

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
	docker compose build backend

up:
	docker compose up -d

up-build:
	docker compose up -d --build

down:
	docker compose down

logs:
	docker compose logs -f backend

clean:
	docker compose down --volumes --remove-orphans

front-install:
	cd $(FRONTEND_DIR) && $(NPM) ci

front-dev:
	cd $(FRONTEND_DIR) && $(NPM) run dev

front-lint:
	cd $(FRONTEND_DIR) && $(NPM) run lint && $(NPM) run format:check

front-format:
	cd $(FRONTEND_DIR) && $(NPM) run format

front-test:
	cd $(FRONTEND_DIR) && $(NPM) test

front-build:
	cd $(FRONTEND_DIR) && $(NPM) run build

front-e2e:
	cd $(FRONTEND_DIR) && $(NPM) run test:e2e

check-all: front-install front-lint front-test front-build front-e2e
