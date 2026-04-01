from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db_session
from app.schemas.metrics import MetricsCompareResponse, MetricsSummaryResponse
from app.services.observability.query_service import read_metrics_compare, read_metrics_summary


router = APIRouter()


@router.get("/summary", response_model=MetricsSummaryResponse)
def metrics_summary(db: Session = Depends(get_db_session)) -> MetricsSummaryResponse:
    return read_metrics_summary(db)


@router.get("/compare", response_model=MetricsCompareResponse)
def metrics_compare(
    left_run_type: str = "rag",
    right_run_type: str = "base",
    db: Session = Depends(get_db_session),
) -> MetricsCompareResponse:
    return read_metrics_compare(db, left_run_type=left_run_type, right_run_type=right_run_type)
