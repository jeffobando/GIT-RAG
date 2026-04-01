from pathlib import Path

from app.services.rag.pipeline import RAGPipeline


class RAGState:
    def __init__(self) -> None:
        self.pipeline: RAGPipeline | None = None
        self.generator_signature: tuple[str, str, str | None] | None = None
        self.ready: bool = False
        self.chunks_loaded: int = 0
        self.artifacts_manifest_path: Path | None = None
        self.last_error: str | None = None

    def set_runtime(
        self,
        pipeline: RAGPipeline,
        chunks_loaded: int,
        generator_signature: tuple[str, str, str | None],
        artifacts_manifest_path: Path | None = None,
    ) -> None:
        self.pipeline = pipeline
        self.chunks_loaded = chunks_loaded
        self.generator_signature = generator_signature
        self.artifacts_manifest_path = artifacts_manifest_path
        self.ready = True
        self.last_error = None

    def clear(self, error: str | None = None) -> None:
        self.pipeline = None
        self.generator_signature = None
        self.chunks_loaded = 0
        self.ready = False
        self.last_error = error


rag_state = RAGState()
