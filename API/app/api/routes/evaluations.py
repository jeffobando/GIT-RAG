from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db_session
from app.schemas.evaluations import EvaluationRunResponse
from app.services.observability.query_service import read_evaluation_runs


router = APIRouter()


@router.get("/runs", response_model=list[EvaluationRunResponse])
def evaluation_runs(db: Session = Depends(get_db_session)) -> list[EvaluationRunResponse]:
    return read_evaluation_runs(db)

