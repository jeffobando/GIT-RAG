import re
import unicodedata
from dataclasses import dataclass
from math import log2


def _normalize(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", text)
    return "".join(ch for ch in normalized if not unicodedata.combining(ch))


def _tokenize(text: str) -> set[str]:
    tokens = re.findall(r"[a-zA-Z0-9_-]+", _normalize(text).lower())
    return {token for token in tokens if len(token) > 2}


def _safe_overlap_ratio(left: set[str], right: set[str]) -> float:
    if not left or not right:
        return 0.0
    return len(left & right) / max(len(left), 1)


def _clamp_01(value: float) -> float:
    return max(0.0, min(1.0, value))


@dataclass
class MetricScores:
    recall_at_k: float | None
    mrr: float | None
    hit_at_k: float | None
    ndcg_at_k: float | None
    faithfulness: float | None
    answer_relevance: float | None
    evaluator_version: str


def _compute_retrieval_metrics(
    retrieved_chunk_ids: list[str],
    relevant_chunk_ids: list[str] | None,
) -> tuple[float | None, float | None, float | None, float | None]:
    if not relevant_chunk_ids:
        return None, None, None, None

    relevant = set(relevant_chunk_ids)
    if not relevant:
        return None, None, None, None

    hits = [chunk_id for chunk_id in retrieved_chunk_ids if chunk_id in relevant]
    recall_at_k = len(set(hits)) / len(relevant)
    hit_at_k = 1.0 if hits else 0.0

    reciprocal_rank = 0.0
    for idx, chunk_id in enumerate(retrieved_chunk_ids, start=1):
        if chunk_id in relevant:
            reciprocal_rank = 1.0 / idx
            break

    dcg = 0.0
    for idx, chunk_id in enumerate(retrieved_chunk_ids, start=1):
        rel = 1.0 if chunk_id in relevant else 0.0
        if rel > 0.0:
            dcg += rel / log2(idx + 1)

    ideal_hits = min(len(relevant), len(retrieved_chunk_ids))
    idcg = sum(1.0 / log2(idx + 1) for idx in range(1, ideal_hits + 1))
    ndcg_at_k = (dcg / idcg) if idcg > 0.0 else 0.0

    return _clamp_01(recall_at_k), _clamp_01(reciprocal_rank), _clamp_01(hit_at_k), _clamp_01(ndcg_at_k)


def _compute_faithfulness(answer_text: str, retrieved_texts: list[str]) -> float | None:
    answer_tokens = _tokenize(answer_text)
    if not answer_tokens:
        return None

    context_tokens: set[str] = set()
    for text in retrieved_texts:
        context_tokens.update(_tokenize(text))
    if not context_tokens:
        return None

    return _clamp_01(_safe_overlap_ratio(answer_tokens, context_tokens))


def _compute_answer_relevance(query_text: str, answer_text: str) -> float | None:
    query_tokens = _tokenize(query_text)
    answer_tokens = _tokenize(answer_text)
    if not query_tokens or not answer_tokens:
        return None
    return _clamp_01(_safe_overlap_ratio(query_tokens, answer_tokens))


def compute_metrics(
    query_text: str,
    answer_text: str,
    retrieved_chunk_ids: list[str],
    retrieved_texts: list[str],
    relevant_chunk_ids: list[str] | None,
) -> MetricScores:
    recall_at_k, mrr, hit_at_k, ndcg_at_k = _compute_retrieval_metrics(retrieved_chunk_ids, relevant_chunk_ids)
    faithfulness = _compute_faithfulness(answer_text, retrieved_texts)
    answer_relevance = _compute_answer_relevance(query_text, answer_text)

    return MetricScores(
        recall_at_k=recall_at_k,
        mrr=mrr,
        hit_at_k=hit_at_k,
        ndcg_at_k=ndcg_at_k,
        faithfulness=faithfulness,
        answer_relevance=answer_relevance,
        evaluator_version="heuristic-v1",
    )
