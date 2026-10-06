PYTHON      ?= python
POETRY      ?= poetry
BACKEND_DIR := backend
APP         := app.main:app
HOST        ?= 0.0.0.0
PORT        ?= 8000
.DEFAULT_GOAL := help
.PHONY: help install run test test-unit test-integration docker-build up down logs clean
help:
	@echo Alvos disponiveis:
	@echo   help     Mostra esta mensagem
	@echo   install  Instala as dependencias com o poetry
	@echo   run      Sobe a API em http://$(HOST):$(PORT)
	@echo   test     Executa os testes automatizados com Pytest
	@echo   test-unit         Executa apenas os testes unitarios
	@echo   test-integration  Executa apenas os testes de integracao
	@echo   docker-build  Constroi a imagem do backend
	@echo   up       Sobe o backend e o banco com Docker Compose
	@echo   down     Para os servicos do Docker Compose
	@echo   logs     Exibe os logs do backend
	@echo   clean    Para os servicos e remove os volumes

install:
	cd $(BACKEND_DIR) && $(POETRY) install

run:
	cd $(BACKEND_DIR) && $(POETRY) run uvicorn $(APP) --host $(HOST) --port $(PORT) --reload

test:
	cd $(BACKEND_DIR) && $(POETRY) run pytest

test-unit:
	cd $(BACKEND_DIR) && $(POETRY) run pytest -m unit

test-integration:
	cd $(BACKEND_DIR) && $(POETRY) run pytest -m integration

docker-build:
	docker compose build backend

up:
	docker compose up -d

down:
	docker compose down

logs:
	docker compose logs -f backend

clean:
	docker compose down --volumes --remove-orphans
