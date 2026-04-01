from typing import Any
from pathlib import Path
import faiss
import numpy as np

class FaissIndex:
    def __init__(self, dimension: int | None = None, index: Any | None = None):
        # FAISS Python bindings often have incomplete/incorrect type stubs in editors.
        # Use `Any` to avoid false-positive call-signature errors from Pylance.
        if index is not None:
            self.index: Any = index
            return
        if dimension is None:
            raise ValueError("dimension is required when creating a new FAISS index.")
        self.index = faiss.IndexFlatIP(dimension)

    @property
    def ntotal(self) -> int:
        return int(self.index.ntotal)

    def add(self, embeddings: np.ndarray) -> None:
        if embeddings.ndim != 2 or embeddings.shape[0] == 0:
            raise ValueError("Embeddings must be a non-empty 2D array.")
        self.index.add(embeddings.astype("float32"))

    def search(self, query_embedding: np.ndarray, k: int = 5) -> tuple[np.ndarray, np.ndarray]:
        if k <= 0:
            raise ValueError("k must be greater than 0.")
        if query_embedding.ndim != 2:
            raise ValueError("Query embedding must be a 2D array.")
        if self.index.ntotal == 0:
            return (
                np.empty((query_embedding.shape[0], 0), dtype=np.float32),
                np.empty((query_embedding.shape[0], 0), dtype=np.int64),
            )

        k_eff = min(k, self.index.ntotal)
        scores, indices = self.index.search(query_embedding.astype("float32"), k_eff)
        return scores, indices

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        faiss.write_index(self.index, str(path))

    @classmethod
    def load(cls, path: Path) -> "FaissIndex":
        index = faiss.read_index(str(path))
        return cls(index=index)
