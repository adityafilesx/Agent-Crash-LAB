"""
TestRun model — a single test execution of a scenario against an agent version.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import String, Text, DateTime, ForeignKey, JSON, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class TestRun(Base):
    __tablename__ = "test_runs"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    agent_version_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("agent_versions.id"), nullable=False, index=True,
    )
    scenario_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("scenarios.id"), nullable=False, index=True,
    )
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="pending"
    )  # pending, running, passed, failed, error, timeout
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=True,
    )
    completed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=True,
    )
    duration_ms: Mapped[float] = mapped_column(Float, nullable=True)
    trace: Mapped[dict] = mapped_column(JSON, nullable=True, default=dict)
    metrics: Mapped[dict] = mapped_column(JSON, nullable=True, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    agent_version = relationship("AgentVersion", back_populates="test_runs")
    scenario = relationship("Scenario")
    steps = relationship("ExecutionStep", back_populates="test_run", cascade="all, delete-orphan")
    failures = relationship("Failure", back_populates="test_run", cascade="all, delete-orphan")
