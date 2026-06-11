# Evolution API — DataCrazy Piloto

Deploy da Evolution API no Render para integração com DataCrazy CRM.

## Banco de dados
Neon PostgreSQL (já configurado via variável de ambiente no Render)

## Variáveis de ambiente necessárias no Render
- `SERVER_URL` — URL pública gerada pelo Render
- `DATABASE_CONNECTION_URI` — Connection string do Neon
- `AUTHENTICATION_API_KEY` — Chave de autenticação (gerada automaticamente)
