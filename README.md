# CRUD Pessoas - Backend

API FastAPI para cadastro de pessoas com MongoDB.

## Como rodar

1) Suba o MongoDB (opcional se ja tiver um rodando):

```bash
docker compose up -d
```

Se quiser usar o pipeline assíncrono de logs, suba o RabbitMQ também (ele já está no compose):

```bash
docker compose up -d rabbitmq
```

2) Instale dependencias:

```bash
cd backend
pip install -r requirements.txt
```

3) Configure o arquivo `.env` em `backend/.env` (veja abaixo).

4) Inicie a API:

```bash
cd backend
uvicorn main:app --app-dir app --reload
```

API: `http://localhost:8000`

## Variaveis de ambiente

Arquivo: `backend/.env`

- `MONGODB_URI` (obrigatoria) - string de conexao do MongoDB.
- `MONGODB_DB` (opcional) - nome do banco, padrao `personal_db`.
- `MONGODB_LOGS_DB` (opcional) - nome do banco de logs, padrao `app_logs`.
- `LOG_TTL_DAYS` (opcional) - dias para expirar logs, padrao `30`.
- `LOG_BODY_MAX_BYTES` (opcional) - limite de bytes do body logado, padrao `10240`.
- `RABBITMQ_URL` (opcional) - URL do RabbitMQ (ex.: `amqp://guest:guest@localhost:5672/`).
- `LOGGER` (opcional) - `ON` ou `OFF` para ativar/desativar logs, padrao `ON`.
- `LOGGER_MODE` (opcional) - `ASYNC`, `SYNC` ou `DISABLE`.
  - `ASYNC`: publica na fila RabbitMQ (padrao).
  - `SYNC`: grava direto no Mongo (debug).
  - `DISABLE`: nao grava (pode logar no console).
- `AUTH_MODE` (opcional) - `OFF`, `API_KEY`, `JWT` ou `BOTH`.
- `JWT_SECRET` (obrigatoria se `AUTH_MODE=JWT`/`BOTH`).
- `JWT_ALG` (opcional) - algoritmo JWT, padrao `HS256`.
- `JWT_EXPIRES_MIN` (opcional) - expira em minutos, padrao `60`.
- `API_KEYS` (opcional) - lista separada por virgula (ex.: `key1,key2`).
  - Suporta multiplas chaves ativas (rotacao).
  - Se nao estiver definido, a API usa a collection `api_keys` no Mongo.
- `AUTH_USER` (opcional) - usuario simples para emitir token.
- `AUTH_PASSWORD` (opcional) - senha simples para emitir token.
- `AUTH_ROLES` (opcional) - roles separadas por virgula (ex.: `admin,reader`).
- `APP_HOST` (opcional) - usado apenas no exemplo de `.env`.
- `APP_PORT` (opcional) - usado apenas no exemplo de `.env`.

Exemplo:

```
MONGODB_URI=mongodb://root:root@localhost:27017/personal_db?authSource=admin
MONGODB_DB=personal_db
MONGODB_LOGS_DB=app_logs
LOG_TTL_DAYS=30
LOG_BODY_MAX_BYTES=10240
RABBITMQ_URL=amqp://guest:guest@localhost:5672/
LOGGER=ON
LOGGER_MODE=ASYNC
AUTH_MODE=OFF
JWT_SECRET=5565be7f86e171ec332bf2f30b6f0d3b944a389fc7168b663e693e1b73be69d8
JWT_ALG=HS256
JWT_EXPIRES_MIN=60
API_KEYS=ff63d8d424ad4fff9604b5db91b4da9d,461da3c1d087495389af86c10e492fa4
AUTH_USER=admin
AUTH_PASSWORD=admin
AUTH_ROLES=admin
APP_HOST=0.0.0.0
APP_PORT=8000
```

## Logs (RabbitMQ)

Ative ou desative o pipeline assíncrono via env:

- `LOGGER=ON` e `LOGGER_MODE=ASYNC` publica na fila.
- `LOGGER=ON` e `LOGGER_MODE=SYNC` grava direto no Mongo (debug).
- `LOGGER=OFF` ou `LOGGER_MODE=DISABLE` não grava.

Rodar o consumer separado:

```bash
cd backend
python app/worker/logger_consumer.py
```

## Endpoints

Base URL: `http://localhost:8000`

- `GET /` - mensagem de boas-vindas.
- `GET /health/` - healthcheck da API.
- `GET /health/ping` - healthcheck com ping no MongoDB.

- `POST /persons/` - cria pessoa.
- `GET /persons/` - lista pessoas (query: `skip`, `limit`, `firstName`, `lastName`, `email`).
- `GET /persons/{id}` - busca por id.
- `PATCH /persons/{id}` - update parcial.
- `DELETE /persons/{id}` - remove pessoa.

## Exemplos de payload

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

Filtro de lista (exemplo):

```
GET /persons/?skip=0&limit=20&firstName=maria&email=@example.com
```
