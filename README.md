# C216 - Sistemas Distribuídos

Projeto das práticas da disciplina C216:

- **Backend** em FastAPI, com persistência em PostgreSQL via SQLAlchemy e migrations versionadas com Alembic;
- **Frontend** em React + Vite com Tailwind CSS: um gerenciador de itens (nome e descrição) que funciona apenas no navegador, sem chamadas ao backend.

## Requisitos

- Python 3.12+
- [Poetry](https://python-poetry.org/)
- Docker e Docker Compose (PostgreSQL)
- Node.js 22+ e npm (frontend)

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

O GitHub Actions do backend (workflow `.github/workflows/ci-backend.yml`) roda a cada `push` e `pull_request` com três jobs: lint (Ruff), testes unitários e testes de integração. Os testes rodam com um serviço PostgreSQL.

## Frontend

O frontend fica em `frontend/` e implementa um gerenciador de itens com nome e descrição. Os itens ficam apenas em memória no navegador: não há nenhuma chamada ao backend.

### Funcionalidades

- Cadastro, edição e remoção de itens;
- Validação no formulário:
  - nome obrigatório, entre 3 e 50 caracteres e sem repetir o nome de outro item (sem diferenciar maiúsculas);
  - descrição obrigatória, com até 200 caracteres;
  - os erros aparecem após a primeira tentativa de envio e somem assim que o campo é corrigido;
- Contador de caracteres e mensagens de erro ligadas aos campos (`aria-invalid` e `aria-describedby`);
- Layout responsivo com Tailwind CSS: formulário e lista lado a lado em telas médias e empilhados no celular.

### Stack

| Ferramenta                                                          | Uso                                         |
| ------------------------------------------------------------------- | ------------------------------------------- |
| [Vite](https://vite.dev/) + [React](https://react.dev/)             | Build e interface                           |
| [Tailwind CSS](https://tailwindcss.com/) (plugin `@tailwindcss/vite`) | Estilos                                    |
| [Biome](https://biomejs.dev/)                                       | Lint e formatação                           |
| [Vitest](https://vitest.dev/) + [Testing Library](https://testing-library.com/) | Testes unitários e de integração |
| [Playwright](https://playwright.dev/)                               | Testes E2E no navegador                     |

### Estrutura

```
frontend/
├── src/
│   ├── main.jsx              # Ponto de entrada, monta o App
│   ├── App.jsx               # Junta formulário e lista e controla o item em edição
│   ├── index.css             # Importa o Tailwind
│   ├── components/
│   │   ├── ItemForm.jsx      # Formulário de cadastro e edição com validação
│   │   ├── CampoTexto.jsx    # Campo com label, contador e mensagem de erro
│   │   ├── ItemList.jsx      # Lista de itens, contador e estado vazio
│   │   └── ItemCard.jsx      # Um item com as ações de editar e remover
│   ├── hooks/useItens.js     # Estado dos itens em memória
│   └── utils/
│       ├── validacao.js      # Regras de validação (funções puras)
│       └── itens.js          # Operações sobre a lista de itens (funções puras)
├── tests/
│   ├── unit/                 # Testes das funções de validacao.js e itens.js
│   └── integration/          # Testes do App renderizado, simulando o usuário
├── e2e/                      # Testes E2E com Playwright
├── biome.json
├── playwright.config.js
└── vite.config.js            # Configuração do Vite e do Vitest
```

### Executando

```bash
cd frontend
npm ci
npm run dev       # http://localhost:5173
```

Ou, a partir da raiz, `make front-install` e `make front-dev`.

### Qualidade e testes

```bash
npm run lint          # lint com o Biome
npm run format        # formata o código
npm run format:check  # apenas verifica a formatação (usado no CI)
npm test              # testes unitários e de integração (Vitest)
npm run test:unit
npm run test:integration
npm run build         # build de produção em dist/
npm run test:e2e      # testes E2E (Playwright)
```

Os testes seguem três níveis:

- **Unitários** (`tests/unit`): validam as regras de validação e as operações da lista isoladamente;
- **Integração** (`tests/integration`): renderizam o `App` em jsdom e simulam o usuário com `user-event` (cadastro, erros de validação, nome duplicado, edição, cancelamento e remoção). Um teste substitui o `fetch` por um mock e confirma que ele nunca é chamado;
- **E2E** (`e2e`): o Playwright gera o build, sobe o `vite preview` e executa o fluxo completo em um navegador desktop e em um celular emulado, verificando também que nenhuma requisição `fetch`/`xhr` é feita e que não há rolagem horizontal.

Na primeira execução dos testes E2E é preciso baixar o navegador:

```bash
npx playwright install chromium
```

Para rodar todo o checklist de entrega de uma vez, a partir da raiz:

```bash
make check-all   # npm ci, lint, format:check, test, build e test:e2e
```

O workflow `.github/workflows/ci-frontend.yml` roda a cada `push` e `pull_request` com dois jobs: um com lint, formatação, testes do Vitest e build, e outro com os testes E2E do Playwright, que publica o relatório como artefato.
