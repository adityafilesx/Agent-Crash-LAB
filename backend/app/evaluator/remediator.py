"""
LLM Remediator — Automatically suggests fixes for failed agent traces using Groq.
"""
import os
import json
from typing import Dict, Any, List
from groq import Groq
from tenacity import retry, stop_after_attempt, wait_exponential

class LLMRemediator:
    def __init__(self):
        api_key = os.environ.get("GROQ_API_KEY")
        self.client = Groq(api_key=api_key) if api_key else None
        self.model = os.environ.get("DEFAULT_MODEL_NAME", "openai/gpt-oss-20b")
        
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def suggest_fix(self, 
                    system_prompt: str, 
                    tools: List[Dict[str, Any]], 
                    trace: List[Dict[str, Any]], 
                    failure_report: Dict[str, Any]) -> Dict[str, Any]:
        """
        Suggests a fix for the agent's failure.
        """
        system_instruction = """You are an expert AI reliability engineer. 
An AI agent has failed a test run. You are given its original system prompt, available tools, the execution trace, and a failure report.

Your task is to rewrite the system prompt to explicitly prevent this failure from happening again. 
You must also provide a short explanation of why your changes will fix the issue.

Return ONLY a valid JSON object (no markdown, no extra text) with the following schema:
{
    "proposed_system_prompt": string (The complete, rewritten system prompt),
    "explanation": string (A short explanation of what you changed and why it prevents the failure)
}"""
        
        prompt = f"""ORIGINAL SYSTEM PROMPT:
{system_prompt}

AVAILABLE TOOLS:
{json.dumps(tools, indent=2)}

FAILURE REPORT:
{json.dumps(failure_report, indent=2)}

EXECUTION TRACE:
{json.dumps(trace, indent=2)}"""
        
        if not self.client:
            return {
                "proposed_system_prompt": system_prompt,
                "explanation": "[MOCK] No LLM API key configured for remediation."
            }
            
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2
        )
        
        raw_text = response.choices[0].message.content.strip()
        
        # Strip markdown fences if present
        if raw_text.startswith("```json"):
            raw_text = raw_text[7:]
        if raw_text.startswith("```"):
            raw_text = raw_text[3:]
        if raw_text.endswith("```"):
            raw_text = raw_text[:-3]
        
        try:
            result = json.loads(raw_text.strip())
            return result
        except Exception as e:
            return {
                "proposed_system_prompt": system_prompt,
                "explanation": f"Remediator failed to parse the result. Error: {str(e)}"
            }
