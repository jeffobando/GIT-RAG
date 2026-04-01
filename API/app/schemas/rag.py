from typing import Any

from pydantic import BaseModel, Field


class RetrievedChunk(BaseModel):
    score: float
    text: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class RagQueryRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=4000)
    k: int | None = Field(default=None, ge=1, le=20)


class RagQueryResponse(BaseModel):
    answer: str
    sources: list[RetrievedChunk] = Field(default_factory=list)
