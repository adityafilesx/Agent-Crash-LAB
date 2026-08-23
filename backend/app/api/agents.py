"""
Agents API endpoints — CRUD for agents, versions, and tools.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.agent import (
    AgentCreate,
    AgentResponse,
    AgentVersionCreate,
    AgentVersionResponse,
)
from app.services import agent_service

router = APIRouter(prefix="/agents", tags=["agents"])


@router.post("", response_model=AgentResponse, status_code=201)
def create_agent(agent_data: AgentCreate, db: Session = Depends(get_db)):
    """Register a new AI agent."""
    agent = agent_service.create_agent(db, agent_data)
    return agent


@router.get("", response_model=List[AgentResponse])
def list_agents(db: Session = Depends(get_db)):
    """List all registered agents."""
    agents = agent_service.get_agents(db)
    return agents


@router.get("/{agent_id}", response_model=AgentResponse)
def get_agent(agent_id: str, db: Session = Depends(get_db)):
    """Get a specific agent by ID."""
    agent = agent_service.get_agent(db, agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent


@router.post("/{agent_id}/versions", response_model=AgentVersionResponse, status_code=201)
def create_version(
    agent_id: str,
    version_data: AgentVersionCreate,
    db: Session = Depends(get_db),
):
    """Create a new version for an existing agent."""
    agent = agent_service.get_agent(db, agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    version = agent_service.create_agent_version(db, agent_id, version_data)
    return version

from pydantic import BaseModel, Field

class CloneVersionRequest(BaseModel):
    original_version_id: str
    new_version_name: str
    new_system_prompt: str

@router.post("/{agent_id}/versions/clone", response_model=AgentVersionResponse, status_code=201)
def clone_version(
    agent_id: str,
    req: CloneVersionRequest,
    db: Session = Depends(get_db),
):
    """Clone an existing agent version with a new system prompt."""
    agent = agent_service.get_agent(db, agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
        
    original = agent_service.get_agent_version(db, req.original_version_id)
    if not original or original.agent_id != agent_id:
        raise HTTPException(status_code=404, detail="Original version not found")
        
    tools_create = []
    for t in original.tools:
        tools_create.append(
            {
                "name": t.name,
                "description": t.description,
                "parameters_schema": t.parameters_schema,
                "permissions": t.permissions,
                "is_destructive": t.is_destructive,
                "requires_confirmation": t.requires_confirmation
            }
        )
        
    version_data = AgentVersionCreate(
        version=req.new_version_name,
        system_prompt=req.new_system_prompt,
        model_provider=original.model_provider,
        model_name=original.model_name,
        config=original.config,
        tools=tools_create
    )
    
    version = agent_service.create_agent_version(db, agent_id, version_data)
    return version
