# C216 - Sistemas Distribuídos

Backend em FastAPI para as práticas da disciplina C216.

## Requisitos

- Python 3.12+
- [Poetry](https://python-poetry.org/)
- Docker e Docker Compose (para subir a aplicação com o banco de dados)

## Instalação

```bash
make install
```

## Executando a aplicação

```bash
make run
```

A API sobe em `http://localhost:8000`.

Para subir a aplicação junto com o banco de dados via Docker Compose:

```bash
make up
```

## Executando os testes

Os testes automatizados ficam em `backend/tests` e usam Pytest.

```bash
make test
```

Esse comando equivale a rodar `poetry run pytest` dentro da pasta `backend`.

Os testes também são executados automaticamente pelo GitHub Actions (workflow `.github/workflows/ci-backend.yml`) a cada `push` e `pull_request`.
