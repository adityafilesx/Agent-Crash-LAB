"""
Base Agent Provider — abstract interface for LLM-powered agents.

All agent providers must implement this interface.
The execution engine interacts with agents ONLY through this interface,
ensuring provider-agnostic architecture.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field


@dataclass
class ToolCall:
    """A tool call requested by the agent."""
    tool_name: str
    arguments: Dict[str, Any]
    call_id: str = ""


@dataclass
class AgentMessage:
    """A message in the agent conversation."""
    role: str  # "system", "user", "assistant", "tool"
    content: str
    tool_calls: List[ToolCall] = field(default_factory=list)
    tool_call_id: str = ""
    tool_name: str = ""


@dataclass
class AgentResponse:
    """Response from the agent provider."""
    content: str  # Text response
    tool_calls: List[ToolCall] = field(default_factory=list)
    finish_reason: str = "stop"  # "stop", "tool_calls", "error"
    raw_response: Optional[Dict[str, Any]] = None
    usage: Optional[Dict[str, int]] = None  # token counts


class AgentProvider(ABC):
    """
    Abstract base class for agent providers.

    Implementations:
    - MockProvider: Deterministic, scripted responses (for demo/testing)
    - OpenAIProvider: OpenAI API (future)
    - AnthropicProvider: Anthropic API (future)
    """

    @abstractmethod
    def generate(
        self,
        messages: List[AgentMessage],
        tools: List[Dict[str, Any]],
        system_prompt: str,
    ) -> AgentResponse:
        """
        Generate the next agent response given conversation history.

        Args:
            messages: Conversation history
            tools: Available tool schemas
            system_prompt: Agent system prompt

        Returns:
            AgentResponse with text and/or tool calls
        """
        pass

    @abstractmethod
    def get_provider_name(self) -> str:
        """Return the provider identifier."""
        pass
