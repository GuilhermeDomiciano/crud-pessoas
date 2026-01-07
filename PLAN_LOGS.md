# Plano de Implementacao - Checkpoint 13 (Logs de requisicao/resposta)

Objetivo: gravar logs de requisicao/resposta em DB separado `app_logs`, collection `request_logs`, com mascaramento e limites de payload.

## Passo 1 - Inventario e decisoes
- DB: `app_logs`; collection: `request_logs`.
- TTL: 30 dias.
- Campos sensiveis para mascarar:
  - `documentNumber`, `email`, `password`, `token`, `accessToken`, `refreshToken`,
    `authorization`, `apiKey`, `secret`, `ssn`, `cpf`, `cnpj`, `phone`, `phoneNumber`.
- Limite de body: 10KB (truncar payload e registrar que foi truncado).

## Passo 2 - Configuracao de settings
- Adicionar variaveis em `settings.py`:
  - `MONGODB_LOGS_DB` (default `app_logs`)
  - `LOG_TTL_DAYS` (opcional)
  - `LOG_BODY_MAX_BYTES` (opcional)
- Atualizar `.env.example` e `README` com novas variaveis.

## Passo 3 - Conexao e indexes do DB de logs
- Criar helper `get_logs_db()` em `db/database.py`.
- Criar `ensure_log_indexes()` para:
  - `{ requestTime: -1 }`
  - `{ statusCode: 1, requestTime: -1 }`
  - `{ method: 1, url: 1, requestTime: -1 }`
  - TTL (se `LOG_TTL_DAYS` definido)
- Atualizar `lifespan` para chamar `ensure_log_indexes`.

## Passo 4 - Modelo de log e utilitarios
- Definir schema (pydantic opcional) para o documento de log.
- Implementar helpers:
  - `mask_sensitive(data, fields)` (recursivo)
  - `truncate_body(data, max_bytes)`
  - `extract_error(status, response_body)`

## Passo 5 - Middleware de logging
- Criar middleware FastAPI:
  - Capturar `requestTime`, `responseTime`, `method`, `url`, `statusCode`, `userAgent`, `ip`, `requestId`.
  - Extrair `params`, `query`, `body` (se houver).
  - Mascarar e truncar body.
  - Capturar `error` quando status >= 400.
  - Calcular `durationMs`.
  - Inserir documento no DB de logs.
- Garantir que falha no log nao derrube a request (try/except).

## Passo 6 - Validacao e testes manuais
- Subir a API e chamar alguns endpoints.
- Verificar documentos no Mongo (collection `request_logs`).
- Testar:
  - Body grande (truncado)
  - Campos sensiveis mascarados
  - 400/404/409 com `error`

## Passo 7 - Ajustes finais
- Refinar lista de campos sensiveis.
- Ajustar TTL e tamanho maximo conforme necessidade.

Notas:
- Nao logar binario/base64.
- Garantir que `requestId` seja gerado quando nao vier de header.
