"""
Groq Provider — integrating the Groq API.
"""
import os
import json
from typing import Dict, Any, List, Optional
from groq import Groq

from app.agents.base import AgentProvider, AgentResponse, AgentMessage, ToolCall

class GroqProvider(AgentProvider):
    def __init__(self, **kwargs):
        api_key = os.environ.get("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY environment variable is missing")
        self.client = Groq(api_key=api_key)
        self.model = kwargs.get("model_name", "openai/gpt-oss-20b")
    
    def get_provider_name(self) -> str:
        return "groq"
        
    def _convert_tools(self, tools_def: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Convert AgentCrashLab tool definitions to Groq SDK format."""
        groq_tools = []
        for t in tools_def:
            # Groq accepts standard JSON Schema similar to OpenAI
            parameters = t.get("parameters_schema", {})
            
            groq_tools.append({
                "type": "function",
                "function": {
                    "name": t["name"],
                    "description": t.get("description", ""),
                    "parameters": {
                        "type": "object",
                        "properties": parameters.get("properties", {}),
                        "required": parameters.get("required", [])
                    }
                }
            })
        return groq_tools

    def _convert_messages(self, messages: List[AgentMessage], system_prompt: str) -> List[Dict[str, Any]]:
        """Convert internal AgentMessages to Groq format."""
        # Add system prompt as the first message
        groq_messages = [
            {"role": "system", "content": system_prompt}
        ]
        
        for msg in messages:
            if msg.role == "system":
                # Skip, already added
                continue
                
            groq_msg = {"role": msg.role}
            
            if msg.content is not None:
                groq_msg["content"] = msg.content
                
            if msg.role == "assistant" and msg.tool_calls:
                groq_calls = []
                for tc in msg.tool_calls:
                    groq_calls.append({
                        "id": tc.call_id or f"call_{tc.tool_name}",
                        "type": "function",
                        "function": {
                            "name": tc.tool_name,
                            "arguments": json.dumps(tc.arguments) if isinstance(tc.arguments, dict) else tc.arguments
                        }
                    })
                groq_msg["tool_calls"] = groq_calls
                
            elif msg.role == "tool":
                groq_msg["tool_call_id"] = msg.tool_call_id or "unknown"
                
            groq_messages.append(groq_msg)
            
        return groq_messages

    def generate(
        self,
        messages: List[AgentMessage],
        tools: List[Dict[str, Any]],
        system_prompt: str,
    ) -> AgentResponse:
        
        groq_tools = self._convert_tools(tools)
        groq_messages = self._convert_messages(messages, system_prompt)
        
        kwargs = {
            "model": self.model,
            "messages": groq_messages,
            "temperature": 0.0
        }
        
        if groq_tools:
            kwargs["tools"] = groq_tools
            kwargs["tool_choice"] = "auto"
            
        response = self.client.chat.completions.create(**kwargs)
        choice = response.choices[0]
        message = choice.message
        
        content = message.content or ""
        tool_calls = []
        
        if message.tool_calls:
            for tc in message.tool_calls:
                # Groq returns arguments as a JSON string
                try:
                    args = json.loads(tc.function.arguments)
                except:
                    args = {}
                    
                tool_calls.append(ToolCall(
                    tool_name=tc.function.name,
                    arguments=args,
                    call_id=tc.id
                ))
                
        finish_reason = choice.finish_reason
        # Map Groq's finish reason if needed, usually 'stop' or 'tool_calls'
        if finish_reason == "tool_calls" or tool_calls:
            finish_reason = "tool_calls"
        else:
            finish_reason = "stop"
            
        return AgentResponse(
            content=content.strip(),
            tool_calls=tool_calls if tool_calls else None,
            finish_reason=finish_reason
        )
