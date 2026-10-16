# C216 - Sistemas Distribuídos

Backend em FastAPI para as práticas da disciplina C216, com persistência em PostgreSQL via SQLAlchemy e migrations versionadas com Alembic.

## Requisitos

- Python 3.12+
- [Poetry](https://python-poetry.org/)
- Docker e Docker Compose (PostgreSQL)

## Instalação

```bash
make install
```

## Configuração

A conexão com o banco é configurada pela variável de ambiente `DATABASE_URL` (lida em `app/core/config.py` com `pydantic-settings`). Sem ela, a aplicação usa o PostgreSQL do Docker Compose em `localhost:5432`. Para personalizar, copie `backend/.env.example` para `backend/.env`.

| Variável            | Padrão                                                     | Uso                                   |
| ------------------- | ---------------------------------------------------------- | ------------------------------------- |
| `DATABASE_URL`      | `postgresql+psycopg://c216:c216@localhost:5432/c216`       | Banco da aplicação e do Alembic       |
| `TEST_DATABASE_URL` | `postgresql+psycopg://c216:c216@localhost:5432/c216_test`  | Banco dos testes de integração        |
| `DB_PORT`           | `5432`                                                     | Porta do PostgreSQL exposta no host   |

## Executando a aplicação

Com Docker Compose (API + PostgreSQL). Ao iniciar, o container do backend aplica as migrations pendentes (`alembic upgrade head`) antes de subir a API:

```bash
make up-build   # reconstrói a imagem e sobe tudo
make up         # sobe sem reconstruir
make down       # para os serviços (os dados ficam no volume postgres_data)
make clean      # para os serviços e apaga o volume do banco
```

Localmente, fora do container:

```bash
make db        # sobe apenas o PostgreSQL
make migrate   # aplica as migrations
make run       # sobe a API com reload
```

A API sobe em `http://localhost:8000` e a documentação interativa (Swagger) fica em `http://localhost:8000/docs`.

## Estrutura do backend

```
backend/
├── app/
│   ├── main.py               # Cria a aplicação, registra routers e handlers de erro
│   ├── core/config.py        # Configurações lidas de variáveis de ambiente
│   ├── api/
│   │   ├── router.py         # Agrega os routers de cada recurso
│   │   ├── dependencies.py   # Monta sessão -> repository -> service (Depends)
│   │   ├── errors.py         # Converte exceções do service em respostas HTTP
│   │   └── routes/           # Endpoints HTTP de cada recurso
│   ├── schemas/              # Modelos Pydantic (entrada e saída da API)
│   ├── services/             # Regras de negócio, usam os repositories
│   ├── repositories/         # Acesso aos dados com SQLAlchemy
│   ├── models/               # Modelos ORM (tabelas)
│   └── database/             # Engine, sessão (get_db) e Base declarativa
├── alembic/
│   ├── env.py                # Lê DATABASE_URL e o metadata dos modelos
│   └── versions/             # Migrations
├── alembic.ini
├── tests/
└── pyproject.toml
```

Fluxo de uma requisição:

```
FastAPI (routes) -> Services -> Repositories -> SQLAlchemy -> PostgreSQL
                                                     ↑
                                    Alembic versiona a estrutura do banco
```

Os schemas Pydantic (`schemas/`) definem o contrato da API e ficam separados dos modelos ORM (`models/`), que definem as tabelas.

## Migrations

A migration inicial (`alembic/versions/2b6ce3ed2319_cria_tabela_tarefas.py`) cria a tabela `tarefas` e permite reproduzir a estrutura a partir de um banco vazio.

```bash
make migrate                          # alembic upgrade head
make migration m="descricao"          # gera uma migration a partir dos modelos (--autogenerate)
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

## Qualidade de código

O projeto usa o [Ruff](https://docs.astral.sh/ruff/) para lint e formatação:

```bash
make format   # formata e corrige o que for possível
make lint     # apenas verifica (usado no CI)
```

## Executando os testes

Os testes automatizados ficam em `backend/tests` e usam Pytest, separados em:

- `tests/unit`: testes unitários sem banco (schemas e service, este com um repositório falso em memória);
- `tests/integration`: testes que usam o PostgreSQL real: endpoints via `TestClient`, repository e migrations.

Cada teste recebe automaticamente o marker `unit` ou `integration` de acordo com a pasta.

Os testes de integração usam um banco separado, `c216_test` (criado automaticamente se não existir), para não apagar os dados da aplicação. A estrutura é criada pelas próprias migrations do Alembic e a tabela é limpa entre um teste e outro.

```bash
make test               # todos os testes (sobe o PostgreSQL antes)
make test-unit          # apenas os unitários (não precisam do banco)
make test-integration   # apenas os de integração (sobe o PostgreSQL antes)
```

Se a porta 5432 já estiver em uso na sua máquina, exporte outra porta e aponte os testes para ela:

```bash
export DB_PORT=5433
export TEST_DATABASE_URL=postgresql+psycopg://c216:c216@localhost:5433/c216_test
make test
```

O GitHub Actions (workflow `.github/workflows/ci-backend.yml`) roda a cada `push` e `pull_request` com três jobs: lint (Ruff), testes unitários e testes de integração. Os testes rodam com um serviço PostgreSQL.
