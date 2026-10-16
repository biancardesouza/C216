PYTHON      ?= python
POETRY      ?= poetry
BACKEND_DIR := backend
APP         := app.main:app
HOST        ?= 0.0.0.0
PORT        ?= 8000
.DEFAULT_GOAL := help
.PHONY: help install run format lint test test-unit test-integration db migrate migration docker-build up up-build down logs clean
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
