"""
Failure model — a detected failure from a test run.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Failure(Base):
    __tablename__ = "failures"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    test_run_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("test_runs.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    # Taxonomy: safety, security, reasoning, tool_usage, resilience
    category: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    # Sub-category: destructive_action, prompt_injection, hallucination, etc.
    subcategory: Mapped[str] = mapped_column(String(100), nullable=True)
    severity: Mapped[str] = mapped_column(
        String(20), nullable=False, default="medium"
    )  # low, medium, high, critical
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    expected_behavior: Mapped[str] = mapped_column(Text, nullable=True)
    actual_behavior: Mapped[str] = mapped_column(Text, nullable=True)
    root_cause: Mapped[str] = mapped_column(Text, nullable=True)
    contributing_factors: Mapped[list] = mapped_column(JSON, nullable=True, default=list)
    evidence: Mapped[list] = mapped_column(JSON, nullable=True, default=list)
    is_reproducible: Mapped[bool] = mapped_column(default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    test_run = relationship("TestRun", back_populates="failures")
    
    # Auto-Remediation
    suggested_fix: Mapped[dict] = mapped_column(JSON, nullable=True) # {proposed_system_prompt: str, explanation: str}
