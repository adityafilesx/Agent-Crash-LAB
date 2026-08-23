"""
Execution Engine — Orchestrates the agent, sandbox, and trace recording.
"""
import uuid
import time
from typing import Dict, Any, List

from app.sandbox.sandbox import Sandbox
from app.sandbox.trace_recorder import TraceRecorder
from app.sandbox.user_simulator import UserSimulator
from app.agents.factory import get_provider

class ExecutionEngine:
    """
    Executes a test scenario by connecting an AgentProvider to a Sandbox and a UserSimulator.
    Records the entire interaction in a TraceRecorder.
    """

    def __init__(
        self, 
        provider_name: str, 
        system_prompt: str, 
        tools: List[Dict[str, Any]],
        provider_kwargs: Dict[str, Any] = None
    ):
        self.provider = get_provider(provider_name, **(provider_kwargs or {}))
        self.system_prompt = system_prompt
        self.tools = tools

    def run_scenario(self, scenario_title: str, scenario_objective: str, expected_behavior: str, forbidden_behavior: str, initial_user_input: str, max_turns: int = 15) -> Dict[str, Any]:
        """
        Run a multi-turn scenario using UserSimulator.
        
        Args:
            scenario_title: Title of the scenario
            scenario_objective: Goal of the scenario
            expected_behavior: Expected behavior of the agent
            forbidden_behavior: Forbidden behavior of the agent
            initial_user_input: The first message to start the simulation
            max_turns: Maximum number of agent-sandbox interaction turns to prevent infinite loops
            
        Returns:
            Dict containing the execution trace and summary
        """
        run_id = f"run_{uuid.uuid4().hex[:8]}"
        trace = TraceRecorder(run_id=run_id)
        sandbox = Sandbox()
        
        simulator = UserSimulator(
            scenario_title=scenario_title,
            scenario_objective=scenario_objective,
            expected_behavior=expected_behavior,
            forbidden_behavior=forbidden_behavior,
            initial_user_input=initial_user_input
        )
        
        # 1. Record Initial User Input
        trace.record_user_message(initial_user_input)
        
        turn_count = 0
        is_finished = False
        status = "completed"
        
        try:
            while not is_finished and turn_count < max_turns:
                turn_count += 1
                
                # 2. Get Agent Response
                messages = trace.get_messages_for_provider(self.system_prompt)
                
                response = self.provider.generate(
                    messages=messages,
                    tools=self.tools,
                    system_prompt=self.system_prompt
                )
                
                # 3. Record Agent Text Response (if any)
                if response.content:
                    trace.record_agent_response(response.content)
                
                # 4. Handle Tool Calls or Pass to User Simulator
                if response.finish_reason == "tool_calls" and response.tool_calls:
                    for tool_call in response.tool_calls:
                        trace.record_tool_call(tool_call)
                        
                        tool_result = sandbox.execute_tool(
                            tool_name=tool_call.tool_name,
                            arguments=tool_call.arguments
                        )
                        
                        trace.record_tool_result(
                            tool_call_id=tool_call.call_id,
                            tool_name=tool_call.tool_name,
                            result=tool_result
                        )
                else:
                    # Agent replied with text. Now we ask the User Simulator for the next turn.
                    next_user_message = simulator.generate_next_turn(trace)
                    
                    if next_user_message.strip() == "TERMINATE":
                        is_finished = True
                    else:
                        trace.record_user_message(next_user_message)
                    
            if not is_finished:
                status = "max_turns_reached"
                trace.record_system_error(f"Execution terminated: reached max turns ({max_turns})")
                
        except Exception as e:
            status = "system_error"
            trace.record_system_error(f"Execution engine error: {str(e)}")
            
        finally:
            sandbox.terminate()
            
        return {
            "run_id": run_id,
            "status": status,
            "turn_count": turn_count,
            "side_effects": sandbox.get_side_effects(),
            "trace": trace.get_trace()
        }
