"""
ExecutionStep model — a single step in an agent execution trace.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import String, Text, DateTime, ForeignKey, JSON, Integer, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class ExecutionStep(Base):
    __tablename__ = "execution_steps"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    test_run_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("test_runs.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    step_index: Mapped[int] = mapped_column(Integer, nullable=False)
    step_type: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # user_message, llm_request, llm_response, tool_call, tool_response, final_response, error
    content: Mapped[str] = mapped_column(Text, nullable=True)
    tool_name: Mapped[str] = mapped_column(String(100), nullable=True)
    tool_args: Mapped[dict] = mapped_column(JSON, nullable=True)
    tool_result: Mapped[dict] = mapped_column(JSON, nullable=True)
    latency_ms: Mapped[float] = mapped_column(Float, nullable=True)
    error: Mapped[str] = mapped_column(Text, nullable=True)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    test_run = relationship("TestRun", back_populates="steps")
