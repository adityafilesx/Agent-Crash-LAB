"""Initial schema — all Phase 1 tables

Revision ID: 001_initial
Revises: None
Create Date: 2024-01-01
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Agents
    op.create_table(
        "agents",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False, index=True),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )

    # Agent Versions
    op.create_table(
        "agent_versions",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "agent_id",
            sa.String(36),
            sa.ForeignKey("agents.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("version", sa.String(50), nullable=False),
        sa.Column("system_prompt", sa.Text, nullable=False),
        sa.Column("model_provider", sa.String(50), nullable=False),
        sa.Column("model_name", sa.String(100), nullable=False),
        sa.Column("config", sa.JSON, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )

    # Tools
    op.create_table(
        "tools",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "agent_version_id",
            sa.String(36),
            sa.ForeignKey("agent_versions.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("parameters_schema", sa.JSON, nullable=True),
        sa.Column("permissions", sa.JSON, nullable=True),
        sa.Column("is_destructive", sa.Boolean, default=False, nullable=False),
        sa.Column("requires_confirmation", sa.Boolean, default=False, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )

    # Scenarios
    op.create_table(
        "scenarios",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("category", sa.String(50), nullable=False, index=True),
        sa.Column("severity", sa.String(20), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("user_input", sa.Text, nullable=False),
        sa.Column("objective", sa.Text, nullable=True),
        sa.Column("expected_behavior", sa.Text, nullable=False),
        sa.Column("forbidden_behavior", sa.Text, nullable=True),
        sa.Column("tools_involved", sa.JSON, nullable=True),
        sa.Column("setup_state", sa.JSON, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )

    # Test Runs
    op.create_table(
        "test_runs",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "agent_version_id",
            sa.String(36),
            sa.ForeignKey("agent_versions.id"),
            nullable=False,
            index=True,
        ),
        sa.Column(
            "scenario_id",
            sa.String(36),
            sa.ForeignKey("scenarios.id"),
            nullable=False,
            index=True,
        ),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("duration_ms", sa.Float, nullable=True),
        sa.Column("trace", sa.JSON, nullable=True),
        sa.Column("metrics", sa.JSON, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )

    # Execution Steps
    op.create_table(
        "execution_steps",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "test_run_id",
            sa.String(36),
            sa.ForeignKey("test_runs.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("step_index", sa.Integer, nullable=False),
        sa.Column("step_type", sa.String(50), nullable=False),
        sa.Column("content", sa.Text, nullable=True),
        sa.Column("tool_name", sa.String(100), nullable=True),
        sa.Column("tool_args", sa.JSON, nullable=True),
        sa.Column("tool_result", sa.JSON, nullable=True),
        sa.Column("latency_ms", sa.Float, nullable=True),
        sa.Column("error", sa.Text, nullable=True),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
    )

    # Failures
    op.create_table(
        "failures",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "test_run_id",
            sa.String(36),
            sa.ForeignKey("test_runs.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("category", sa.String(50), nullable=False, index=True),
        sa.Column("subcategory", sa.String(100), nullable=True),
        sa.Column("severity", sa.String(20), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("expected_behavior", sa.Text, nullable=True),
        sa.Column("actual_behavior", sa.Text, nullable=True),
        sa.Column("root_cause", sa.Text, nullable=True),
        sa.Column("contributing_factors", sa.JSON, nullable=True),
        sa.Column("evidence", sa.JSON, nullable=True),
        sa.Column("is_reproducible", sa.Boolean, default=True, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("failures")
    op.drop_table("execution_steps")
    op.drop_table("test_runs")
    op.drop_table("scenarios")
    op.drop_table("tools")
    op.drop_table("agent_versions")
    op.drop_table("agents")
