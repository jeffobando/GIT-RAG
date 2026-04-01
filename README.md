# Git-RAG

Retrieval-Augmented Generation (RAG) project with:

- FastAPI backend (`API/`)
- React + Vite frontend (`UI/`)
- PostgreSQL for observability/evaluation metrics

## 1. Prerequisites

- Python 3.11+
- Node.js 18+ and npm
- Docker Desktop (recommended for PostgreSQL)

## 2. Project Structure

- `API/`: backend, ingestion, retrieval, evaluation, metrics
- `UI/`: frontend dashboard/chat app

## 3. Environment Setup

### API

From `API/`, copy the example file:

```bash
cp .env.example .env
```

Or on PowerShell:

```powershell
Copy-Item .env.example .env
```

Update at least:

- `LLM_PROVIDER` (`openai` or `local`)
- `LLM_MODEL`
- `OPENAI_API_KEY` (required when `LLM_PROVIDER=openai`)
- `DATABASE_URL`
- `CORS_ALLOW_ORIGINS` (if your UI origin is different)

### UI

From `UI/`, create local env file:

```bash
cp .env.example .env.local
```

Or on PowerShell:

```powershell
Copy-Item .env.example .env.local
```

Default API URL used by UI:

- `VITE_API_BASE_URL=http://127.0.0.1:8000`

## 4. Run PostgreSQL

From `API/`:

```bash
docker compose -f docker-compose.postgres.yml up -d
```

Default local connection:

`postgresql+psycopg://rag_user:rag_password@localhost:5432/rag_db`

Notes:

- Tables are auto-created on API startup when `DATABASE_URL` is configured.
- Optional SQL migrations live in `API/migrations/`.

## 5. Run the API

From `API/`:

1. Create and activate a virtual environment
2. Install dependencies from `pyproject.toml`
3. Start server

Example:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install fastapi "uvicorn[standard]" pydantic-settings sqlalchemy "psycopg[binary]" numpy faiss-cpu sentence-transformers openai pypdf ftfy python-multipart
uvicorn app.main:app --reload
```

PowerShell activation:

```powershell
.venv\Scripts\Activate.ps1
```

API base URL:

- `http://127.0.0.1:8000`

Health check:

- `GET http://127.0.0.1:8000/health/`

## 6. Build / Rebuild Ingestion Artifacts

Once the API is running, rebuild artifacts:

- `POST /ingest/rebuild`

Useful endpoints:

- `GET /ingest/status`
- `POST /ingest/upload-policy` (upload PDF, convert to JSON)

Source-of-truth ingestion data:

- `API/app/data/raw/*.json`

## 7. Run the UI

From `UI/`:

```bash
npm install
npm run dev
```

UI URL:

- `http://127.0.0.1:5173`

## 8. Main Endpoints

- `POST /rag/query`
- `POST /evaluate`
- `POST /evaluate/base`
- `GET /metrics/summary`
- `GET /metrics/compare?left_run_type=rag&right_run_type=base`
- `GET /evaluations/runs`

## 9. Benchmark Script (Optional)

From `API/`:

```bash
python scripts/benchmark_rag_vs_base.py --questions scripts/questions.sample.jsonl --k 5 --workers 4 --csv-out benchmark_results.csv
```

Labeled benchmark:

```bash
python scripts/benchmark_rag_vs_base.py --questions scripts/questions.labeled.sample.jsonl --k 5 --local-mode --csv-out benchmark_results_labeled.csv
```

## 10. Secrets and Security

Do not commit real credentials.

Recommended GitHub Secrets:

- `OPENAI_API_KEY`
- `DATABASE_URL`
- `HF_TOKEN` (optional)

Keep secrets in local `.env` files or GitHub Secrets only.
