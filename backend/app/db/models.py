"""
SQLAlchemy models for the DDD pipeline.

Minimal schema: sessions and versioned artifacts.
Each edit or re-run creates a new artifact version instead of overwriting.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from db.database import Base


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Session(Base):
    """
    A pipeline session — one per requirements document + model config.

    Tracks the HITL workflow: the user creates a session, then runs
    phases one at a time, reviewing and editing artifacts between phases.
    """

    __tablename__ = "sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    requirements_text = Column(Text, nullable=False)
    requirements_name = Column(String(255), nullable=False, default="requirements")
    provider = Column(String(50), nullable=False)
    model = Column(String(255), nullable=False)
    temperature = Column(Float, nullable=False, default=0.3)
    created_at = Column(DateTime(timezone=True), nullable=False, default=_utc_now)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=_utc_now, onupdate=_utc_now)

    artifacts = relationship(
        "Artifact",
        back_populates="session",
        cascade="all, delete-orphan",
        order_by="Artifact.phase_id, Artifact.version",
    )


class Artifact(Base):
    """
    A versioned phase artifact within a session.

    Each LLM generation or human edit creates a new version.
    The latest version per phase is the current artifact.
    """

    __tablename__ = "artifacts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(
        UUID(as_uuid=True),
        ForeignKey("sessions.id", ondelete="CASCADE"),
        nullable=False,
    )
    phase_id = Column(String(50), nullable=False)
    version = Column(Integer, nullable=False, default=1)
    source = Column(String(20), nullable=False, default="llm")  # "llm" or "human"
    status = Column(String(20), nullable=False, default="completed")
    content = Column(JSONB, nullable=True)
    validation_report = Column(JSONB, nullable=True)
    instructions = Column(Text, nullable=True)
    error = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=_utc_now)

    session = relationship("Session", back_populates="artifacts")

    __table_args__ = (
        UniqueConstraint("session_id", "phase_id", "version", name="uq_session_phase_version"),
    )
