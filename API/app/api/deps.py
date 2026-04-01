from collections.abc import Generator

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.core.database import DatabaseUnavailableError, session_scope


def get_db_session() -> Generator[Session, None, None]:
    try:
        with session_scope() as session:
            yield session
    except DatabaseUnavailableError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

