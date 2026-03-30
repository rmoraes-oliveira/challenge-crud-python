# Challenge CRUD Python

## API Endpoints

### 1. Create User
**Endpoint:** `POST /api/v1/users`

**Description:** Creates a new user.

**Request:**
```bash
curl -X POST \
  http://localhost:8000/api/v1/users \
  -H 'Content-Type: application/json' \
  -d '{
    "name": "John Doe",
    "email": "john.doe@example.com",
    "age": 30
  }'
```

### 2. List Users
**Endpoint:** `GET /api/v1/users`

**Description:** Retrieves a paginated list of users.

**Query Parameters:**
- `page` (int): Page number (default: 1).
- `size` (int): Number of records per page (default: 10, max: 100).

**Request:**
```bash
curl -X GET "http://localhost:8000/api/v1/users?page=1&size=10"
```

### 3. Get User by ID
**Endpoint:** `GET /api/v1/users/{user_id}`

**Description:** Retrieves a user by their ID.

**Request:**
```bash
curl -X GET http://localhost:8000/api/v1/users/<user_id>
```

### 4. Update User
**Endpoint:** `PUT /api/v1/users/{user_id}`

**Description:** Updates a user's information.

**Request:**
```bash
curl -X PUT \
  http://localhost:8000/api/v1/users/<user_id> \
  -H 'Content-Type: application/json' \
  -d '{
    "name": "Jane Doe",
    "email": "jane.doe@example.com",
    "age": 25
  }'
```

### 5. Delete User
**Endpoint:** `DELETE /api/v1/users/{user_id}`

**Description:** Deletes a user by their ID.

**Request:**
```bash
curl -X DELETE http://localhost:8000/api/v1/users/<user_id>
```

### 6. Health Check (Database)
**Endpoint:** `GET /api/v1/health/db`

**Description:** Checks the database connection status.

**Request:**
```bash
curl -X GET http://localhost:8000/api/v1/health/db
```

## Como Rodar o Projeto

### Com Docker (recomendado para desenvolvimento)

O repositório inclui **`Dockerfile`** e **`docker-compose.yml`** para subir a API junto com **PostgreSQL** e **Redis** sem instalar esses serviços na máquina.

**Serviços:**

| Serviço | Imagem / build | Porta host | Função |
|--------|-----------------|------------|--------|
| `app`  | build do `Dockerfile` | `8000` | API FastAPI (Uvicorn com `--reload`) |
| `db`   | `postgres:16-alpine` | `5432` | Banco `challenge_db` (usuário/senha: `postgres`/`postgres`) |
| `redis`| `redis:7-alpine`       | `6379` | Cache usado nos endpoints de usuários |

**Variáveis no container da app** (definidas no Compose):

- `DATABASE_URL`: `postgresql://postgres:postgres@db:5432/challenge_db`
- `REDIS_URL`: `redis://redis:6379/0`

**Subir tudo:**

```bash
docker compose up --build
```

Na primeira execução (e após mudanças de migration), o serviço `app` roda `alembic upgrade head` antes do Uvicorn. O diretório do projeto é montado em `/app` para hot-reload.

**API:** [http://localhost:8000](http://localhost:8000) · **Docs:** [http://localhost:8000/docs](http://localhost:8000/docs)

**Parar e remover containers** (mantém volumes com dados de Postgres/Redis):

```bash
docker compose down
```

Para apagar também os volumes nomeados (`postgres_data`, `redis_data`):

```bash
docker compose down -v
```

**Só a imagem da API (sem Compose):** o `Dockerfile` expõe a porta `8000` e usa `uv run uvicorn`; para funcionar é preciso fornecer `DATABASE_URL` e `REDIS_URL` apontando para instâncias acessíveis (por exemplo, rede Docker ou host).

---

### Execução local (sem Docker)

### 1. Configurar o Ambiente Virtual
Certifique-se de que o ambiente virtual está ativado:
```bash
source .venv/bin/activate
```

### 2. Instalar Dependências
Instale as dependências do projeto:
```bash
uv sync
```

### 3. Configurar o Banco de Dados
Inicialize o banco de dados com o Alembic:
```bash
createdb -U postgres challenge_python
alembic upgrade head
```

### 4. Rodar o Servidor
Inicie o servidor FastAPI:
```bash
uvicorn app.main:app --reload
```

O servidor estará disponível em: [http://localhost:8000](http://localhost:8000)

### 5. Documentação da API
Acesse a documentação interativa da API no Swagger:
- [Swagger UI](http://localhost:8000/docs)
- [Redoc](http://localhost:8000/redoc)