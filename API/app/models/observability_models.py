from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy import DateTime, Float, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


def _new_id() -> str:
    return str(uuid4())


class RagQueryORM(Base):
    __tablename__ = "rag_queries"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_new_id)
    query_text: Mapped[str] = mapped_column(Text, nullable=False)
    answer_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
        index=True,
    )
    run_type: Mapped[str | None] = mapped_column(String(50), nullable=True, index=True)
    source_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    top_k: Mapped[int] = mapped_column(Integer, nullable=False, default=5)
    total_latency_ms: Mapped[float | None] = mapped_column(Float, nullable=True)
    retrieval_latency_ms: Mapped[float | None] = mapped_column(Float, nullable=True)
    generation_latency_ms: Mapped[float | None] = mapped_column(Float, nullable=True)
    insufficient_context: Mapped[bool] = mapped_column(default=False, nullable=False)
    had_error: Mapped[bool] = mapped_column(default=False, nullable=False)
    metadata_json: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)

    retrievals: Mapped[list["RagRetrievalORM"]] = relationship(
        back_populates="query",
        cascade="all, delete-orphan",
    )
    evaluations: Mapped[list["RagEvaluationORM"]] = relationship(
        back_populates="query",
        cascade="all, delete-orphan",
    )


class RagRetrievalORM(Base):
    __tablename__ = "rag_retrievals"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_new_id)
    query_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("rag_queries.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    chunk_id: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    retrieved_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    similarity_score: Mapped[float] = mapped_column(Float, nullable=False)
    rank: Mapped[int] = mapped_column(Integer, nullable=False)
    source_file: Mapped[str | None] = mapped_column(String(500), nullable=True)
    source_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    metadata_json: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)

    query: Mapped["RagQueryORM"] = relationship(back_populates="retrievals")


class RagEvaluationORM(Base):
    __tablename__ = "rag_evaluations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_new_id)
    query_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("rag_queries.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    recall_at_k: Mapped[float | None] = mapped_column(Float, nullable=True)
    mrr: Mapped[float | None] = mapped_column(Float, nullable=True)
    hit_at_k: Mapped[float | None] = mapped_column(Float, nullable=True)
    ndcg_at_k: Mapped[float | None] = mapped_column(Float, nullable=True)
    faithfulness: Mapped[float | None] = mapped_column(Float, nullable=True)
    answer_relevance: Mapped[float | None] = mapped_column(Float, nullable=True)
    evaluation_timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
        index=True,
    )
    evaluator_version: Mapped[str | None] = mapped_column(String(120), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    query: Mapped["RagQueryORM"] = relationship(back_populates="evaluations")
