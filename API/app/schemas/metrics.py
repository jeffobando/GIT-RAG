from pydantic import BaseModel


class MetricsSummaryResponse(BaseModel):
    total_queries: int
    avg_total_latency_ms: float
    avg_retrieval_latency_ms: float
    avg_generation_latency_ms: float
    insufficient_context_rate: float
    error_rate: float


class RunTypeMetrics(BaseModel):
    run_type: str
    samples: int
    avg_score: float | None = None
    avg_recall_at_k: float | None = None
    avg_mrr: float | None = None
    avg_hit_at_k: float | None = None
    avg_ndcg_at_k: float | None = None
    avg_faithfulness: float | None = None
    avg_answer_relevance: float | None = None
    avg_total_latency_ms: float | None = None


class MetricsCompareResponse(BaseModel):
    left: RunTypeMetrics
    right: RunTypeMetrics
