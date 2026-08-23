from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List
from datetime import datetime, timezone
import uuid

from app.core.database import get_db
from app.models.test_run import TestRun
from app.models.execution_step import ExecutionStep
from app.models.agent import Agent
from app.models.scenario import Scenario
from app.models.tool import Tool
from app.models.failure import Failure
from app.schemas.test_run import TestRunCreate, TestRunResponse, TestRunDetail
from app.sandbox.executor import ExecutionEngine
from app.evaluator.judge import LLMEvaluator
from app.evaluator.remediator import LLMRemediator

router = APIRouter(prefix="/test-runs", tags=["test_runs"])

@router.post("", response_model=TestRunDetail)
def create_test_run(request: TestRunCreate, db: Session = Depends(get_db)):
    """Execute a scenario against an agent and record the trace."""
    
    # 1. Fetch Agent & Scenario
    agent = db.query(Agent).filter(Agent.id == request.agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
        
    scenario = db.query(Scenario).filter(Scenario.id == request.scenario_id).first()
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")
        
    # Get active version tools
    active_version = None
    if request.agent_version_id:
        active_version = next((v for v in agent.versions if v.id == request.agent_version_id), None)
    
    if not active_version:
        if not agent.versions:
            raise HTTPException(status_code=400, detail="Agent has no active versions")
        # Default to the most recently created version
        active_version = sorted(agent.versions, key=lambda v: v.created_at, reverse=True)[0]
    tools = [
        {
            "name": t.name,
            "description": t.description,
            "parameters": t.parameters_schema
        }
        for t in active_version.tools
    ]
    
    # 2. Create DB Record (Pending)
    db_test_run = TestRun(
        id=f"tr_{uuid.uuid4().hex[:12]}",
        agent_version_id=active_version.id,
        scenario_id=scenario.id,
        status="running",
        started_at=datetime.now(timezone.utc)
    )
    db.add(db_test_run)
    db.commit()
    db.refresh(db_test_run)
    
    # 3. Dispatch to Celery Worker
    from app.worker import execute_test_run_task
    try:
        execute_test_run_task.delay(db_test_run.id, request.behavior_mode)
    except Exception as e:
        # If celery is down, fallback to marking error
        db_test_run.status = "error"
        db_test_run.completed_at = datetime.now(timezone.utc)
        db.commit()
        raise HTTPException(status_code=500, detail=f"Failed to dispatch task: {str(e)}")
        
    return db_test_run

@router.get("", response_model=List[TestRunResponse])
def list_test_runs(db: Session = Depends(get_db), limit: int = 50):
    return db.query(TestRun).order_by(desc(TestRun.started_at)).limit(limit).all()


from sqlalchemy.orm import Session, selectinload

@router.get("/{run_id}", response_model=TestRunDetail)
def get_test_run(run_id: str, db: Session = Depends(get_db)):
    run = db.query(TestRun).options(selectinload(TestRun.steps), selectinload(TestRun.failures)).filter(TestRun.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Test Run not found")
    
    # Map steps to execution_steps for the schema
    run.execution_steps = run.steps
    return run
