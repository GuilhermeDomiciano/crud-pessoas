# CRUD Pessoas - Backend

API FastAPI para cadastro de pessoas com MongoDB.

## Como rodar

1) Suba o MongoDB (opcional se ja tiver um rodando):

```bash
docker compose up -d
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
- `APP_HOST` (opcional) - usado apenas no exemplo de `.env`.
- `APP_PORT` (opcional) - usado apenas no exemplo de `.env`.

Exemplo:

```
MONGODB_URI=mongodb://root:root@localhost:27017/personal_db?authSource=admin
MONGODB_DB=personal_db
APP_HOST=0.0.0.0
APP_PORT=8000
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
