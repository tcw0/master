"""
Repository for database operations.

Artifacts are versioned: each LLM generation or human edit inserts a new
row with an incremented version number. Queries return the latest version.
"""

from uuid import UUID

from sqlalchemy import desc
from sqlalchemy.orm import Session as DBSession

from db.models import Artifact, Session


class SessionRepository:
    """
    CRUD operations for pipeline sessions and versioned artifacts.

    One instance per request, wrapping a SQLAlchemy session.
    """

    def __init__(self, db: DBSession) -> None:
        self.db = db

    # ------------------------------------------------------------------
    # Session CRUD
    # ------------------------------------------------------------------

    def create_session(
        self,
        requirements_text: str,
        requirements_name: str,
        provider: str,
        model: str,
        temperature: float,
    ) -> Session:
        """Create a new pipeline session (no pre-created artifact rows)."""
        session = Session(
            requirements_text=requirements_text,
            requirements_name=requirements_name,
            provider=provider,
            model=model,
            temperature=temperature,
        )
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        return session

    def get_session(self, session_id: UUID) -> Session | None:
        return self.db.query(Session).filter(Session.id == session_id).first()

    def list_sessions(self) -> list[Session]:
        return (
            self.db.query(Session)
            .order_by(Session.created_at.desc())
            .all()
        )

    def delete_session(self, session_id: UUID) -> bool:
        session = self.get_session(session_id)
        if session is None:
            return False
        self.db.delete(session)
        self.db.commit()
        return True

    # ------------------------------------------------------------------
    # Artifact Versioning
    # ------------------------------------------------------------------

    def get_latest_artifact(
        self, session_id: UUID, phase_id: str,
    ) -> Artifact | None:
        """Get the latest version of a phase artifact."""
        return (
            self.db.query(Artifact)
            .filter(
                Artifact.session_id == session_id,
                Artifact.phase_id == phase_id,
            )
            .order_by(desc(Artifact.version))
            .first()
        )

    def get_latest_artifacts(self, session_id: UUID) -> list[Artifact]:
        """Get the latest version of each phase artifact for a session."""
        all_artifacts = (
            self.db.query(Artifact)
            .filter(Artifact.session_id == session_id)
            .order_by(Artifact.phase_id, desc(Artifact.version))
            .all()
        )
        # Pick the first (latest) per phase_id
        latest: dict[str, Artifact] = {}
        for a in all_artifacts:
            if a.phase_id not in latest:
                latest[a.phase_id] = a
        return list(latest.values())

    def get_artifact_history(
        self, session_id: UUID, phase_id: str,
    ) -> list[Artifact]:
        """Get all versions of a phase artifact, oldest first."""
        return (
            self.db.query(Artifact)
            .filter(
                Artifact.session_id == session_id,
                Artifact.phase_id == phase_id,
            )
            .order_by(Artifact.version)
            .all()
        )

    def create_artifact_version(
        self,
        session_id: UUID,
        phase_id: str,
        source: str,
        status: str = "completed",
        content: dict | None = None,
        validation_report: dict | None = None,
        error: str | None = None,
    ) -> Artifact:
        """
        Insert a new artifact version.

        Version number is auto-incremented based on the current max version
        for this (session, phase) pair.
        """
        current = self.get_latest_artifact(session_id, phase_id)
        next_version = (current.version + 1) if current else 1

        artifact = Artifact(
            session_id=session_id,
            phase_id=phase_id,
            version=next_version,
            source=source,
            status=status,
            content=content,
            validation_report=validation_report,
            error=error,
        )
        self.db.add(artifact)
        self.db.commit()
        self.db.refresh(artifact)
        return artifact
