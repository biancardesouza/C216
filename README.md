# C216 - Sistemas Distribuídos

Projeto das práticas da disciplina C216:

- **Backend** em FastAPI, com persistência em PostgreSQL via SQLAlchemy e migrations versionadas com Alembic;
- **Frontend** em React + Vite com Tailwind CSS: um gerenciador de itens (nome e descrição) que consome a API REST do backend;
- **Docker Compose** com os serviços `db`, `api` e `frontend`, e testes automatizados em todas as camadas (Pytest, Vitest e Playwright).

```
Navegador (localhost:5173) --fetch + CORS--> API FastAPI (localhost:8000) --SQLAlchemy--> PostgreSQL
        frontend (Nginx)                              api                                   db
```

## Requisitos

- Python 3.12+
- [Poetry](https://python-poetry.org/)
- Docker e Docker Compose
- Node.js 22+ e npm (frontend)

## Instalação

```bash
make install           # dependências do backend
make frontend-install  # dependências do frontend
```

## Configuração

O backend lê as configurações de variáveis de ambiente (`app/core/config.py`, com `pydantic-settings`). Para personalizar a execução local, copie `backend/.env.example` para `backend/.env`.

| Variável            | Padrão                                                     | Uso                                                       |
| ------------------- | ---------------------------------------------------------- | --------------------------------------------------------- |
| `DATABASE_URL`      | `postgresql+psycopg://c216:c216@localhost:5432/c216`       | Banco da aplicação e do Alembic                           |
| `CORS_ORIGINS`      | `http://localhost:5173,http://127.0.0.1:5173`              | Origens que o navegador pode usar para chamar a API       |
| `TEST_DATABASE_URL` | `postgresql+psycopg://c216:c216@localhost:5432/c216_test`  | Banco dos testes de integração                            |
| `DB_PORT`           | `5432`                                                     | Porta do PostgreSQL exposta no host                       |
| `API_PORT`          | `8000`                                                     | Porta da API exposta no host                              |
| `FRONTEND_PORT`     | `5173`                                                     | Porta do frontend exposta no host                         |
| `VITE_API_URL`      | `http://localhost:8000`                                    | Endereço da API usado pelo frontend (definido no build)   |

### CORS

O frontend (`localhost:5173`) e a API (`localhost:8000`) estão em origens diferentes, então o navegador só entrega as respostas da API se ela devolver o cabeçalho `Access-Control-Allow-Origin`. O `CORSMiddleware` do FastAPI (`app/main.py`) libera apenas as origens listadas em `CORS_ORIGINS`, nunca `*`, e apenas os métodos e cabeçalhos usados pelo frontend.

Como o `POST` envia JSON (`Content-Type: application/json`), o navegador faz antes uma requisição `OPTIONS` (preflight). Na aba *Network* aparecem o `OPTIONS` e o `POST /items/`, ambos com `access-control-allow-origin: http://localhost:5173`.

## Executando a aplicação

Com Docker Compose (`compose.yml`), sobem os três serviços, cada um com healthcheck. Ao iniciar, o container da `api` aplica as migrations pendentes (`alembic upgrade head`) antes de subir o servidor:

```bash
make up-build     # reconstrói as imagens e sobe db, api e frontend (espera todos ficarem healthy)
make ps           # estado dos serviços
make db-upgrade   # aplica as migrations no banco, pelo container da api
make db-current   # mostra a revisão atual do banco (deve terminar com "(head)")
make logs         # logs da api e do frontend
make down         # para os serviços (os dados ficam no volume postgres_data)
make clean        # para os serviços e apaga o volume do banco
```

| Serviço    | Endereço                       |
| ---------- | ------------------------------ |
| `frontend` | http://localhost:5173          |
| `api`      | http://localhost:8000 (Swagger em http://localhost:8000/docs) |
| `db`       | `localhost:5432`               |

Localmente, fora dos containers:

```bash
make db        # sobe apenas o PostgreSQL
make migrate   # aplica as migrations
make run       # sobe a API com reload
make frontend-dev  # sobe o Vite em http://localhost:5173
```

## Estrutura do backend

```
backend/
├── app/
│   ├── main.py               # Cria a aplicação, configura o CORS, registra routers e handlers de erro
│   ├── core/config.py        # Configurações lidas de variáveis de ambiente
│   ├── api/
│   │   ├── router.py         # Agrega os routers de cada recurso
│   │   ├── dependencies.py   # Monta sessão -> repository -> service (Depends)
│   │   ├── errors.py         # Converte exceções do service em respostas HTTP (404, 409)
│   │   └── routes/           # Endpoints HTTP de cada recurso (tarefas e items)
│   ├── schemas/              # Modelos Pydantic (entrada e saída da API)
│   ├── services/             # Regras de negócio, usam os repositories
│   ├── repositories/         # Acesso aos dados com SQLAlchemy
│   ├── models/               # Modelos ORM (tabelas)
│   └── database/             # Engine, sessão (get_db) e Base declarativa
├── alembic/
│   ├── env.py                # Lê DATABASE_URL e o metadata dos modelos
│   └── versions/             # Migrations
├── alembic.ini
├── Dockerfile
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

| Migration                                   | O que faz                                                                 |
| ------------------------------------------- | ------------------------------------------------------------------------- |
| `2b6ce3ed2319_cria_tabela_tarefas.py`       | Cria a tabela `tarefas`                                                   |
| `7c3f9a1d2e4b_cria_tabela_items.py`         | Cria a tabela `items` e o índice único `lower(nome)` (nome sem repetição) |

```bash
make migrate                          # alembic upgrade head (banco local)
make db-upgrade                       # alembic upgrade head (container da api)
make db-current                       # alembic current (container da api)
make migration m="descricao"          # gera uma migration a partir dos modelos (--autogenerate)
```

## Endpoints

| Método | Rota                    | Descrição                                                      |
| ------ | ----------------------- | -------------------------------------------------------------- |
| GET    | `/`                     | Health check                                                   |
| GET    | `/items/`               | Lista os itens, ordenados por id                               |
| GET    | `/items/{item_id}`      | Busca um item                                                  |
| POST   | `/items/`               | Cria um item (`409` se o nome já existir)                      |
| PUT    | `/items/{item_id}`      | Atualiza nome e descrição (`409` se o nome for de outro item)  |
| DELETE | `/items/{item_id}`      | Remove um item                                                 |
| GET    | `/tarefas`              | Lista tarefas (query: `concluida`, `offset`, `limit`)          |
| GET    | `/tarefas/{tarefa_id}`  | Busca uma tarefa                                               |
| POST   | `/tarefas`              | Cria uma tarefa                                                |
| PUT    | `/tarefas/{tarefa_id}`  | Substitui todos os campos de uma tarefa                        |
| PATCH  | `/tarefas/{tarefa_id}`  | Atualiza apenas os campos enviados                             |
| DELETE | `/tarefas/{tarefa_id}`  | Remove uma tarefa                                              |

Regras de um item, iguais às do formulário do frontend:

- `nome`: obrigatório, de 3 a 50 caracteres (espaços nas pontas são removidos) e único sem diferenciar maiúsculas. Repetir um nome devolve `409` com `{"detail": "Já existe um item com esse nome."}`. O índice único no banco garante a regra mesmo com requisições simultâneas;
- `descricao`: obrigatória, até 200 caracteres.

## Qualidade de código

O projeto usa o [Ruff](https://docs.astral.sh/ruff/) para lint e formatação do backend:

```bash
make format   # formata e corrige o que for possível
make lint     # apenas verifica (usado no CI)
```

## Executando os testes do backend

Os testes automatizados ficam em `backend/tests` e usam Pytest, separados em:

- `tests/unit`: testes unitários sem banco (schemas, services com repositórios falsos em memória e configuração do CORS);
- `tests/integration`: testes que usam o PostgreSQL real: endpoints via `TestClient`, repositories, migrations e cabeçalhos de CORS.

Cada teste recebe automaticamente o marker `unit` ou `integration` de acordo com a pasta.

Os testes de integração usam um banco separado, `c216_test` (criado automaticamente se não existir), para não apagar os dados da aplicação. A estrutura é criada pelas próprias migrations do Alembic e as tabelas são limpas entre um teste e outro.

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

O frontend fica em `frontend/` e implementa um gerenciador de itens com nome e descrição. Os itens são lidos e gravados na API, então continuam na lista depois de recarregar a página.

### Funcionalidades

- Listagem, cadastro, edição e remoção de itens pela API (`src/services/items.js`, com `fetch`);
- Estados da interface:
  - **carregando**: "Carregando itens..." enquanto a lista não chega;
  - **erro**: mensagem quando a API está fora do ar ou recusa a operação (ex.: nome repetido), com botão "Tentar novamente" no carregamento;
  - durante o envio, o botão mostra "Salvando..." e fica desabilitado; em caso de erro, os campos digitados são mantidos;
- Validação no formulário, antes de chamar a API:
  - nome obrigatório, entre 3 e 50 caracteres e sem repetir o nome de outro item (sem diferenciar maiúsculas);
  - descrição obrigatória, com até 200 caracteres;
  - os erros aparecem após a primeira tentativa de envio e somem assim que o campo é corrigido;
- Contador de caracteres e mensagens de erro ligadas aos campos (`aria-invalid`, `aria-describedby` e `role="alert"`);
- Layout responsivo com Tailwind CSS: formulário e lista lado a lado em telas médias e empilhados no celular.

### Stack

| Ferramenta                                                          | Uso                                         |
| ------------------------------------------------------------------- | ------------------------------------------- |
| [Vite](https://vite.dev/) + [React](https://react.dev/)             | Build e interface                           |
| [Tailwind CSS](https://tailwindcss.com/) (plugin `@tailwindcss/vite`) | Estilos                                    |
| [Biome](https://biomejs.dev/)                                       | Lint e formatação                           |
| [Vitest](https://vitest.dev/) + [Testing Library](https://testing-library.com/) | Testes unitários e de integração |
| [Playwright](https://playwright.dev/)                               | Testes E2E no navegador                     |
| [Nginx](https://nginx.org/)                                         | Serve o build no container `frontend`       |

### Estrutura

```
frontend/
├── src/
│   ├── main.jsx              # Ponto de entrada, monta o App
│   ├── App.jsx               # Junta formulário e lista e controla o item em edição
│   ├── index.css             # Importa o Tailwind
│   ├── services/items.js     # Chamadas à API com fetch (listItems, createItem, updateItem, deleteItem)
│   ├── components/
│   │   ├── ItemForm.jsx      # Formulário de cadastro e edição com validação e erro da API
│   │   ├── CampoTexto.jsx    # Campo com label, contador e mensagem de erro
│   │   ├── ItemList.jsx      # Lista, contador e estados de carregamento, erro e vazio
│   │   └── ItemCard.jsx      # Um item com as ações de editar e remover
│   ├── hooks/useItens.js     # Estado dos itens sincronizado com a API
│   └── utils/
│       ├── validacao.js      # Regras de validação (funções puras)
│       └── itens.js          # Operações sobre a lista exibida (funções puras)
├── tests/
│   ├── helpers/api.js        # Respostas falsas e uma API /items/ em memória para mockar o fetch
│   ├── unit/                 # Testes de validacao.js, itens.js e services/items.js
│   └── integration/          # Testes do App renderizado, simulando o usuário
├── e2e/                      # Testes E2E com Playwright contra a stack completa
├── Dockerfile                # Build com Node e imagem final com Nginx
├── nginx.conf
├── biome.json
├── playwright.config.js
└── vite.config.js            # Configuração do Vite e do Vitest
```

### Executando

Pelo Docker Compose (`make up-build`), o frontend fica em http://localhost:5173. O `frontend/Dockerfile` gera o build com o Vite, embutindo `VITE_API_URL`, e serve os arquivos estáticos com o Nginx.

Em modo de desenvolvimento, com a API rodando:

```bash
cd frontend
npm ci
npm run dev       # http://localhost:5173
```

Ou, a partir da raiz, `make frontend-install` e `make frontend-dev`.

### Qualidade e testes

```bash
make frontend-check   # lint e formatação com o Biome
make frontend-format  # formata o código
make frontend-test    # testes unitários e de integração (Vitest)
make frontend-build   # build de produção em dist/
make e2e              # testes E2E com os serviços integrados
```

Os testes seguem três níveis:

- **Unitários** (`tests/unit`): regras de validação, operações da lista e o serviço `items.js` com o `fetch` mockado (URL, método, corpo JSON, respostas `204`, mensagens de erro `409`/`422`/`500` e falha de conexão);
- **Integração** (`tests/integration`): renderizam o `App` em jsdom com o `fetch` mockado e simulam o usuário com `user-event`, cobrindo os estados de **carregamento** (promessa pendente), **sucesso** (lista, cadastro, edição e remoção) e **erro** (API fora do ar, nome repetido, falha ao remover);
- **E2E** (`e2e`): o Playwright abre o frontend servido pelo Nginx, que chama a API real com PostgreSQL. Os testes cadastram um item e conferem que ele **continua na lista após `page.reload()`**, verificam o preflight `OPTIONS` e o cabeçalho `access-control-allow-origin` do `POST /items/`, o erro de nome repetido (validado no formulário e pela API), a persistência de edição e remoção, a validação antes de chamar a API e a ausência de rolagem horizontal. Rodam em um navegador desktop e em um celular emulado.

O `make e2e` sobe uma stack isolada no projeto `lab-e2e` (portas `15173`, `18000` e `55432`, para não conflitar com o `make up`), executa o Playwright e remove containers e volume com `down --volumes`, mesmo quando um teste falha. Para rodar o Playwright contra a stack do `make up`, use `cd frontend && npm run test:e2e`.

Na primeira execução dos testes E2E é preciso baixar o navegador:

```bash
cd frontend && npx playwright install chromium
```

Para rodar todo o checklist de uma vez, a partir da raiz:

```bash
make check-all   # lint e testes do backend, npm ci, frontend-check, frontend-test, frontend-build e e2e
```

O workflow `.github/workflows/ci-frontend.yml` roda a cada `push` e `pull_request` com dois jobs: um com lint, formatação, testes do Vitest e build, e outro que executa `make e2e` com os serviços integrados e publica o relatório do Playwright como artefato.

## Checklist de validação

- `make up-build` sobe `db`, `api` e `frontend`, todos `healthy` em `make ps`;
- `make db-upgrade` aplica a migration e `make db-current` mostra `(head)`;
- http://localhost:8000/docs abre e http://localhost:5173 carrega a interface;
- cadastrar um item pela interface o exibe na lista e recarregar a página (F5) o mantém;
- cadastrar o mesmo nome de novo mostra "Já existe um item com esse nome.";
- a aba *Network* mostra `OPTIONS` + `POST /items/` e o cabeçalho `access-control-allow-origin`;
- `make test`, `make frontend-test`, `make frontend-check` e `make frontend-build` passam;
- `make e2e` passa e não deixa containers `lab-e2e` ativos.
