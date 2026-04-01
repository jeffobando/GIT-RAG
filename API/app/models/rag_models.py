from dataclasses import dataclass
from typing import Any


@dataclass
class RetrievedChunk:
    score: float
    text: str
    metadata: dict[str, Any]


@dataclass
class QueryResult:
    answer: str
    sources: list[RetrievedChunk]
