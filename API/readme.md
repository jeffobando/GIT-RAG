Run API:

`uvicorn app.main:app --reload`

PostgreSQL (Docker, recommended):

1. Start PostgreSQL:

`docker compose -f docker-compose.postgres.yml up -d`

2. Set DB URL in `API/.env`:

`DATABASE_URL=postgresql+psycopg://rag_user:rag_password@localhost:5432/rag_db`

3. Optional manual SQL migration:

PowerShell:
`$env:DATABASE_URL="postgresql+psycopg://rag_user:rag_password@localhost:5432/rag_db"; psql $env:DATABASE_URL -f migrations/001_initial_observability.sql`

Bash:
`DATABASE_URL=postgresql+psycopg://rag_user:rag_password@localhost:5432/rag_db psql "$DATABASE_URL" -f migrations/001_initial_observability.sql`

If your DB already existed before `hit_at_k` and `ndcg_at_k`:

PowerShell:
`$env:DATABASE_URL="postgresql+psycopg://rag_user:rag_password@localhost:5432/rag_db"; psql $env:DATABASE_URL -f migrations/002_add_hit_ndcg.sql`

Bash:
`DATABASE_URL=postgresql+psycopg://rag_user:rag_password@localhost:5432/rag_db psql "$DATABASE_URL" -f migrations/002_add_hit_ndcg.sql`

Note:
- The API creates tables automatically on startup when `DATABASE_URL` is set.
- `API/.env.db.example` includes the default local connection string.
- Use `API/.env.example` as template for local configuration.

GitHub Secrets (recommended before pushing/deploying):

- `OPENAI_API_KEY`: required when `LLM_PROVIDER=openai`.
- `DATABASE_URL`: required for persistent observability/evaluation storage.
- `HF_TOKEN` (optional): enables authenticated downloads and higher limits for Hugging Face models.

Security checklist before pushing:

- Keep real credentials only in local `.env` (ignored by git) or GitHub Secrets.
- Never commit API keys, tokens, or production credentials in tracked files.

Build ingestion artifacts:

`POST /ingest/rebuild`

Ingestion source of truth:

- `API/app/data/raw/*.json` (no legacy fallback directories)

Check ingestion status:

`GET /ingest/status`

Upload and convert policy PDF (internal converter in API, no external `INGEST/` dependency):

`POST /ingest/upload-policy`

Query RAG:

`POST /rag/query`

Evaluate and persist query/retrieval/metrics:

`POST /evaluate`

Evaluate baseline without retrieval:

`POST /evaluate/base`

Metrics summary (for UI dashboard):

`GET /metrics/summary`

Metrics comparison by run type (example: rag vs base):

`GET /metrics/compare?left_run_type=rag&right_run_type=base`

Batch benchmark script (rag vs base):

`python scripts/benchmark_rag_vs_base.py --questions scripts/questions.sample.jsonl --k 5 --workers 4 --csv-out benchmark_results.csv`

For local models (to reduce timeouts), run with lower concurrency and higher timeout:

`python scripts/benchmark_rag_vs_base.py --questions scripts/questions.sample.jsonl --k 5 --workers 1 --timeout 300 --retries 2 --retry-delay 2 --csv-out benchmark_results.csv`

Or use local mode auto-tuning:

`python scripts/benchmark_rag_vs_base.py --questions scripts/questions.sample.jsonl --k 5 --local-mode --csv-out benchmark_results.csv`

Labeled benchmark (recommended for fair comparison):

`python scripts/benchmark_rag_vs_base.py --questions scripts/questions.labeled.sample.jsonl --k 5 --local-mode --csv-out benchmark_results_labeled.csv`

Evaluation runs (for UI table):

`GET /evaluations/runs`

Health:

`GET /health/`
