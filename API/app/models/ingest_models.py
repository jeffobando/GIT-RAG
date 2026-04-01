from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class ParsedDocument:
    text: str
    metadata: dict[str, Any]


@dataclass
class ProcessedChunk:
    text: str
    metadata: dict[str, Any]


@dataclass
class IngestArtifacts:
    processed_chunks_path: Path
    embeddings_path: Path
    faiss_index_path: Path
    manifest_path: Path


@dataclass
class IngestBuildResult:
    source_files: list[Path]
    raw_records: int
    parsed_documents: int
    chunks: int
    embedding_dimension: int
    artifacts: IngestArtifacts
