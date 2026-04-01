from collections.abc import Generator
from contextlib import contextmanager
from functools import lru_cache

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings


class DatabaseUnavailableError(RuntimeError):
    pass


def _normalized_database_url() -> str:
    settings = get_settings()
    database_url = (settings.database_url or "").strip()
    if not database_url:
        raise DatabaseUnavailableError(
            "DATABASE_URL is not configured. Set DATABASE_URL to enable persistence."
        )
    return database_url


@lru_cache
def _engine_for_url(database_url: str) -> Engine:
    return create_engine(database_url, pool_pre_ping=True)


def get_engine() -> Engine:
    return _engine_for_url(_normalized_database_url())


@lru_cache
def _session_factory_for_url(database_url: str) -> sessionmaker[Session]:
    engine = _engine_for_url(database_url)
    return sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)


def get_session_factory() -> sessionmaker[Session]:
    return _session_factory_for_url(_normalized_database_url())


@contextmanager
def session_scope() -> Generator[Session, None, None]:
    session = get_session_factory()()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def init_database() -> bool:
    settings = get_settings()
    if not (settings.database_url or "").strip():
        return False

    from app.models.observability_models import Base

    Base.metadata.create_all(bind=get_engine())
    return True

