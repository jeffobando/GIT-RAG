from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db_session
from app.core.config import reload_settings
from app.schemas.evaluation import EvaluateRequest, EvaluateResponse
from app.services.evaluation.service import EvaluateService


router = APIRouter()


@router.post("/evaluate", response_model=EvaluateResponse)
def evaluate(payload: EvaluateRequest, db: Session = Depends(get_db_session)) -> EvaluateResponse:
    settings = reload_settings()
    service = EvaluateService(settings=settings, db=db)
    try:
        return service.evaluate_response(payload)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=f"Evaluation failed: {exc}") from exc


@router.post("/evaluate/base", response_model=EvaluateResponse)
def evaluate_base(payload: EvaluateRequest, db: Session = Depends(get_db_session)) -> EvaluateResponse:
    settings = reload_settings()
    service = EvaluateService(settings=settings, db=db)
    try:
        return service.evaluate_base_response(payload)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=f"Base evaluation failed: {exc}") from exc
