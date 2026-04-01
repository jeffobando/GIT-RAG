from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.core.config import reload_settings
from app.schemas.ingest import (
    IngestRebuildRequest,
    IngestRebuildResponse,
    IngestStatusResponse,
    IngestUploadPolicyResponse,
)
from app.services.ingest.pipeline import IngestPipeline
from app.services.ingest.policy_pdf import generate_policy_json_from_pdf
from app.services.ingest.writer import ensure_data_dirs
from app.state.rag_state import rag_state


router = APIRouter()


@router.post("/rebuild", response_model=IngestRebuildResponse)
def ingest_rebuild(payload: IngestRebuildRequest) -> IngestRebuildResponse:
    settings = reload_settings()
    ingest_pipeline = IngestPipeline(settings)

    try:
        build_result = ingest_pipeline.rebuild(payload.source_paths)
        runtime = ingest_pipeline.load_runtime()
        if runtime is None:
            raise RuntimeError("Ingestion succeeded but runtime artifacts could not be loaded.")
    except Exception as exc:  # noqa: BLE001
        rag_state.clear(error=str(exc))
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {exc}") from exc

    rag_state.set_runtime(
        pipeline=runtime.pipeline,
        chunks_loaded=runtime.chunks_loaded,
        generator_signature=runtime.generator_signature,
        artifacts_manifest_path=build_result.artifacts.manifest_path,
    )

    return IngestRebuildResponse(
        ready=rag_state.ready,
        raw_records=build_result.raw_records,
        parsed_documents=build_result.parsed_documents,
        chunks=build_result.chunks,
        embedding_dimension=build_result.embedding_dimension,
        source_files=[str(path) for path in build_result.source_files],
        processed_chunks_path=str(build_result.artifacts.processed_chunks_path),
        embeddings_path=str(build_result.artifacts.embeddings_path),
        faiss_index_path=str(build_result.artifacts.faiss_index_path),
        manifest_path=str(build_result.artifacts.manifest_path),
    )


@router.get("/status", response_model=IngestStatusResponse)
def ingest_status() -> IngestStatusResponse:
    settings = reload_settings()
    return IngestStatusResponse(
        ready=rag_state.ready,
        chunks_loaded=rag_state.chunks_loaded,
        index_exists=settings.faiss_index_path.exists(),
        processed_chunks_path=str(settings.processed_chunks_path),
        embeddings_path=str(settings.embeddings_path),
        faiss_index_path=str(settings.faiss_index_path),
        manifest_path=str(settings.manifest_path),
        llm_provider=settings.llm_provider,
        llm_model=settings.llm_model,
    )


@router.post("/upload-policy", response_model=IngestUploadPolicyResponse)
def upload_policy_pdf(file: UploadFile = File(...)) -> IngestUploadPolicyResponse:
    settings = reload_settings()
    ensure_data_dirs(settings)

    filename = Path(file.filename or "").name
    if not filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted.")

    upload_dir = settings.policy_upload_dir
    upload_dir.mkdir(parents=True, exist_ok=True)
    uploaded_pdf_path = upload_dir / filename
    uploaded_pdf_path.write_bytes(file.file.read())

    try:
        generated_chunks = generate_policy_json_from_pdf(
            pdf_path=uploaded_pdf_path,
            output_json_path=settings.uploaded_policy_json_path,
        )
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=f"Failed to process uploaded PDF: {exc}") from exc

    return IngestUploadPolicyResponse(
        uploaded_pdf_path=str(uploaded_pdf_path),
        generated_json_path=str(settings.uploaded_policy_json_path),
        generated_chunks=generated_chunks,
    )
