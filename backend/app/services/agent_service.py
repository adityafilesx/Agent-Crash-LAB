"""
Agent Service — CRUD operations for agents, versions, and tools.
"""

from typing import List, Optional
from sqlalchemy.orm import Session, joinedload

from app.models.agent import Agent
from app.models.agent_version import AgentVersion
from app.models.tool import Tool
from app.schemas.agent import AgentCreate, AgentVersionCreate


def create_agent(db: Session, agent_data: AgentCreate) -> Agent:
    """Create a new agent with an optional initial version."""
    agent = Agent(
        name=agent_data.name,
        description=agent_data.description,
    )
    db.add(agent)
    db.flush()

    if agent_data.version:
        create_agent_version(db, agent.id, agent_data.version)

    db.commit()
    db.refresh(agent)
    return agent


def create_agent_version(
    db: Session, agent_id: str, version_data: AgentVersionCreate
) -> AgentVersion:
    """Create a new version for an existing agent."""
    version = AgentVersion(
        agent_id=agent_id,
        version=version_data.version,
        system_prompt=version_data.system_prompt,
        model_provider=version_data.model_provider,
        model_name=version_data.model_name,
        config=version_data.config or {},
    )
    db.add(version)
    db.flush()

    for tool_data in version_data.tools:
        tool = Tool(
            agent_version_id=version.id,
            name=tool_data.name,
            description=tool_data.description,
            parameters_schema=tool_data.parameters_schema or {},
            permissions=tool_data.permissions or {},
            is_destructive=tool_data.is_destructive,
            requires_confirmation=tool_data.requires_confirmation,
        )
        db.add(tool)

    db.commit()
    db.refresh(version)
    return version


def get_agent(db: Session, agent_id: str) -> Optional[Agent]:
    """Get an agent by ID with all versions and tools loaded."""
    return (
        db.query(Agent)
        .options(joinedload(Agent.versions).joinedload(AgentVersion.tools))
        .filter(Agent.id == agent_id)
        .first()
    )


def get_agents(db: Session) -> List[Agent]:
    """Get all agents with their versions and tools."""
    return (
        db.query(Agent)
        .options(joinedload(Agent.versions).joinedload(AgentVersion.tools))
        .all()
    )


def get_agent_version(db: Session, version_id: str) -> Optional[AgentVersion]:
    """Get an agent version by ID with tools loaded."""
    return (
        db.query(AgentVersion)
        .options(joinedload(AgentVersion.tools))
        .filter(AgentVersion.id == version_id)
        .first()
    )
