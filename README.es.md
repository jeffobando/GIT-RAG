# Git-RAG

Proyecto de Retrieval-Augmented Generation (RAG) con:

- Backend FastAPI (`API/`)
- Frontend React + Vite (`UI/`)
- PostgreSQL para observabilidad y métricas de evaluación

## 1. Requisitos previos

- Python 3.11+
- Node.js 18+ y npm
- Docker Desktop (recomendado para PostgreSQL)

## 2. Estructura del proyecto

- `API/`: backend, ingestión, retrieval, evaluación, métricas
- `UI/`: dashboard/frontend del chat

## 3. Configuración de entorno

### API

Desde `API/`, copia el archivo de ejemplo:

```bash
cp .env.example .env
```

O en PowerShell:

```powershell
Copy-Item .env.example .env
```

Ajusta al menos:

- `LLM_PROVIDER` (`openai` o `local`)
- `LLM_MODEL`
- `OPENAI_API_KEY` (obligatoria cuando `LLM_PROVIDER=openai`)
- `DATABASE_URL`
- `CORS_ALLOW_ORIGINS` (si el origen de tu UI es distinto)

### UI

Desde `UI/`, crea el archivo local de entorno:

```bash
cp .env.example .env.local
```

O en PowerShell:

```powershell
Copy-Item .env.example .env.local
```

URL de API usada por defecto en la UI:

- `VITE_API_BASE_URL=http://127.0.0.1:8000`

## 4. Levantar PostgreSQL

Desde `API/`:

```bash
docker compose -f docker-compose.postgres.yml up -d
```

Conexión local por defecto:

`postgresql+psycopg://rag_user:rag_password@localhost:5432/rag_db`

Notas:

- Las tablas se crean automáticamente al iniciar la API si `DATABASE_URL` está configurada.
- Las migraciones SQL opcionales están en `API/migrations/`.

## 5. Levantar la API

Desde `API/`:

1. Crea y activa un entorno virtual
2. Instala las dependencias de `pyproject.toml`
3. Inicia el servidor

Ejemplo:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install fastapi "uvicorn[standard]" pydantic-settings sqlalchemy "psycopg[binary]" numpy faiss-cpu sentence-transformers openai pypdf ftfy python-multipart
uvicorn app.main:app --reload
```

Activación en PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

URL base de la API:

- `http://127.0.0.1:8000`

Health check:

- `GET http://127.0.0.1:8000/health/`

## 6. Construir / reconstruir artefactos de ingestión

Con la API en ejecución, reconstruye los artefactos:

- `POST /ingest/rebuild`

Endpoints útiles:

- `GET /ingest/status`
- `POST /ingest/upload-policy` (sube PDF y lo convierte a JSON)

Fuente de verdad para ingestión:

- `API/app/data/raw/*.json`

## 7. Levantar la UI

Desde `UI/`:

```bash
npm install
npm run dev
```

URL de la UI:

- `http://127.0.0.1:5173`

## 8. Endpoints principales

- `POST /rag/query`
- `POST /evaluate`
- `POST /evaluate/base`
- `GET /metrics/summary`
- `GET /metrics/compare?left_run_type=rag&right_run_type=base`
- `GET /evaluations/runs`

## 9. Script de benchmark (opcional)

Desde `API/`:

```bash
python scripts/benchmark_rag_vs_base.py --questions scripts/questions.sample.jsonl --k 5 --workers 4 --csv-out benchmark_results.csv
```

Benchmark etiquetado:

```bash
python scripts/benchmark_rag_vs_base.py --questions scripts/questions.labeled.sample.jsonl --k 5 --local-mode --csv-out benchmark_results_labeled.csv
```

## 10. Secrets y seguridad

No subas credenciales reales al repositorio.

Secrets recomendados en GitHub:

- `OPENAI_API_KEY`
- `DATABASE_URL`
- `HF_TOKEN` (opcional)

Mantén secretos solo en archivos `.env` locales o en GitHub Secrets.
