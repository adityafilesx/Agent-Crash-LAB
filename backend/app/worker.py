import os
from celery import Celery
from datetime import datetime, timezone
import structlog

# Assuming database interaction in worker needs separate DB session handling
from app.core.database import SessionLocal
from app.models.test_run import TestRun
from app.models.execution_step import ExecutionStep
from app.models.agent import Agent
from app.models.scenario import Scenario
from app.models.failure import Failure
from app.sandbox.executor import ExecutionEngine
from app.evaluator.judge import LLMEvaluator
from app.evaluator.remediator import LLMRemediator

logger = structlog.get_logger(__name__)

broker_url = os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379/0")
result_backend = os.environ.get("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")

celery_app = Celery(
    "agentcrashlab_worker",
    broker=broker_url,
    backend=result_backend
)

@celery_app.task(name="execute_test_run_task")
def execute_test_run_task(test_run_id: str, behavior_mode: str):
    """
    Executes a test run in the background using Celery.
    """
    logger.info("Starting execute_test_run_task", test_run_id=test_run_id)
    db = SessionLocal()
    try:
        db_test_run = db.query(TestRun).filter(TestRun.id == test_run_id).first()
        if not db_test_run:
            logger.error("TestRun not found", test_run_id=test_run_id)
            return
        
        scenario = db.query(Scenario).filter(Scenario.id == db_test_run.scenario_id).first()
        if not scenario:
            logger.error("Scenario not found", scenario_id=db_test_run.scenario_id)
            return

        active_version = next((v for v in db.query(Agent).filter(Agent.id == db_test_run.agent_version.agent_id).first().versions if v.id == db_test_run.agent_version_id), None)
        if not active_version:
            logger.error("AgentVersion not found", agent_version_id=db_test_run.agent_version_id)
            return
            
        tools = [
            {
                "name": t.name,
                "description": t.description,
                "parameters": t.parameters_schema
            }
            for t in active_version.tools
        ]
        
        # 3. Execute in Sandbox
        try:
            engine = ExecutionEngine(
                provider_name=active_version.model_provider,
                system_prompt=active_version.system_prompt,
                tools=tools,
                provider_kwargs={"behavior_mode": behavior_mode}
            )
            
            result = engine.run_scenario(
                scenario_title=scenario.title,
                scenario_objective=scenario.objective or "Test the agent's general reliability.",
                expected_behavior=scenario.expected_behavior,
                forbidden_behavior=scenario.forbidden_behavior or "None",
                initial_user_input=scenario.user_input
            )
            
            # 4. Save Trace to DB
            trace = result["trace"]
            for step_data in trace:
                db_step = ExecutionStep(
                    test_run_id=db_test_run.id,
                    step_index=step_data["step_order"],
                    step_type=step_data["step_type"],
                    content=step_data["content"],
                    tool_name=step_data["tool_name"],
                    tool_args=step_data["tool_arguments"],
                    tool_result=step_data["tool_result"],
                    error=str(step_data["tool_result"]) if step_data.get("is_error") else None,
                    timestamp=datetime.fromisoformat(step_data["timestamp"])
                )
                db.add(db_step)
                
            db_test_run.status = result["status"]
            
            # 5. Evaluate the Trace
            if db_test_run.status == "completed":
                try:
                    evaluator = LLMEvaluator()
                    eval_result = evaluator.evaluate(
                        trace=trace, 
                        expected_behavior=scenario.expected_behavior,
                        forbidden_behavior=scenario.forbidden_behavior
                    )
                    
                    if eval_result.get("passed") is True:
                        db_test_run.status = "passed"
                    else:
                        db_test_run.status = "failed"
                        # Create Failure record
                        db_failure = Failure(
                            test_run_id=db_test_run.id,
                            category=eval_result.get("failure_category", "reasoning"),
                            severity=eval_result.get("severity", "medium"),
                            title=f"Failed Scenario: {scenario.title}",
                            root_cause=eval_result.get("root_cause", "Unknown"),
                            contributing_factors=eval_result.get("contributing_factors", [])
                        )
                        
                        try:
                            remediator = LLMRemediator()
                            fix_suggestion = remediator.suggest_fix(
                                system_prompt=active_version.system_prompt,
                                tools=tools,
                                trace=trace,
                                failure_report=eval_result
                            )
                            db_failure.suggested_fix = fix_suggestion
                        except Exception as rem_err:
                            logger.error("Remediator error", error=str(rem_err))
                            
                        db.add(db_failure)
                except Exception as eval_err:
                    logger.error("Evaluator error", error=str(eval_err))
                    db_test_run.status = "completed"

            db_test_run.completed_at = datetime.now(timezone.utc)
            db.commit()
            logger.info("Completed execute_test_run_task", test_run_id=test_run_id, status=db_test_run.status)
            
        except Exception as e:
            db_test_run.status = "error"
            db_test_run.completed_at = datetime.now(timezone.utc)
            db.commit()
            logger.exception("Engine execution error", error=str(e))
    finally:
        db.close()
