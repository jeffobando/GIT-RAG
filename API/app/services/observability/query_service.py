from sqlalchemy import Select, case, func, select
from sqlalchemy.orm import Session

from app.models.observability_models import RagEvaluationORM, RagQueryORM
from app.schemas.evaluations import EvaluationRunResponse
from app.schemas.metrics import MetricsCompareResponse, MetricsSummaryResponse, RunTypeMetrics


def read_metrics_summary(db: Session) -> MetricsSummaryResponse:
    stmt: Select = select(
        func.count(RagQueryORM.id),
        func.avg(RagQueryORM.total_latency_ms),
        func.avg(RagQueryORM.retrieval_latency_ms),
        func.avg(RagQueryORM.generation_latency_ms),
        func.avg(case((RagQueryORM.insufficient_context.is_(True), 1.0), else_=0.0)),
        func.avg(case((RagQueryORM.had_error.is_(True), 1.0), else_=0.0)),
    )
    (
        total_queries,
        avg_total_latency,
        avg_retrieval_latency,
        avg_generation_latency,
        insufficient_context_rate,
        error_rate,
    ) = db.execute(stmt).one()

    return MetricsSummaryResponse(
        total_queries=int(total_queries or 0),
        avg_total_latency_ms=float(avg_total_latency or 0.0),
        avg_retrieval_latency_ms=float(avg_retrieval_latency or 0.0),
        avg_generation_latency_ms=float(avg_generation_latency or 0.0),
        insufficient_context_rate=float(insufficient_context_rate or 0.0),
        error_rate=float(error_rate or 0.0),
    )


def read_evaluation_runs(db: Session, limit: int = 100) -> list[EvaluationRunResponse]:
    stmt: Select = (
        select(RagEvaluationORM, RagQueryORM)
        .join(RagQueryORM, RagEvaluationORM.query_id == RagQueryORM.id)
        .order_by(RagEvaluationORM.evaluation_timestamp.desc())
        .limit(limit)
    )
    rows = db.execute(stmt).all()

    runs: list[EvaluationRunResponse] = []
    for evaluation, query in rows:
        score_components = [
            value
            for value in [
                evaluation.recall_at_k,
                evaluation.mrr,
                evaluation.hit_at_k,
                evaluation.ndcg_at_k,
                evaluation.faithfulness,
                evaluation.answer_relevance,
            ]
            if value is not None
        ]
        score = float(sum(score_components) / len(score_components)) if score_components else None
        runs.append(
            EvaluationRunResponse(
                id=evaluation.id,
                name=f"Eval: {query.query_text[:60]}",
                created_at=evaluation.evaluation_timestamp.isoformat(),
                status="completed",
                score=score,
                run_type=query.run_type,
                recall_at_k=evaluation.recall_at_k,
                mrr=evaluation.mrr,
                hit_at_k=evaluation.hit_at_k,
                ndcg_at_k=evaluation.ndcg_at_k,
                faithfulness=evaluation.faithfulness,
                answer_relevance=evaluation.answer_relevance,
            )
        )
    return runs


def _aggregate_run_type(db: Session, run_type: str) -> RunTypeMetrics:
    stmt: Select = (
        select(
            func.count(RagQueryORM.id),
            func.avg(RagEvaluationORM.recall_at_k),
            func.avg(RagEvaluationORM.mrr),
            func.avg(RagEvaluationORM.hit_at_k),
            func.avg(RagEvaluationORM.ndcg_at_k),
            func.avg(RagEvaluationORM.faithfulness),
            func.avg(RagEvaluationORM.answer_relevance),
            func.avg(RagQueryORM.total_latency_ms),
        )
        .join(RagEvaluationORM, RagEvaluationORM.query_id == RagQueryORM.id)
        .where(RagQueryORM.run_type == run_type)
    )
    (
        samples,
        avg_recall,
        avg_mrr,
        avg_hit,
        avg_ndcg,
        avg_faithfulness,
        avg_answer_relevance,
        avg_latency,
    ) = db.execute(stmt).one()

    score_values = [
        float(v)
        for v in [avg_recall, avg_mrr, avg_hit, avg_ndcg, avg_faithfulness, avg_answer_relevance]
        if v is not None
    ]
    avg_score = (sum(score_values) / len(score_values)) if score_values else None

    return RunTypeMetrics(
        run_type=run_type,
        samples=int(samples or 0),
        avg_score=avg_score,
        avg_recall_at_k=float(avg_recall) if avg_recall is not None else None,
        avg_mrr=float(avg_mrr) if avg_mrr is not None else None,
        avg_hit_at_k=float(avg_hit) if avg_hit is not None else None,
        avg_ndcg_at_k=float(avg_ndcg) if avg_ndcg is not None else None,
        avg_faithfulness=float(avg_faithfulness) if avg_faithfulness is not None else None,
        avg_answer_relevance=float(avg_answer_relevance) if avg_answer_relevance is not None else None,
        avg_total_latency_ms=float(avg_latency) if avg_latency is not None else None,
    )


def read_metrics_compare(db: Session, left_run_type: str, right_run_type: str) -> MetricsCompareResponse:
    left = _aggregate_run_type(db, left_run_type)
    right = _aggregate_run_type(db, right_run_type)
    return MetricsCompareResponse(left=left, right=right)
