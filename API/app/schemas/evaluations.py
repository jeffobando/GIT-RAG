from pydantic import BaseModel


class EvaluationRunResponse(BaseModel):
    id: str
    name: str | None = None
    created_at: str | None = None
    status: str | None = None
    score: float | None = None
    run_type: str | None = None
    recall_at_k: float | None = None
    mrr: float | None = None
    hit_at_k: float | None = None
    ndcg_at_k: float | None = None
    faithfulness: float | None = None
    answer_relevance: float | None = None
