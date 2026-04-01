from dataclasses import dataclass
from pathlib import Path

from app.core.config import Settings
from app.models.ingest_models import IngestBuildResult, ParsedDocument, ProcessedChunk
from app.services.ingest.chunker import semantic_chunk_text
from app.services.ingest.deduplicator import deduplicate_and_filter
from app.services.ingest.loader import discover_json_sources, load_json_records
from app.services.ingest.parser import parse_records
from app.services.ingest.writer import (
    artifacts_exist,
    ensure_data_dirs,
    load_manifest,
    load_processed_chunks,
    resolve_artifacts,
    write_embeddings,
    write_index,
    write_manifest,
    write_processed_chunks,
)
from app.services.rag.embedder import EmbeddingService
from app.services.rag.pipeline import RAGPipeline, build_generator, generator_signature
from app.services.rag.retriever import Retriever
from app.services.rag.vector_index import FaissIndex


@dataclass
class LoadedRuntime:
    pipeline: RAGPipeline
    chunks_loaded: int
    generator_signature: tuple[str, str, str | None]


class IngestPipeline:
    def __init__(self, settings: Settings):
        self.settings = settings

    def resolve_source_paths(self, requested_paths: list[str] | None = None) -> list[Path]:
        if requested_paths:
            return [Path(path).resolve() for path in requested_paths]

        configured = self.settings.configured_raw_sources
        if configured:
            return [p if p.is_absolute() else (Path.cwd() / p).resolve() for p in configured]

        discovered = discover_json_sources(Path(self.settings.data_raw_dir))
        if discovered:
            return discovered

        return []

    def _chunk_documents(self, parsed_documents: list[ParsedDocument]) -> list[ProcessedChunk]:
        chunk_candidates: list[ProcessedChunk] = []
        for doc in parsed_documents:
            chunks = semantic_chunk_text(
                text=doc.text,
                max_tokens=self.settings.chunk_size_tokens,
                overlap_tokens=self.settings.chunk_overlap_tokens,
            )
            for chunk in chunks:
                chunk_candidates.append(ProcessedChunk(text=chunk, metadata=doc.metadata))
        return chunk_candidates

    def rebuild(self, requested_paths: list[str] | None = None) -> IngestBuildResult:
        ensure_data_dirs(self.settings)
        artifacts = resolve_artifacts(self.settings)
        source_paths = self.resolve_source_paths(requested_paths)
        if not source_paths:
            raise RuntimeError("No JSON sources were found for ingestion.")

        records = load_json_records(source_paths)
        if not records:
            raise RuntimeError("No records found in configured ingestion sources.")

        parsed_documents = parse_records(records)
        if not parsed_documents:
            raise RuntimeError("No valid documents were parsed from raw records.")

        chunk_candidates = self._chunk_documents(parsed_documents)
        chunks = deduplicate_and_filter(
            chunk_candidates=chunk_candidates,
            min_chunk_chars=self.settings.min_chunk_chars,
            min_quality_score_policy=self.settings.min_quality_score_policy,
            min_quality_score_qa=self.settings.min_quality_score_qa,
        )
        if not chunks:
            raise RuntimeError("No valid chunks were produced during ingestion.")

        embedder = EmbeddingService(model_name=self.settings.embedding_model_name)
        embeddings = embedder.encode([chunk.text for chunk in chunks])
        if embeddings.ndim != 2 or embeddings.shape[0] == 0:
            raise RuntimeError("Embedding generation returned invalid shape.")

        vector_index = FaissIndex(dimension=embeddings.shape[1])
        vector_index.add(embeddings)

        write_processed_chunks(artifacts.processed_chunks_path, chunks)
        write_embeddings(artifacts.embeddings_path, embeddings)
        write_index(artifacts.faiss_index_path, vector_index)
        write_manifest(
            artifacts.manifest_path,
            {
                "raw_records": len(records),
                "parsed_documents": len(parsed_documents),
                "chunks": len(chunks),
                "embedding_dimension": int(embeddings.shape[1]),
                "embedding_model_name": self.settings.embedding_model_name,
                "source_files": [str(path) for path in source_paths],
            },
        )

        return IngestBuildResult(
            source_files=source_paths,
            raw_records=len(records),
            parsed_documents=len(parsed_documents),
            chunks=len(chunks),
            embedding_dimension=int(embeddings.shape[1]),
            artifacts=artifacts,
        )

    def load_runtime(self) -> LoadedRuntime | None:
        artifacts = resolve_artifacts(self.settings)
        if not artifacts_exist(artifacts):
            return None

        chunks = load_processed_chunks(artifacts.processed_chunks_path)
        if not chunks:
            return None

        _ = load_manifest(artifacts.manifest_path)
        vector_index = FaissIndex.load(artifacts.faiss_index_path)
        embedder = EmbeddingService(model_name=self.settings.embedding_model_name)
        retriever = Retriever(embedder, vector_index, chunks)
        pipeline = RAGPipeline(retriever=retriever, generator=build_generator(self.settings))
        return LoadedRuntime(
            pipeline=pipeline,
            chunks_loaded=len(chunks),
            generator_signature=generator_signature(self.settings),
        )
