"""
Scenario model — a test scenario to run against an agent.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import String, Text, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Scenario(Base):
    __tablename__ = "scenarios"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    category: Mapped[str] = mapped_column(
        String(50), nullable=False, index=True
    )  # normal, edge_case, ambiguous, adversarial, tool_failure, destructive_action, long_horizon
    severity: Mapped[str] = mapped_column(
        String(20), nullable=False, default="medium"
    )  # low, medium, high, critical
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    user_input: Mapped[str] = mapped_column(Text, nullable=False)
    objective: Mapped[str] = mapped_column(Text, nullable=True)
    expected_behavior: Mapped[str] = mapped_column(Text, nullable=False)
    forbidden_behavior: Mapped[str] = mapped_column(Text, nullable=True)
    tools_involved: Mapped[list] = mapped_column(JSON, nullable=True, default=list)
    setup_state: Mapped[dict] = mapped_column(
        JSON, nullable=True, default=dict
    )  # Initial sandbox state for this scenario
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
