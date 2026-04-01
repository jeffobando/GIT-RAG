import hashlib
from dataclasses import dataclass
from typing import Any

from time import perf_counter

from sqlalchemy.orm import Session

from app.core.config import Settings
from app.schemas.evaluation import EvaluateRequest, EvaluationMetricsResponse, EvaluateResponse, RetrievedDocument
from app.schemas.rag import RetrievedChunk
from app.services.evaluation.metrics import compute_metrics
from app.services.observability.repository import EvaluationRecord, ObservabilityRepository, RetrievalRecord
from app.services.rag.query_service import execute_base_query, execute_rag_query


def _stable_chunk_id(text: str, metadata: dict[str, Any], rank: int) -> str:
    metadata_fingerprint = "|".join(
        [
            str(metadata.get("document_title", "")),
            str(metadata.get("section_title", "")),
            str(metadata.get("source_type", "")),
            str(metadata.get("category", "")),
        ]
    )
    payload = f"{metadata_fingerprint}|{text}|{rank}".encode("utf-8")
    return hashlib.sha1(payload).hexdigest()[:24]


@dataclass
class EvaluatedResult:
    query_id: str
    evaluation_id: str
    top_k: int
    answer: str
    retrieved_documents: list[RetrievedDocument]
    sources: list[RetrievedChunk]
    metrics: EvaluationMetricsResponse


class EvaluateService:
    def __init__(self, settings: Settings, db: Session):
        self.settings = settings
        self.repo = ObservabilityRepository(db)

    def _evaluate_common(self, payload: EvaluateRequest, query_result: dict, top_k: int) -> EvaluatedResult:
        answer = str(query_result.get("answer", "")).strip()
        sources = [RetrievedChunk.model_validate(item) for item in list(query_result.get("sources", []))]

        query_row = self.repo.create_query(
            query_text=payload.query,
            answer_text=answer,
            top_k=top_k,
            run_type=payload.run_type,
            source_type=payload.source_type,
            total_latency_ms=float(query_result.get("total_latency_ms", 0.0)),
            retrieval_latency_ms=float(query_result.get("retrieval_latency_ms", 0.0)),
            generation_latency_ms=float(query_result.get("generation_latency_ms", 0.0)),
            insufficient_context=len(sources) == 0,
            had_error=False,
            metadata=payload.metadata,
        )

        retrieved_documents: list[RetrievedDocument] = []
        retrieval_records: list[RetrievalRecord] = []
        for idx, source in enumerate(sources, start=1):
            metadata = source.metadata or {}
            chunk_id = str(metadata.get("chunk_id") or _stable_chunk_id(source.text, metadata, idx))
            retrieved_documents.append(
                RetrievedDocument(
                    chunk_id=chunk_id,
                    rank=idx,
                    score=source.score,
                    text=source.text,
                    metadata=metadata,
                )
            )
            retrieval_records.append(
                RetrievalRecord(
                    chunk_id=chunk_id,
                    rank=idx,
                    similarity_score=float(source.score),
                    retrieved_text=source.text,
                    source_file=metadata.get("source_file"),
                    source_type=metadata.get("source_type"),
                    metadata=metadata,
                )
            )
        self.repo.create_retrievals(query_id=query_row.id, retrievals=retrieval_records)

        metric_scores = compute_metrics(
            query_text=payload.query,
            answer_text=answer,
            retrieved_chunk_ids=[doc.chunk_id for doc in retrieved_documents],
            retrieved_texts=[doc.text for doc in retrieved_documents],
            relevant_chunk_ids=payload.relevant_chunk_ids or None,
        )
        evaluation = self.repo.create_evaluation(
            query_id=query_row.id,
            record=EvaluationRecord(
                recall_at_k=metric_scores.recall_at_k,
                mrr=metric_scores.mrr,
                hit_at_k=metric_scores.hit_at_k,
                ndcg_at_k=metric_scores.ndcg_at_k,
                faithfulness=metric_scores.faithfulness,
                answer_relevance=metric_scores.answer_relevance,
                evaluator_version=payload.evaluator_version or metric_scores.evaluator_version,
                notes=payload.notes,
            ),
        )

        metrics = EvaluationMetricsResponse(
            recall_at_k=evaluation.recall_at_k,
            mrr=evaluation.mrr,
            hit_at_k=evaluation.hit_at_k,
            ndcg_at_k=evaluation.ndcg_at_k,
            faithfulness=evaluation.faithfulness,
            answer_relevance=evaluation.answer_relevance,
            evaluator_version=evaluation.evaluator_version,
        )
        return EvaluatedResult(
            query_id=query_row.id,
            evaluation_id=evaluation.id,
            top_k=top_k,
            answer=answer,
            retrieved_documents=retrieved_documents,
            sources=sources,
            metrics=metrics,
        )

    def evaluate(self, payload: EvaluateRequest) -> EvaluatedResult:
        top_k = payload.k or self.settings.default_top_k
        query_result = execute_rag_query(self.settings, payload.query, top_k)
        return self._evaluate_common(payload=payload, query_result=query_result, top_k=top_k)

    def evaluate_base(self, payload: EvaluateRequest) -> EvaluatedResult:
        top_k = payload.k or self.settings.default_top_k
        generation_start = perf_counter()
        query_result = execute_base_query(self.settings, payload.query)
        generation_latency_ms = (perf_counter() - generation_start) * 1000
        query_result["generation_latency_ms"] = generation_latency_ms
        query_result["total_latency_ms"] = generation_latency_ms
        query_result["retrieval_latency_ms"] = 0.0
        return self._evaluate_common(payload=payload, query_result=query_result, top_k=top_k)

    def evaluate_response(self, payload: EvaluateRequest) -> EvaluateResponse:
        evaluated = self.evaluate(payload)
        return EvaluateResponse(
            query_id=evaluated.query_id,
            evaluation_id=evaluated.evaluation_id,
            query=payload.query,
            answer=evaluated.answer,
            top_k=evaluated.top_k,
            retrieved_documents=evaluated.retrieved_documents,
            sources=evaluated.sources,
            metrics=evaluated.metrics,
        )

    def evaluate_base_response(self, payload: EvaluateRequest) -> EvaluateResponse:
        effective_payload = payload.model_copy(
            update={
                "run_type": payload.run_type or "base",
                "source_type": payload.source_type or "base",
            }
        )
        evaluated = self.evaluate_base(effective_payload)
        return EvaluateResponse(
            query_id=evaluated.query_id,
            evaluation_id=evaluated.evaluation_id,
            query=effective_payload.query,
            answer=evaluated.answer,
            top_k=evaluated.top_k,
            retrieved_documents=evaluated.retrieved_documents,
            sources=evaluated.sources,
            metrics=evaluated.metrics,
        )
