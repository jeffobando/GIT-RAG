from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


APP_DIR = Path(__file__).resolve().parents[1]
API_DIR = APP_DIR.parents[0]
REPO_ROOT = API_DIR.parents[0]


class Settings(BaseSettings):
    app_name: str = "RAG API"
    app_version: str = "0.1.0"

    llm_provider: str = "local"
    llm_model: str = "Qwen/Qwen2.5-1.5B-Instruct"
    openai_api_key: str | None = None
    cors_allow_origins: str = "http://localhost:5173,http://127.0.0.1:5173"

    embedding_model_name: str = "sentence-transformers/all-MiniLM-L6-v2"
    default_top_k: int = 5
    generation_input_max_tokens: int = 3072
    generation_max_new_tokens: int = 320

    chunk_size_tokens: int = 120
    chunk_overlap_tokens: int = 20
    min_chunk_chars: int = 50
    min_quality_score_policy: int = 2
    min_quality_score_qa: int = 3

    # Raw source JSONs to ingest. If empty, all *.json in data_raw_dir are used.
    raw_source_files: str = ""

    data_raw_dir: str = str(REPO_ROOT / "API" / "app" / "data" / "raw")
    data_processed_dir: str = str(REPO_ROOT / "API" / "app" / "data" / "processed")
    data_indexes_dir: str = str(REPO_ROOT / "API" / "app" / "data" / "indexes")

    vector_db_url: str | None = None
    database_url: str | None = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def processed_chunks_path(self) -> Path:
        return Path(self.data_processed_dir) / "processed_chunks.json"

    @property
    def embeddings_path(self) -> Path:
        return Path(self.data_processed_dir) / "embeddings.npy"

    @property
    def faiss_index_path(self) -> Path:
        return Path(self.data_indexes_dir) / "faiss.index"

    @property
    def manifest_path(self) -> Path:
        return Path(self.data_indexes_dir) / "artifacts_manifest.json"

    @property
    def configured_raw_sources(self) -> list[Path]:
        if not self.raw_source_files.strip():
            return []
        return [Path(p.strip()) for p in self.raw_source_files.split(",") if p.strip()]

    @property
    def cors_origins(self) -> list[str]:
        origins = [origin.strip() for origin in self.cors_allow_origins.split(",")]
        return [origin for origin in origins if origin]

    @property
    def policy_upload_dir(self) -> Path:
        return Path(self.data_raw_dir) / "policies"

    @property
    def uploaded_policy_json_path(self) -> Path:
        return Path(self.data_raw_dir) / "corporate_policy_uploaded_rag.json"


@lru_cache
def get_settings() -> Settings:
    return Settings()


def reload_settings() -> Settings:
    get_settings.cache_clear()
    return get_settings()
