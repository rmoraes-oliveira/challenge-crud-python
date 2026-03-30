# Challenge CRUD Python

API REST para cadastro e consulta de usuários, com paginação, cache em Redis e persistência em PostgreSQL.

## Stack

| Camada | Tecnologia |
|--------|------------|
| Linguagem | Python 3.12+ |
| API | FastAPI, Uvicorn |
| Banco | PostgreSQL, SQLAlchemy, Alembic |
| Cache | Redis |
| Dependências | uv |
| Testes | pytest, httpx, fakeredis |
| Lint / formatação | Ruff |

## Pré-requisitos

- **Python 3.12+** e **[uv](https://docs.astral.sh/uv/)** para dependências e execução de comandos
- **Docker** e **Docker Compose** (opcional, recomendado para subir API + Postgres + Redis de forma integrada)

## Variáveis de ambiente

| Variável | Obrigatório | Descrição |
|----------|-------------|-----------|
| `DATABASE_URL` | Sim | URL de conexão do PostgreSQL (formato SQLAlchemy) |
| `REDIS_URL` | Sim * | URL do Redis (usado no cache das rotas de usuário) |
| `CACHE_TTL` | Não | TTL do cache em segundos (padrão: `60`) |

\* Em testes automatizados o `conftest` usa Redis em memória (**fakeredis**); em produção ou desenvolvimento local com a app real, configure `REDIS_URL`.

Crie um arquivo **`.env`** na raiz (o projeto carrega com `python-dotenv`) ou exporte as variáveis no shell.

## Execução com Docker

O **`Dockerfile`** e o **`docker-compose.yml`** sobem a aplicação junto com **PostgreSQL 16** e **Redis 7**.

| Serviço | Conteúdo | Porta (host) |
|---------|----------|---------------|
| `app` | API (Uvicorn com `--reload`, volume do código) | `8000` |
| `db` | PostgreSQL (`challenge_db`, usuário/senha `postgres`/`postgres`) | `5432` |
| `redis` | Redis (AOF habilitado) | `6379` |

No Compose, a aplicação recebe automaticamente:

- `DATABASE_URL=postgresql://postgres:postgres@db:5432/challenge_db`
- `REDIS_URL=redis://redis:6379/0`

**Subir o ambiente:**

```bash
docker compose up --build
```

Antes do Uvicorn, o serviço `app` executa `alembic upgrade head` (aplicação das migrations).

**Encerrar** (mantém volumes de dados):

```bash
docker compose down
```

**Remover também os volumes** (`postgres_data`, `redis_data`):

```bash
docker compose down -v
```

**Imagem apenas da API:** o `Dockerfile` inicia `uvicorn` na porta `8000`; é necessário informar `DATABASE_URL` e `REDIS_URL` apontando para serviços acessíveis (rede Docker ou host).

- **API:** [http://localhost:8000](http://localhost:8000)
- **Swagger UI:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc:** [http://localhost:8000/redoc](http://localhost:8000/redoc)

## Execução local (sem Docker)

1. **Instalar dependências**

   ```bash
   uv sync
   ```

2. **PostgreSQL e Redis**  
   Tenha instâncias acessíveis e defina `DATABASE_URL` e `REDIS_URL` (por exemplo em `.env`), alinhados ao banco que você criar (nome de database, usuário e senha).

   Exemplo de criação de banco com cliente `psql` ou `createdb` (ajuste usuário/host conforme sua instalação):

   ```bash
   createdb -U postgres challenge_db
   ```

3. **Migrations**

   ```bash
   uv run alembic upgrade head
   ```

4. **Servidor de desenvolvimento**

   ```bash
   uv run uvicorn app.main:app --reload
   ```

   A API ficará em [http://localhost:8000](http://localhost:8000).

## Referência da API

| Método | Caminho | Descrição |
|--------|---------|-----------|
| `POST` | `/api/v1/users/` | Cria usuário |
| `GET` | `/api/v1/users/` | Lista usuários (paginação: `page`, `size`) |
| `GET` | `/api/v1/users/{user_id}` | Obtém usuário por ID (UUID) |
| `PUT` | `/api/v1/users/{user_id}` | Atualiza usuário (corpo parcial) |
| `DELETE` | `/api/v1/users/{user_id}` | Remove usuário |
| `GET` | `/api/v1/health/db` | Verifica conectividade com o banco |

**Paginação (`GET /api/v1/users/`):** `page` ≥ 1 (padrão `1`); `size` entre 1 e 100 (padrão `10`).

Contratos detalhados, validação e testes a partir do navegador: **[Swagger UI](http://localhost:8000/docs)**.

**Exemplo — criar usuário:**

```bash
curl -sS -X POST "http://localhost:8000/api/v1/users/" \
  -H "Content-Type: application/json" \
  -d '{"name":"John Doe","email":"john.doe@example.com","age":30}'
```

**Exemplo — listar primeira página:**

```bash
curl -sS "http://localhost:8000/api/v1/users/?page=1&size=10"
```

## Testes

Os testes ficam em **`tests/`**, com **`TestClient`** do FastAPI e fixture **`client`** em **`tests/conftest.py`**. A suíte usa **SQLite** em arquivo e **fakeredis**; não é necessário Postgres/Redis para `pytest`.

```bash
uv sync --group dev
uv run pytest          # execução padrão
uv run pytest -v       # mais detalhes
```

Configuração em **`pytest.ini`**: `testpaths = tests`, `pythonpath = .`.

## Qualidade de código (Ruff)

```bash
uv sync --group dev
uv run ruff check app tests
uv run ruff format app tests
```

## Seed de dados (`seed_users.py`)

Script para popular o banco com registros sintéticos (**Faker**, locale `pt_BR`): por padrão **500** usuários, e-mails únicos no formato `{usuario}{indice}@example.com`, idades entre **18** e **65**, em uma transação via `SessionLocal`.

**Requisitos:** migrations aplicadas e `DATABASE_URL` coerente com o banco da API.

**Local:**

```bash
uv run python seed_users.py
```

**Docker Compose** (com o serviço `app` em execução):

```bash
docker compose exec app uv run python seed_users.py
```

**Quantidade customizada** (`seed_users(total=...)`):

```bash
uv run python -c "from seed_users import seed_users; seed_users(100)"
```
