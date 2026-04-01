from typing import Any

from pydantic import BaseModel, Field

from app.schemas.rag import RetrievedChunk


class EvaluateRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=4000)
    k: int | None = Field(default=None, ge=1, le=20)
    run_type: str | None = Field(default="interactive")
    source_type: str | None = Field(default="rag")
    relevant_chunk_ids: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    notes: str | None = None
    evaluator_version: str | None = None


class RetrievedDocument(BaseModel):
    chunk_id: str
    rank: int
    score: float
    text: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class EvaluationMetricsResponse(BaseModel):
    recall_at_k: float | None = None
    mrr: float | None = None
    hit_at_k: float | None = None
    ndcg_at_k: float | None = None
    faithfulness: float | None = None
    answer_relevance: float | None = None
    evaluator_version: str | None = None


class EvaluateResponse(BaseModel):
    query_id: str
    evaluation_id: str
    query: str
    answer: str
    top_k: int
    retrieved_documents: list[RetrievedDocument] = Field(default_factory=list)
    sources: list[RetrievedChunk] = Field(default_factory=list)
    metrics: EvaluationMetricsResponse
