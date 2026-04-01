from dataclasses import dataclass
from typing import Any

from sqlalchemy.orm import Session

from app.models.observability_models import RagEvaluationORM, RagQueryORM, RagRetrievalORM


@dataclass
class RetrievalRecord:
    chunk_id: str
    rank: int
    similarity_score: float
    retrieved_text: str | None
    source_file: str | None
    source_type: str | None
    metadata: dict[str, Any]


@dataclass
class EvaluationRecord:
    recall_at_k: float | None
    mrr: float | None
    hit_at_k: float | None
    ndcg_at_k: float | None
    faithfulness: float | None
    answer_relevance: float | None
    evaluator_version: str | None
    notes: str | None


class ObservabilityRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_query(
        self,
        query_text: str,
        answer_text: str,
        top_k: int,
        run_type: str | None,
        source_type: str | None,
        total_latency_ms: float | None = None,
        retrieval_latency_ms: float | None = None,
        generation_latency_ms: float | None = None,
        insufficient_context: bool = False,
        had_error: bool = False,
        metadata: dict[str, Any] | None = None,
    ) -> RagQueryORM:
        row = RagQueryORM(
            query_text=query_text,
            answer_text=answer_text,
            top_k=top_k,
            run_type=run_type,
            source_type=source_type,
            total_latency_ms=total_latency_ms,
            retrieval_latency_ms=retrieval_latency_ms,
            generation_latency_ms=generation_latency_ms,
            insufficient_context=insufficient_context,
            had_error=had_error,
            metadata_json=metadata or {},
        )
        self.db.add(row)
        self.db.flush()
        return row

    def create_retrievals(self, query_id: str, retrievals: list[RetrievalRecord]) -> list[RagRetrievalORM]:
        rows: list[RagRetrievalORM] = []
        for retrieval in retrievals:
            row = RagRetrievalORM(
                query_id=query_id,
                chunk_id=retrieval.chunk_id,
                rank=retrieval.rank,
                similarity_score=retrieval.similarity_score,
                retrieved_text=retrieval.retrieved_text,
                source_file=retrieval.source_file,
                source_type=retrieval.source_type,
                metadata_json=retrieval.metadata,
            )
            self.db.add(row)
            rows.append(row)
        self.db.flush()
        return rows

    def create_evaluation(self, query_id: str, record: EvaluationRecord) -> RagEvaluationORM:
        row = RagEvaluationORM(
            query_id=query_id,
            recall_at_k=record.recall_at_k,
            mrr=record.mrr,
            hit_at_k=record.hit_at_k,
            ndcg_at_k=record.ndcg_at_k,
            faithfulness=record.faithfulness,
            answer_relevance=record.answer_relevance,
            evaluator_version=record.evaluator_version,
            notes=record.notes,
        )
        self.db.add(row)
        self.db.flush()
        return row
