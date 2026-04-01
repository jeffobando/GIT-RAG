from fastapi import APIRouter, HTTPException

from app.core.config import reload_settings
from app.schemas.rag import RagQueryRequest, RagQueryResponse
from app.services.rag.query_service import execute_rag_query


router = APIRouter()


@router.post("/query", response_model=RagQueryResponse)
def rag_query(payload: RagQueryRequest) -> RagQueryResponse:
    settings = reload_settings()
    top_k = payload.k or settings.default_top_k
    try:
        result = execute_rag_query(settings=settings, question=payload.question, top_k=top_k)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    return RagQueryResponse(
        answer=str(result.get("answer", "")).strip(),
        sources=list(result.get("sources", [])),
    )
