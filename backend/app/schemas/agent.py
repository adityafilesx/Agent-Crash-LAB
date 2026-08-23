"""
Pydantic schemas for Agent and AgentVersion endpoints.
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


# --- Tool Schemas ---

class ToolCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    parameters_schema: Optional[dict] = None
    permissions: Optional[dict] = None
    is_destructive: bool = False
    requires_confirmation: bool = False


class ToolResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    parameters_schema: Optional[dict]
    permissions: Optional[dict]
    is_destructive: bool
    requires_confirmation: bool
    created_at: datetime

    class Config:
        from_attributes = True


# --- AgentVersion Schemas ---

class AgentVersionCreate(BaseModel):
    version: str = Field(..., min_length=1, max_length=50)
    system_prompt: str = Field(..., min_length=1)
    model_provider: str = Field(default="mock", max_length=50)
    model_name: str = Field(default="gpt-4o", max_length=100)
    config: Optional[dict] = None
    tools: List[ToolCreate] = Field(default_factory=list)


class AgentVersionResponse(BaseModel):
    id: str
    agent_id: str
    version: str
    system_prompt: str
    model_provider: str
    model_name: str
    config: Optional[dict]
    tools: List[ToolResponse] = []
    created_at: datetime

    class Config:
        from_attributes = True


# --- Agent Schemas ---

class AgentCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    version: Optional[AgentVersionCreate] = None


class AgentResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    versions: List[AgentVersionResponse] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AgentListResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    version_count: int = 0
    latest_version: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
