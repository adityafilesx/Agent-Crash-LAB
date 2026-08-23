from typing import List, Dict, Any, Optional
from pydantic import BaseModel, ConfigDict
from datetime import datetime


class FailureSchema(BaseModel):
    id: str
    category: str
    subcategory: Optional[str] = None
    severity: str
    title: str
    description: Optional[str] = None
    root_cause: Optional[str] = None
    contributing_factors: List[str] = []
    suggested_fix: Optional[Dict[str, Any]] = None
    
    model_config = ConfigDict(from_attributes=True)

class ExecutionStepSchema(BaseModel):
    id: Optional[str] = None
    step_index: int
    step_type: str
    content: Optional[str] = None
    tool_name: Optional[str] = None
    tool_args: Optional[Dict[str, Any]] = None
    tool_result: Optional[Dict[str, Any]] = None
    latency_ms: Optional[float] = None
    error: Optional[str] = None
    timestamp: datetime
    
    model_config = ConfigDict(from_attributes=True)


class TestRunCreate(BaseModel):
    agent_id: str
    agent_version_id: Optional[str] = None
    scenario_id: str
    behavior_mode: str = "realistic"  # Mock provider mode: realistic, safe, unsafe


class TestRunResponse(BaseModel):
    id: str
    agent_version_id: str
    scenario_id: str
    status: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


class TestRunDetail(TestRunResponse):
    execution_steps: List[ExecutionStepSchema] = []
    failures: List[FailureSchema] = []
    
    model_config = ConfigDict(from_attributes=True)
