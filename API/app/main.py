from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.evaluations import router as evaluations_router
from app.api.routes.evaluate import router as evaluate_router
from app.api.routes.health import router as health_router
from app.api.routes.ingest import router as ingest_router
from app.api.routes.metrics import router as metrics_router
from app.api.routes.rag import router as rag_router
from app.core.config import get_settings
from app.core.database import init_database
from app.services.ingest.pipeline import IngestPipeline
from app.services.ingest.writer import ensure_data_dirs
from app.state.rag_state import rag_state

@asynccontextmanager
async def lifespan(_: FastAPI):
    settings = get_settings()
    init_database()
    ensure_data_dirs(settings)
    runtime = IngestPipeline(settings).load_runtime()
    if runtime is None:
        rag_state.clear(error="Artifacts not found. Run POST /ingest/rebuild.")
    else:
        rag_state.set_runtime(
            pipeline=runtime.pipeline,
            chunks_loaded=runtime.chunks_loaded,
            generator_signature=runtime.generator_signature,
            artifacts_manifest_path=settings.manifest_path,
        )
    yield

app = FastAPI(title="RAG API", version="0.1.0", lifespan=lifespan)
settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(ingest_router, prefix="/ingest", tags=["ingest"])
app.include_router(rag_router, prefix="/rag", tags=["rag"])
app.include_router(evaluate_router, tags=["evaluation"])
app.include_router(metrics_router, prefix="/metrics", tags=["metrics"])
app.include_router(evaluations_router, prefix="/evaluations", tags=["evaluations"])
app.include_router(health_router, prefix="/health", tags=["health"])
