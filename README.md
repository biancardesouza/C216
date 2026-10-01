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

A documentação interativa (Swagger) fica em `http://localhost:8000/docs`.

## Estrutura do backend

```
backend/app/
├── main.py                 # Apenas cria a aplicação e registra os routers
├── core/config.py          # Configurações da aplicação
├── api/
│   ├── router.py           # Agrega os routers de cada recurso
│   ├── dependencies.py     # Dependências injetadas nas rotas (Depends)
│   └── routes/             # Endpoints HTTP de cada recurso
├── schemas/                # Modelos Pydantic (entrada e saída)
└── repositories/           # Acesso aos dados (em memória)
```

## Endpoints

| Método | Rota                    | Descrição                                                      |
| ------ | ----------------------- | -------------------------------------------------------------- |
| GET    | `/`                     | Health check                                                   |
| GET    | `/tarefas`              | Lista tarefas (query: `concluida`, `offset`, `limit`)          |
| GET    | `/tarefas/{tarefa_id}`  | Busca uma tarefa                                               |
| POST   | `/tarefas`              | Cria uma tarefa                                                |
| PUT    | `/tarefas/{tarefa_id}`  | Substitui todos os campos de uma tarefa                        |
| PATCH  | `/tarefas/{tarefa_id}`  | Atualiza apenas os campos enviados                             |
| DELETE | `/tarefas/{tarefa_id}`  | Remove uma tarefa                                              |

## Executando os testes

Os testes automatizados ficam em `backend/tests` e usam Pytest, separados em:

- `tests/unit`: testes unitários das camadas isoladas (schemas e repositório), sem HTTP;
- `tests/integration`: testes de integração que exercitam todos os endpoints via `TestClient`.

Cada teste recebe automaticamente o marker `unit` ou `integration` de acordo com a pasta.

```bash
make test               # todos os testes
make test-unit          # apenas os unitários
make test-integration   # apenas os de integração
```

Os testes também são executados automaticamente pelo GitHub Actions (workflow `.github/workflows/ci-backend.yml`) a cada `push` e `pull_request`, com um job para cada tipo de teste.
