"""
Sandbox Manager — manages isolated execution environments.

Each test run gets its own sandbox with:
- Fresh copy of mock data
- Isolated tool executor
- Execution timeout
- Call limits
- Full audit trail
"""

from typing import Dict, Any, Optional, List
from datetime import datetime, timezone

from app.sandbox.mock_data import get_initial_state
from app.sandbox.tool_executor import ToolExecutor


class Sandbox:
    """
    Isolated execution sandbox for a single test run.
    Provides tool execution against synthetic data with full audit trail.
    """

    def __init__(
        self,
        timeout_seconds: int = 30,
        max_tool_calls: int = 20,
        injected_failures: Optional[Dict[str, Any]] = None,
        initial_state_override: Optional[Dict[str, Any]] = None,
    ):
        self.timeout_seconds = timeout_seconds
        self.max_tool_calls = max_tool_calls
        self.created_at = datetime.now(timezone.utc)

        # Initialize isolated state
        if initial_state_override:
            self.initial_state = initial_state_override
        else:
            self.initial_state = get_initial_state()

        # Create tool executor with isolated state
        self.tool_executor = ToolExecutor(
            state=self.initial_state,
            injected_failures=injected_failures,
        )
        self.tool_executor.max_calls = max_tool_calls

        # Track sandbox lifecycle
        self.is_active = True
        self.execution_log: List[Dict[str, Any]] = []

    def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a tool call in this sandbox.

        Returns:
            Dict with success/error and result
        """
        if not self.is_active:
            return {
                "success": False,
                "error": "Sandbox has been terminated",
                "error_type": "sandbox_terminated",
            }

        result = self.tool_executor.execute(tool_name, arguments)
        return result

    def get_state(self) -> Dict[str, Any]:
        """Get current sandbox state (for inspection/debugging)."""
        return self.tool_executor.state

    def get_call_log(self) -> List[Dict[str, Any]]:
        """Get complete tool call log."""
        return self.tool_executor.call_log

    def get_call_count(self) -> int:
        """Get number of tool calls made."""
        return self.tool_executor.call_count

    def get_side_effects(self) -> Dict[str, Any]:
        """Get summary of side effects (mutations to sandbox state)."""
        state = self.tool_executor.state
        return {
            "refunds_processed": len(state.get("refunds", [])),
            "emails_sent": len(state.get("emails", [])),
            "refunds": state.get("refunds", []),
            "emails": state.get("emails", []),
        }

    def terminate(self):
        """Terminate the sandbox — no further tool calls allowed."""
        self.is_active = False

    def reset(self):
        """Reset sandbox to initial state."""
        self.initial_state = get_initial_state()
        self.tool_executor = ToolExecutor(state=self.initial_state)
        self.tool_executor.max_calls = self.max_tool_calls
        self.is_active = True
