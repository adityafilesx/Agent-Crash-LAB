"""
Pydantic schemas for Scenario endpoints.
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class ScenarioCreate(BaseModel):
    category: str = Field(..., max_length=50)
    severity: str = Field(default="medium", max_length=20)
    title: str = Field(..., min_length=1, max_length=255)
    user_input: str = Field(..., min_length=1)
    objective: Optional[str] = None
    expected_behavior: str = Field(..., min_length=1)
    forbidden_behavior: Optional[str] = None
    tools_involved: List[str] = Field(default_factory=list)
    setup_state: Optional[dict] = None


class ScenarioResponse(BaseModel):
    id: str
    category: str
    severity: str
    title: str
    user_input: str
    objective: Optional[str]
    expected_behavior: str
    forbidden_behavior: Optional[str]
    tools_involved: Optional[List[str]]
    setup_state: Optional[dict]
    created_at: datetime

    class Config:
        from_attributes = True
