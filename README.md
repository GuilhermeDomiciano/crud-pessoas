# CRUD Pessoas - Backend

API FastAPI para cadastro de pessoas com MongoDB, logs em banco separado (com RabbitMQ opcional), e cache Redis (cache-aside).

## Por que esse projeto existe

Este projeto foi desenhado para treinar observabilidade e boas praticas de API:
- Modelos ricos com subdocumentos (endereços, telefones)
- Logs estruturados em DB separado
- Pipeline async com RabbitMQ
- Cache Redis com invalidação simples
- Autenticação (API Key / JWT) e scopes

## Stack

- FastAPI + Uvicorn
- MongoDB + Motor (async)
- Redis (cache)
- RabbitMQ (fila de logs)
- Pydantic v2
- PyJWT
- Ruff + MyPy (opcional)
- Pytest + httpx

## Arquitetura (pasta app)

- `routers/` - rotas HTTP
- `services/` - regras de negocio
- `repository/` - acesso ao Mongo
- `model/` - schemas Pydantic
- `middleware/` - logging de request
- `auth/` - JWT + API Key
- `cache/` - Redis client + chaves
- `messaging/` - RabbitMQ
- `worker/` - consumer de logs

## Como rodar (local)

1) Suba dependências:

```bash
docker compose up -d
```

2) Instale dependências:

```bash
cd backend
pip install -r requirements.txt
```

3) Configure `.env` em `backend/.env` (use o `.env.example` como base).

4) Suba a API:

```bash
cd backend
uvicorn main:app --app-dir app --reload
```

API: `http://localhost:8000`

Swagger: `http://localhost:8000/docs`

## Variáveis de ambiente (principais)

Arquivo: `backend/.env`

### Mongo
- `MONGODB_URI` (obrigatoria)
- `MONGODB_DB` (padrão `personal_db`)
- `MONGODB_LOGS_DB` (padrão `app_logs`)

### Logs
- `LOG_TTL_DAYS` (padrão `30`)
- `LOG_BODY_MAX_BYTES` (padrão `10240`)
- `LOGGER=ON|OFF`
- `LOGGER_MODE=ASYNC|SYNC|DISABLE`
- `RABBITMQ_URL` (ex.: `amqp://guest:guest@localhost:5672/`)

### Cache
- `REDIS_URL` (host: `redis://localhost:6379/0`)
- `CACHE=ON|OFF`
- `CACHE_TTL_PERSON_SECONDS` (padrão `600`)
- `CACHE_TTL_LIST_SECONDS` (padrão `60`)
- `REDIS_TIMEOUT_MS` (padrão `150`)

### Auth
- `AUTH_MODE=OFF|API_KEY|JWT|BOTH`
- `API_KEYS` (lista separada por virgula)
- `JWT_SECRET`, `JWT_ALG`, `JWT_EXPIRES_MIN`
- `AUTH_USER`, `AUTH_PASSWORD`, `AUTH_ROLES`

## Endpoints (resumo)

Base URL: `http://localhost:8000`

### Pessoas
- `POST /persons/`
- `GET /persons/`
- `GET /persons/{id}`
- `PATCH /persons/{id}`
- `DELETE /persons/{id}`

### Subdocs (endereços e telefones)
- `POST /persons/{id}/addresses`
- `PATCH /persons/{id}/addresses/{addressId}`
- `DELETE /persons/{id}/addresses/{addressId}`

- `POST /persons/{id}/phones`
- `PATCH /persons/{id}/phones/{phoneId}`
- `DELETE /persons/{id}/phones/{phoneId}`

### Auth
- `POST /auth/token`

### Logs
- `GET /logs`
- `GET /persons/{id}/logs`
- `GET /logs/dlq`

### Health
- `GET /health/`
- `GET /health/ping`
- `GET /health/rabbit`
- `GET /health/cache`

## Payloads de exemplo

Criar pessoa:

```json
{
  "firstName": "Maria",
  "lastName": "Silva",
  "email": "maria@example.com",
  "documentNumber": "12345678900",
  "dateOfBirth": "1995-02-10",
  "addresses": [
    {
      "line1": "Rua A, 123",
      "city": "Sao Paulo"
    }
  ],
  "phoneNumbers": [
    {
      "type": "mobile",
      "number": "11999990000"
    }
  ]
}
```

Update parcial:

```json
{
  "lastName": "Souza"
}
```

## Autenticação (resumo)

- API Key: header `X-API-Key: <key>`
- JWT: header `Authorization: Bearer <token>`

Scopes:
- `persons:read`
- `persons:write`

## Logs (RabbitMQ)

Modo recomendado:
- `LOGGER=ON`
- `LOGGER_MODE=ASYNC`

Rodar consumer:

```bash
cd backend
python app/worker/logger_consumer.py
```

Health Rabbit:
- `GET /health/rabbit`

## Cache (Redis)

Ativar cache:
- `CACHE=ON`

Health Cache:
- `GET /health/cache`

Ver chaves no Redis:

```bash
docker exec -it redis_local redis-cli
keys app:*
```

## Testes

```bash
cd backend
pytest
```

## Troubleshooting rapido

- Redis no host: `REDIS_URL=redis://localhost:6379/0`
- Redis no Docker: `REDIS_URL=redis://redis:6379/0`
- Rabbit precondition failed: apague filas antigas no painel do Rabbit (Queues)
- Logs não aparecem: confira `LOGGER`, `LOGGER_MODE` e se o consumer esta rodando

## Proximos passos (ideias)

- Cache em escrita (warm-up)
- Observabilidade com métricas
- Rate limit
- Usuários reais + refresh token

---

Se quiser um walkthrough completo (arquitetura + fluxo de dados), me chama.
