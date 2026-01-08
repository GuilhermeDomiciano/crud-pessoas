2) Autenticação JWT / API-KEY
Checkpoint A1 — Infra de auth (config + dependência de autenticação)

Variáveis .env:

AUTH_MODE=OFF|API_KEY|JWT|BOTH

JWT_SECRET, JWT_ALG=HS256, JWT_EXPIRES_MIN

API_KEYS= (ou DB/collection depois)

Criar auth/ com:

dependencies.py (get_current_principal)

jwt.py (encode/decode/claims)

api_key.py (validar header)

Checkpoint A2 — API-KEY simples (rápido e útil)

Header padrão: X-API-Key: <key>

Comparação segura (timing-safe)

Decidir armazenamento:

versão simples: keys em env

melhor: collection api_keys com hash + status + nome + createdAt

Rate limit fica pra depois; agora só validação e 401

Checkpoint A3 — JWT (sem sistema de usuários completo ainda)

Definir claims mínimos:

sub (id do sujeito), iat, exp, scope/roles (opcional)

Criar endpoint de emissão (mínimo):

POST /auth/token (credencial simples por env ou “usuário fake” por enquanto)

Middleware/Dependency para:

ler Authorization: Bearer <token>

validar assinatura e expiração

expor “principal” para a rota

Checkpoint A4 — Proteção por rota (granular)

Definir quais rotas são públicas:

/health público

/docs opcional (ou protegida)

Proteger /persons/* com auth

Adicionar “scopes” simples:

persons:read, persons:write

checar scope na dependency

Checkpoint A5 — Observabilidade + segurança básica

Não logar segredo/token no log (mascarar headers sensíveis)

Respostas 401/403 padronizadas

“Key rotation” (suportar múltiplas API keys ativas)