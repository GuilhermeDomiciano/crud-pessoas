3) RabbitMQ (fila) para escrita assíncrona dos Logs

Objetivo fixo (o seu): middleware publica mensagem; consumer grava no Mongo (logs DB). Consumer liga/desliga por LOGGER (default ON).

Checkpoint Q1 — Infra RabbitMQ + docker-compose

Adicionar RabbitMQ no docker-compose.yml (com management UI)

Variáveis .env:

RABBITMQ_URL=amqp://...

LOGGER=ON|OFF (default ON)

LOGGER_MODE=ASYNC|SYNC|DISABLE (recomendado; explica abaixo)

Biblioteca de AMQP (ex.: aio-pika se async)

Checkpoint Q2 — Definir contrato da mensagem de log (schema)

Mensagem JSON contendo exatamente o que você quer salvar:

requestTime, responseTime, method, url, statusCode, userAgent, body, params, query, __v

recomendado: durationMs, requestId, ip

Mascarar/limitar:

remover/mascarar Authorization, X-API-Key, senhas

truncar body acima de X KB

Checkpoint Q3 — Exchange/Queue durável + persistência

Criar:

Exchange (ex.: logs.exchange, type direct)

Queue (ex.: logs.queue, durable)

Routing key (ex.: logs.write)

Publicar mensagem como persistente (pra não perder em restart)

Confirm publisher (garantir que Rabbit aceitou)

Checkpoint Q4 — Middleware de logs publica mensagem (sem travar request)

Middleware captura request/response e monta payload

Se LOGGER=ON e LOGGER_MODE=ASYNC:

publicar na fila

não escrever no Mongo dentro do request

Se publish falhar:

estratégia recomendada: fallback para stdout + “best effort”

opcional: fallback SYNC (escreve direto no Mongo) — mas isso volta a gerar gargalo

Sugestão de modos (pra ficar claro)

LOGGER_MODE=ASYNC: publica na fila (padrão)

LOGGER_MODE=SYNC: escreve direto no Mongo (debug)

LOGGER_MODE=DISABLE: não grava (mas pode logar no console)

Checkpoint Q5 — Consumer (worker) para gravar no Mongo

Criar serviço logger-consumer (processo separado)

Ao iniciar:

conecta no Rabbit

consome logs.queue

valida schema mínimo da mensagem

grava na collection request_logs

Ack/Nack correto:

sucesso: ack

falha temporária (Mongo fora): nack com requeue (cuidado com loop)

falha definitiva (mensagem inválida): mandar para DLQ

Checkpoint Q6 — DLQ + retry controlado

Configurar Dead Letter Exchange/Queue:

logs.dlx + logs.dlq

Retry com limite:

usar header x-death do RabbitMQ para contar tentativas

após N tentativas, mandar para DLQ

Criar endpoint/admin simples:

GET /logs/dlq (opcional) ou script pra inspecionar

Checkpoint Q7 — Toggle do consumer via env LOGGER

LOGGER=OFF:

consumer nem inicia (no compose, escala 0 ou não sobe o serviço)

middleware decide o que fazer:

LOGGER_MODE=DISABLE (não grava)

ou SYNC (grava direto)

Documentar no README:

como ligar/desligar

como rodar consumer separado

Checkpoint Q8 — Métricas mínimas de saúde do pipeline

Health check do Rabbit (no app e no consumer)

Logar tamanho da fila (opcional)

Alarmes manuais: se DLQ crescer, tem bug/instabilidade