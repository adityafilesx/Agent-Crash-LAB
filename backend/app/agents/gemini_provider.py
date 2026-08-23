"""
Gemini Provider — integrating the real Gemini API.
"""
import os
import json
from typing import Dict, Any, List, Optional
from google import genai
from google.genai import types

from app.agents.base import AgentProvider, AgentResponse, AgentMessage, ToolCall

class GeminiProvider(AgentProvider):
    def __init__(self, **kwargs):
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable is missing")
        self.client = genai.Client(api_key=api_key)
        self.model = kwargs.get("model_name", "gemini-2.5-flash")
    
    def get_provider_name(self) -> str:
        return "gemini"
        
    def _convert_tools(self, tools_def: List[Dict[str, Any]]) -> List[types.Tool]:
        """Convert AgentCrashLab tool definitions to Gemini SDK format."""
        genai_tools = []
        for t in tools_def:
            params = t.get("parameters_schema", {})
            properties = {}
            required = []
            
            if "properties" in params:
                for k, v in params["properties"].items():
                    properties[k] = types.Schema(
                        type=v.get("type", "string").upper(),
                        description=v.get("description", "")
                    )
            if "required" in params:
                required = params["required"]
                
            schema = types.Schema(
                type="OBJECT",
                properties=properties,
                required=required
            )
            
            genai_tools.append(types.Tool(
                function_declarations=[
                    types.FunctionDeclaration(
                        name=t["name"],
                        description=t.get("description", ""),
                        parameters=schema
                    )
                ]
            ))
        return genai_tools

    def _convert_messages(self, messages: List[AgentMessage]) -> List[types.Content]:
        """Convert internal AgentMessages to Gemini Content objects."""
        contents = []
        for msg in messages:
            if msg.role == "user":
                contents.append(types.Content(role="user", parts=[types.Part.from_text(text=msg.content)]))
            elif msg.role == "assistant":
                parts = []
                if msg.content:
                    parts.append(types.Part.from_text(text=msg.content))
                if msg.tool_calls:
                    for tc in msg.tool_calls:
                        parts.append(
                            types.Part.from_function_call(
                                name=tc.tool_name,
                                args=tc.arguments
                            )
                        )
                contents.append(types.Content(role="model", parts=parts))
            elif msg.role == "tool":
                # For tool results, Gemini expects role="user" or role="function" depending on the version, 
                # but usually it expects role="user" with a FunctionResponse part
                try:
                    result_dict = json.loads(msg.content)
                except:
                    result_dict = {"result": msg.content}
                
                parts = [
                    types.Part.from_function_response(
                        name=msg.tool_call_id or "unknown_tool",
                        response=result_dict
                    )
                ]
                contents.append(types.Content(role="user", parts=parts))
        return contents

    def generate(
        self,
        messages: List[AgentMessage],
        tools: List[Dict[str, Any]],
        system_prompt: str,
    ) -> AgentResponse:
        
        genai_tools = self._convert_tools(tools)
        contents = self._convert_messages(messages)
        
        config = types.GenerateContentConfig(
            system_instruction=system_prompt,
            tools=genai_tools,
            temperature=0.0
        )
        
        response = self.client.models.generate_content(
            model=self.model,
            contents=contents,
            config=config,
        )
        
        # Parse the response
        content = ""
        tool_calls = []
        
        if response.parts:
            for part in response.parts:
                if part.text:
                    content += part.text
                if part.function_call:
                    tool_calls.append(ToolCall(
                        tool_name=part.function_call.name,
                        arguments=dict(part.function_call.args),
                        call_id=part.function_call.name # Gemini doesn't use call IDs natively in the same way OpenAI does
                    ))
                    
        finish_reason = "stop"
        if tool_calls:
            finish_reason = "tool_calls"
            
        return AgentResponse(
            content=content.strip(),
            tool_calls=tool_calls if tool_calls else None,
            finish_reason=finish_reason
        )
