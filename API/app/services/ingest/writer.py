import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import numpy as np

from app.core.config import Settings
from app.models.ingest_models import IngestArtifacts, ProcessedChunk
from app.services.rag.vector_index import FaissIndex


def resolve_artifacts(settings: Settings) -> IngestArtifacts:
    return IngestArtifacts(
        processed_chunks_path=settings.processed_chunks_path,
        embeddings_path=settings.embeddings_path,
        faiss_index_path=settings.faiss_index_path,
        manifest_path=settings.manifest_path,
    )


def ensure_data_dirs(settings: Settings) -> None:
    Path(settings.data_raw_dir).mkdir(parents=True, exist_ok=True)
    Path(settings.data_processed_dir).mkdir(parents=True, exist_ok=True)
    Path(settings.data_indexes_dir).mkdir(parents=True, exist_ok=True)


def write_processed_chunks(path: Path, chunks: list[ProcessedChunk]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    serializable = [{"text": c.text, "metadata": c.metadata} for c in chunks]
    with path.open("w", encoding="utf-8") as file_handle:
        json.dump(serializable, file_handle, ensure_ascii=False, indent=2)


def write_embeddings(path: Path, embeddings: np.ndarray) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    np.save(path, embeddings.astype("float32"))


def write_index(path: Path, index: FaissIndex) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    index.save(path)


def write_manifest(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    manifest = {
        **payload,
        "updated_at_utc": datetime.now(UTC).isoformat(),
    }
    with path.open("w", encoding="utf-8") as file_handle:
        json.dump(manifest, file_handle, ensure_ascii=False, indent=2)


def load_processed_chunks(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8-sig") as file_handle:
        loaded = json.load(file_handle)
    if not isinstance(loaded, list):
        return []
    return [item for item in loaded if isinstance(item, dict)]


def load_embeddings(path: Path) -> np.ndarray:
    return np.load(path)


def load_manifest(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as file_handle:
        loaded = json.load(file_handle)
    return loaded if isinstance(loaded, dict) else {}


def artifacts_exist(artifacts: IngestArtifacts) -> bool:
    return (
        artifacts.processed_chunks_path.exists()
        and artifacts.embeddings_path.exists()
        and artifacts.faiss_index_path.exists()
    )
