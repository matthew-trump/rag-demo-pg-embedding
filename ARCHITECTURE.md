# Architecture

## Components (minimal RAG)

1. **FastAPI service** (single container)
   - Ingest: chunk → embed → store (Postgres/pg_embedding)
   - Ask: embed question → retrieve top-k → generate answer → return citations

2. **Postgres + pg_embedding**
   - Stores documents, chunks, and chunk embeddings.
   - Retrieval is a single SQL query using pg_embedding distance ordering.
   - pg_embedding is archived/deprecated by Neon; prefer pgvector for new work.

## Data flow

### Ingest
1. `POST /ingest` (text + optional metadata)
2. Chunking (fixed-size + overlap)
3. Embeddings
4. Insert `documents` row
5. Insert N `chunks` rows with `embedding`

### Ask
1. `POST /ask` (question)
2. Embed question
3. Retrieve top-k similar chunks
4. Build prompt with:
   - instructions
   - retrieved context (with citations)
   - question
5. Call the LLM
6. Return answer + citations (chunk ids + sources)

## Storage

Tables:
- `documents(id, source, metadata, created_at)`
- `chunks(id, document_id, chunk_index, content, embedding, created_at)`

Index:
- pg_embedding HNSW index on `chunks.embedding` (created when possible).

## Deployments

### Local dev
- Postgres via `docker compose`
- API via `uvicorn` (or via docker compose)

### AWS
- ECR repo for container image
- ECS cluster + Fargate service
- ALB public endpoint
- RDS Postgres in private subnets
- Secrets Manager for DB password
- SSM / env vars for non-secret config
