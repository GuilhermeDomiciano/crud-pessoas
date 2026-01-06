# Plano de Implementacao - Checkpoint 10 (Person com subdocumentos)

Objetivo: refatorar o modelo `Person` para usar `firstName`/`lastName`, adicionar subdocumentos `addresses` e `phoneNumbers`, novos campos, auditoria e soft delete, mantendo conversao de ObjectId para string no output.

## Passo 1 - Inventario e impactos
- Mapear onde o modelo `Person` e usado (model, repo, service, routes, testes).
- Listar endpoints e payloads atuais para ajustar contratos.
- Teste rapido: `pytest` (para confirmar baseline antes de mudar).

## Passo 2 - Modelos e tipos
- Atualizar `model/person.py`:
  - Trocar `name` -> `firstName` e `lastName`.
  - Adicionar `documentNumber`, `dateOfBirth`.
  - Criar modelos `Address` e `Phone` (com `_id` por item, e `type` em Phone).
  - Adicionar `addresses: list[Address]`, `phoneNumbers: list[Phone]`.
  - Auditoria: `createdAt`, `updatedAt`, `version`, `deletedAt | None`.
- Decidir formatos (por exemplo `dateOfBirth` como `date`).

## Passo 3 - Conversao e ObjectId
- Atualizar helpers em `db/objectid.py` para:
  - Converter `_id` de pessoa e `_id` dos subdocs em string no output.
  - Manter compatibilidade para listas e subdocumentos.
- Adicionar testes unitarios simples para conversao (se fizer sentido).

## Passo 4 - Repository
- Ajustar `repository/person_repo.py`:
  - Adaptar insercao e update para novos campos.
  - Setar auditoria (`createdAt`, `updatedAt`, `version`).
  - Soft delete: setar `deletedAt` ao remover.
  - Filtragem de listagem: ignorar `deletedAt`.
  - Gerar `_id` para cada `Address` e `Phone` no create e no update.

## Passo 5 - Services e regras
- Validar `documentNumber` (se houver regra).
- Ajustar update parcial para aceitar subdocs.
- Incrementar `version` a cada update.

## Passo 6 - Routers e contratos
- Atualizar schemas de entrada/saida nos endpoints.
- Revisar exemplos no `README.md`.

## Passo 7 - Testes
- Atualizar testes existentes para os novos campos.
- Cobrir: create, list, get by id, update parcial, delete (soft), duplicidade (se ainda existir).
- Testar conversao de `_id` de subdocs no output.

## Passo 8 - Validacao final
- `ruff check .`
- `pytest`

Notas:
- Fazer pequenas mudancas por etapa e rodar testes sempre que possivel.
