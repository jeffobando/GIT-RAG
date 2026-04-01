from pydantic import BaseModel, Field


class IngestRebuildRequest(BaseModel):
    source_paths: list[str] | None = Field(
        default=None,
        description="Optional list of JSON source paths to ingest. If omitted, configured defaults are used.",
    )


class IngestRebuildResponse(BaseModel):
    ready: bool
    raw_records: int
    parsed_documents: int
    chunks: int
    embedding_dimension: int
    source_files: list[str]
    processed_chunks_path: str
    embeddings_path: str
    faiss_index_path: str
    manifest_path: str


class IngestStatusResponse(BaseModel):
    ready: bool
    chunks_loaded: int
    index_exists: bool
    processed_chunks_path: str
    embeddings_path: str
    faiss_index_path: str
    manifest_path: str
    llm_provider: str
    llm_model: str


class IngestUploadPolicyResponse(BaseModel):
    uploaded_pdf_path: str
    generated_json_path: str
    generated_chunks: int
