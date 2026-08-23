"""
Trace Recorder — Records the step-by-step execution trace of a test run.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timezone

from app.agents.base import AgentMessage, ToolCall


class TraceRecorder:
    """
    Records the complete execution trace of an agent interacting with the sandbox.
    Produces a list of execution steps suitable for database storage and forensics.
    """

    def __init__(self, run_id: str):
        self.run_id = run_id
        self.steps: List[Dict[str, Any]] = []
        self.step_counter = 0

    def record_user_message(self, content: str) -> None:
        """Record the initial scenario/user prompt."""
        self.step_counter += 1
        self.steps.append({
            "step_order": self.step_counter,
            "step_type": "user_input",
            "actor": "user",
            "content": content,
            "tool_call_id": None,
            "tool_name": None,
            "tool_arguments": None,
            "tool_result": None,
            "is_error": False,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })

    def record_agent_response(self, content: str) -> None:
        """Record a text response from the agent."""
        if not content:
            return

        self.step_counter += 1
        self.steps.append({
            "step_order": self.step_counter,
            "step_type": "agent_message",
            "actor": "agent",
            "content": content,
            "tool_call_id": None,
            "tool_name": None,
            "tool_arguments": None,
            "tool_result": None,
            "is_error": False,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })

    def record_tool_call(self, tool_call: ToolCall) -> None:
        """Record the agent requesting a tool call."""
        self.step_counter += 1
        self.steps.append({
            "step_order": self.step_counter,
            "step_type": "tool_call",
            "actor": "agent",
            "content": None,
            "tool_call_id": tool_call.call_id,
            "tool_name": tool_call.tool_name,
            "tool_arguments": tool_call.arguments,
            "tool_result": None,
            "is_error": False,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })

    def record_tool_result(self, tool_call_id: str, tool_name: str, result: Dict[str, Any]) -> None:
        """Record the result of a tool execution (from the sandbox)."""
        self.step_counter += 1
        is_error = not result.get("success", True)
        
        self.steps.append({
            "step_order": self.step_counter,
            "step_type": "tool_result",
            "actor": "system",
            "content": None,
            "tool_call_id": tool_call_id,
            "tool_name": tool_name,
            "tool_arguments": None,
            "tool_result": result,
            "is_error": is_error,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })

    def record_system_error(self, error_message: str) -> None:
        """Record a system-level error (e.g., timeout, engine failure)."""
        self.step_counter += 1
        self.steps.append({
            "step_order": self.step_counter,
            "step_type": "system_error",
            "actor": "system",
            "content": error_message,
            "tool_call_id": None,
            "tool_name": None,
            "tool_arguments": None,
            "tool_result": None,
            "is_error": True,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })

    def get_messages_for_provider(self, system_prompt: str) -> List[AgentMessage]:
        """
        Convert the current trace into a list of AgentMessage objects 
        suitable for feeding back into the AgentProvider.
        """
        messages = [
            AgentMessage(role="system", content=system_prompt)
        ]
        
        # We need to reconstruct the conversation history.
        # This is simplified. In a real system, we'd carefully reconstruct 
        # the exact message array required by OpenAI/Anthropic.
        
        # Group tool calls that happen in the same turn
        current_agent_turn = None
        
        for step in self.steps:
            if step["step_type"] == "user_input":
                messages.append(AgentMessage(role="user", content=step["content"]))
                
            elif step["step_type"] == "agent_message":
                messages.append(AgentMessage(role="assistant", content=step["content"]))
                
            elif step["step_type"] == "tool_call":
                # We append tool calls to the previous assistant message or create a new one
                if not messages or messages[-1].role != "assistant":
                    msg = AgentMessage(role="assistant", content="", tool_calls=[])
                    messages.append(msg)
                
                messages[-1].tool_calls.append(
                    ToolCall(
                        tool_name=step["tool_name"],
                        arguments=step["tool_arguments"],
                        call_id=step["tool_call_id"]
                    )
                )
                
            elif step["step_type"] == "tool_result":
                import json
                result_str = json.dumps(step["tool_result"])
                messages.append(AgentMessage(
                    role="tool", 
                    content=result_str,
                    tool_call_id=step["tool_call_id"],
                    tool_name=step["tool_name"]
                ))
                
        return messages

    def get_trace(self) -> List[Dict[str, Any]]:
        """Return the complete recorded trace."""
        return self.steps
