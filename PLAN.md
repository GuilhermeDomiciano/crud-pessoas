Checkpoints — Implementar cache com Redis (cache-aside) no seu backend
Checkpoint R1 — Infra Redis + env flags

Adicionar Redis no docker-compose.yml

Variáveis no .env.example:

REDIS_URL=redis://redis:6379/0

CACHE=ON|OFF (default OFF ou ON, você decide)

CACHE_TTL_PERSON_SECONDS=300

CACHE_TTL_LIST_SECONDS=60

Criar módulo cache/redis_client.py com:

singleton de conexão

startup/shutdown

ping no health

Checkpoint R2 — API de cache (wrapper) pra não espalhar Redis no código

Criar cache/cache_service.py com funções:

get_json(key) -> dict | None

set_json(key, value, ttl)

delete(key)

incr(key) (pra versionamento)

Serialização consistente (JSON) e compressão opcional (deixa pra depois)

Checkpoint R3 — Estratégia de keys (nada de key aleatória)

Key para pessoa:

person:{personId}

Key para listas/queries (com versionamento pra invalidar sem varrer Redis):

persons:list:v{ver}:{hash(query)}

Key de versão:

persons:list:ver (int)

Hash do query: gerar a partir de params normalizados (limit, skip, name, email, sort, etc.)

Checkpoint R4 — Cache de leitura (read-through / cache-aside)

Aplicar no service/usecase, não no router.

GET /persons/{id}:

se CACHE=OFF → busca no Mongo direto

se CACHE=ON:

tenta GET person:{id}

se hit → retorna

se miss → busca no Mongo, SET com TTL, retorna

GET /persons (lista + filtros):

monta queryKey = persons:list:v{ver}:{hash(query)}

tenta cache; se miss busca Mongo e salva com TTL menor

Regras:

Não cachear erro (404/500)

TTL curto pra lista, maior pra item

Checkpoint R5 — Invalidação no write (sem frescura)

Em toda mutação de pessoa, invalidar item e listas:

Após POST /persons:

delete person:{newId} (opcional, geralmente nem existe)

incr persons:list:ver

Após PATCH /persons/{id} e DELETE /persons/{id}:

delete person:{id}

incr persons:list:ver

Após endpoints de subdocs (addresses e phones):

delete person:{id}

incr persons:list:ver

Isso resolve listas sem precisar SCAN/DEL por padrão.

Checkpoint R6 — Proteções mínimas (pra não virar fonte de bug)

Timeout curto no Redis (ex.: 50–150ms)

Falha no Redis não quebra a API:

se Redis cair: loga e faz fallback Mongo

se SET falhar: ignora

Key namespace (ex.: prefixo app:) pra evitar conflito:

app:person:{id}, app:persons:list:...

Checkpoint R7 — Endpoint/observabilidade do cache (debug)

GET /cache/health (ou incluir no /health)

mostra redis=ok|down, cache=on|off

(Opcional) contador simples:

cache_hits, cache_misses por endpoint (só log já serve)

Checkpoint R8 — Ajuste fino de TTL e payload

Se PersonOut for grande, cachear só o que retorna na API (não doc cru do Mongo)

Revisar TTL:

pessoa: 5–15 min

lista: 30–120s

(Opcional) “stale-while-revalidate” fica pra depois

Onde aplicar primeiro (impacto real)

GET /persons/{id} (maior ganho, invalidação simples)

GET /persons com filtros/paginação (gargalo comum)

Armadilhas que você deve evitar

Cachear lista sem versionamento (vai ficar servindo dado velho)

Invalidar lista com DEL por pattern (vai doer quando crescer)

Cachear resposta que depende de auth/escopo sem incluir isso na key

Se você quiser, eu te passo o contrato exato de hash(query) e um exemplo de “normalização de query” (ordenar keys, remover valores vazios, etc.) pra não gerar keys diferentes pro mesmo filtro.