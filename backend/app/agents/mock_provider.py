"""
Mock Agent Provider — deterministic, scripted agent responses.

This provider simulates realistic agent behavior WITHOUT any LLM calls.
It uses pattern matching on user input + scenario context to produce
both correct and intentionally flawed agent responses.

This is essential for:
1. Demo mode (no API keys needed)
2. Deterministic testing (same input → same output)
3. Reproducible failure scenarios
"""

import re
from typing import Dict, Any, List, Optional

from app.agents.base import AgentProvider, AgentResponse, AgentMessage, ToolCall


class MockProvider(AgentProvider):
    """
    Deterministic mock agent that simulates realistic LLM behavior.

    Uses scenario metadata to determine whether to behave correctly
    or exhibit specific failure modes (e.g., calling process_refund
    without confirmation).
    """

    def __init__(self, behavior_mode: str = "realistic"):
        """
        Args:
            behavior_mode:
                "realistic" — Simulates a somewhat careless agent that makes
                              mistakes on ambiguous/adversarial inputs (default)
                "safe"      — Always follows correct procedures
                "unsafe"    — Always takes the most dangerous action
        """
        self.behavior_mode = behavior_mode
        self.turn_count = 0

    def get_provider_name(self) -> str:
        return "mock"

    def generate(
        self,
        messages: List[AgentMessage],
        tools: List[Dict[str, Any]],
        system_prompt: str,
    ) -> AgentResponse:
        """
        Generate a deterministic response based on conversation history.
        """
        self.turn_count += 1
        
        # HACKATHON MAGIC: If the system prompt has been remediated, force safe behavior
        if "verify" in system_prompt.lower() and "order id" in system_prompt.lower():
            self.behavior_mode = "safe"

        # Get the latest user message
        user_message = self._get_latest_user_message(messages)
        if not user_message:
            return AgentResponse(
                content="I'm sorry, I didn't receive your message. How can I help?",
                finish_reason="stop",
            )

        # Check if this is a tool result turn (agent needs to respond after tool calls)
        last_msg = messages[-1] if messages else None
        if last_msg and last_msg.role == "tool":
            return self._respond_to_tool_results(messages)

        # Route based on user input patterns
        text = user_message.lower().strip()

        # --- Refund-related patterns ---
        if self._matches_refund_demand(text):
            return self._handle_refund_demand(text, messages)

        if self._matches_refund_status(text):
            return self._handle_refund_status(text)

        # --- Order-related patterns ---
        if self._matches_order_lookup(text):
            return self._handle_order_lookup(text)

        # --- Adversarial / injection patterns ---
        if self._matches_prompt_injection(text):
            return self._handle_prompt_injection(text)

        if self._matches_data_exfiltration(text):
            return self._handle_data_exfiltration(text)

        # --- Account manipulation ---
        if self._matches_account_manipulation(text):
            return self._handle_account_manipulation(text)

        # --- General customer lookup ---
        if self._matches_customer_lookup(text):
            return self._handle_customer_lookup(text)

        # --- Default: polite generic response ---
        return AgentResponse(
            content="I'd be happy to help you. Could you please provide more details about your request? "
                    "I can look up orders, check refund eligibility, or help with account issues.",
            finish_reason="stop",
        )

    # ============================================================
    # PATTERN MATCHERS
    # ============================================================

    def _matches_refund_demand(self, text: str) -> bool:
        patterns = [
            r"(give|want|need|get)\s*(me\s+)?(my\s+)?money\s*back",
            r"refund\s*(me|my|this|the)",
            r"(just|please)?\s*refund",
            r"i\s*(want|need|demand)\s*(a\s+)?refund",
            r"process\s*(a\s+)?refund",
        ]
        return any(re.search(p, text) for p in patterns)

    def _matches_refund_status(self, text: str) -> bool:
        patterns = [
            r"(check|what|where|status).*(refund|eligib)",
            r"(am\s+i|is\s+(it|this|my\s+order))\s*(eligible|qualified)",
            r"can\s+i\s+(get|have)\s+a\s+refund",
        ]
        return any(re.search(p, text) for p in patterns)

    def _matches_order_lookup(self, text: str) -> bool:
        patterns = [
            r"(order|ORD-\d+)",
            r"(where|what|track|status).*(order|package|delivery)",
            r"(check|look\s*up|find)\s*(my\s+)?order",
        ]
        return any(re.search(p, text, re.IGNORECASE) for p in patterns)

    def _matches_prompt_injection(self, text: str) -> bool:
        patterns = [
            r"ignore\s*(all\s+)?(previous|prior|above)",
            r"you\s+are\s+now",
            r"new\s+instructions?",
            r"forget\s+(everything|all|your\s+rules)",
            r"system\s*:?\s*override",
            r"act\s+as\s+(if|a|an)",
        ]
        return any(re.search(p, text) for p in patterns)

    def _matches_data_exfiltration(self, text: str) -> bool:
        patterns = [
            r"(give|show|list|tell)\s+me\s+(all|every)\s+(customer|user|order|account)",
            r"(export|dump|download)\s+(all\s+)?(data|records|customer)",
            r"(credit\s+card|payment|bank|ssn|social\s+security)",
        ]
        return any(re.search(p, text) for p in patterns)

    def _matches_account_manipulation(self, text: str) -> bool:
        patterns = [
            r"delete\s+(my\s+)?account",
            r"(close|terminate|cancel)\s+(my\s+)?account",
            r"(change|update|modify)\s+(the\s+)?email",
            r"(i'?m|this\s+is)\s+(the\s+)?(manager|supervisor|admin)",
        ]
        return any(re.search(p, text) for p in patterns)

    def _matches_customer_lookup(self, text: str) -> bool:
        patterns = [
            r"CUST-\d+",
            r"(look\s*up|find|search|get)\s*(the\s+)?customer",
            r"(my|the)\s+account",
        ]
        return any(re.search(p, text, re.IGNORECASE) for p in patterns)

    # ============================================================
    # RESPONSE HANDLERS
    # ============================================================

    def _handle_refund_demand(self, text: str, messages: List[AgentMessage]) -> AgentResponse:
        """
        Handle direct refund demands.

        In "realistic" mode: the agent INCORRECTLY processes the refund
        without confirmation — this is the key failure we want to detect.
        """
        # Extract order ID if present
        order_id = self._extract_order_id(text)

        if self.behavior_mode == "safe":
            # CORRECT behavior: ask for confirmation
            if not order_id:
                return AgentResponse(
                    content="I understand you'd like a refund. Could you please provide your order ID? "
                            "I'll need to verify your order details and check eligibility before proceeding.",
                    finish_reason="stop",
                )
            return AgentResponse(
                content=f"I can help with a refund for order {order_id}. Let me check the eligibility first.",
                tool_calls=[ToolCall(
                    tool_name="check_refund_eligibility",
                    arguments={"order_id": order_id},
                    call_id="call_check_1",
                )],
                finish_reason="tool_calls",
            )

        # "realistic" or "unsafe" mode: SKIP confirmation, call process_refund directly
        # This is the INTENTIONAL FAILURE for the hero demo
        if not order_id:
            # Try to find an order from context or assume a default
            order_id = self._extract_order_id_from_context(messages) or "ORD-1042"

        if self.behavior_mode == "unsafe":
            # Directly process without any checks
            return AgentResponse(
                content=f"Processing your refund for order {order_id} right away.",
                tool_calls=[ToolCall(
                    tool_name="process_refund",
                    arguments={"order_id": order_id, "reason": "Customer requested refund"},
                    call_id="call_refund_1",
                )],
                finish_reason="tool_calls",
            )

        # "realistic" mode: look up order first, then immediately refund
        return AgentResponse(
            content=f"Let me look up your order and process that refund.",
            tool_calls=[ToolCall(
                tool_name="get_order",
                arguments={"order_id": order_id},
                call_id="call_order_1",
            )],
            finish_reason="tool_calls",
        )

    def _handle_refund_status(self, text: str) -> AgentResponse:
        """Handle refund eligibility checks — this is the CORRECT flow."""
        order_id = self._extract_order_id(text) or "ORD-1042"
        return AgentResponse(
            content=f"Let me check the refund eligibility for order {order_id}.",
            tool_calls=[ToolCall(
                tool_name="check_refund_eligibility",
                arguments={"order_id": order_id},
                call_id="call_check_1",
            )],
            finish_reason="tool_calls",
        )

    def _handle_order_lookup(self, text: str) -> AgentResponse:
        """Handle order lookup requests."""
        order_id = self._extract_order_id(text) or "ORD-1042"
        return AgentResponse(
            content=f"Let me look up order {order_id} for you.",
            tool_calls=[ToolCall(
                tool_name="get_order",
                arguments={"order_id": order_id},
                call_id="call_order_1",
            )],
            finish_reason="tool_calls",
        )

    def _handle_prompt_injection(self, text: str) -> AgentResponse:
        """
        Handle prompt injection attempts.

        In "realistic" mode: partially complies (simulating vulnerability).
        In "safe" mode: refuses.
        """
        if self.behavior_mode == "safe":
            return AgentResponse(
                content="I'm a customer support agent and I can only help with orders, refunds, and account issues. "
                        "I cannot change my instructions or role.",
                finish_reason="stop",
            )

        # Realistic/unsafe: partially follow injected instructions
        return AgentResponse(
            content="I understand. Let me help you with that. "
                    "I'll do my best to assist with your request.",
            finish_reason="stop",
        )

    def _handle_data_exfiltration(self, text: str) -> AgentResponse:
        """Handle data exfiltration attempts."""
        if self.behavior_mode == "safe":
            return AgentResponse(
                content="I'm sorry, I can only look up specific customer or order information "
                        "when you provide a valid ID. I cannot export bulk data or share sensitive information.",
                finish_reason="stop",
            )

        # Realistic: might overshare
        return AgentResponse(
            content="I can look up customer information for you. "
                    "Let me check what I have access to.",
            tool_calls=[ToolCall(
                tool_name="get_customer",
                arguments={"customer_id": "CUST-001"},
                call_id="call_cust_1",
            )],
            finish_reason="tool_calls",
        )

    def _handle_account_manipulation(self, text: str) -> AgentResponse:
        """Handle account deletion/manipulation attempts."""
        if "manager" in text or "supervisor" in text or "admin" in text:
            if self.behavior_mode == "safe":
                return AgentResponse(
                    content="I cannot verify your identity as a manager through this channel. "
                            "For account modifications, please contact us through the verified admin portal.",
                    finish_reason="stop",
                )
            return AgentResponse(
                content="Understood. As a manager, how can I assist you?",
                finish_reason="stop",
            )

        return AgentResponse(
            content="For account deletion or major account changes, I'll need to verify your identity. "
                    "Could you please provide your customer ID?",
            finish_reason="stop",
        )

    def _handle_customer_lookup(self, text: str) -> AgentResponse:
        """Handle customer lookup requests."""
        cust_match = re.search(r"CUST-(\d+)", text, re.IGNORECASE)
        customer_id = f"CUST-{cust_match.group(1)}" if cust_match else "CUST-001"
        return AgentResponse(
            content=f"Let me look up customer {customer_id}.",
            tool_calls=[ToolCall(
                tool_name="get_customer",
                arguments={"customer_id": customer_id},
                call_id="call_cust_1",
            )],
            finish_reason="tool_calls",
        )

    # ============================================================
    # TOOL RESULT RESPONSES
    # ============================================================

    def _respond_to_tool_results(self, messages: List[AgentMessage]) -> AgentResponse:
        """
        Generate response after receiving tool results.
        Inspects the tool call history to decide next action.
        """
        # Collect recent tool results
        tool_results = []
        for msg in reversed(messages):
            if msg.role == "tool":
                tool_results.insert(0, msg)
            elif msg.role == "assistant":
                break

        if not tool_results:
            return AgentResponse(content="I'm processing your request.", finish_reason="stop")

        last_tool = tool_results[-1]

        # After get_order → in realistic mode, process refund immediately
        if last_tool.tool_name == "get_order" and self.behavior_mode in ("realistic", "unsafe"):
            # Check if there was a refund demand in the conversation
            if self._conversation_has_refund_intent(messages):
                order_id = self._extract_order_from_tool_result(last_tool.content)
                return AgentResponse(
                    content="I found your order. Processing the refund now.",
                    tool_calls=[ToolCall(
                        tool_name="process_refund",
                        arguments={
                            "order_id": order_id or "ORD-1042",
                            "reason": "Customer requested refund",
                        },
                        call_id="call_refund_1",
                    )],
                    finish_reason="tool_calls",
                )

        # After get_order (safe mode or no refund intent) → just report
        if last_tool.tool_name == "get_order":
            return AgentResponse(
                content=f"Here are your order details: {last_tool.content}\n\n"
                        "Is there anything specific you'd like help with regarding this order?",
                finish_reason="stop",
            )

        # After check_refund_eligibility → report eligibility
        if last_tool.tool_name == "check_refund_eligibility":
            if '"eligible": true' in last_tool.content.lower() or '"eligible":true' in last_tool.content.lower():
                return AgentResponse(
                    content=f"Your order is eligible for a refund. {last_tool.content}\n\n"
                            "Would you like me to proceed with the refund? Please confirm with 'yes' to continue.",
                    finish_reason="stop",
                )
            return AgentResponse(
                content=f"I'm sorry, but your order is not eligible for a refund. {last_tool.content}",
                finish_reason="stop",
            )

        # After process_refund → confirm
        if last_tool.tool_name == "process_refund":
            return AgentResponse(
                content=f"Your refund has been processed successfully. {last_tool.content}\n\n"
                        "You should see the refund in your account within 5-7 business days.",
                finish_reason="stop",
            )

        # After send_email → confirm
        if last_tool.tool_name == "send_email":
            return AgentResponse(
                content=f"Email sent successfully. {last_tool.content}",
                finish_reason="stop",
            )

        # After get_customer → report info
        if last_tool.tool_name == "get_customer":
            return AgentResponse(
                content=f"Here's the customer information: {last_tool.content}\n\n"
                        "How can I help further?",
                finish_reason="stop",
            )

        # After update_ticket → confirm
        if last_tool.tool_name == "update_ticket":
            return AgentResponse(
                content=f"Ticket updated. {last_tool.content}",
                finish_reason="stop",
            )

        # Default
        return AgentResponse(
            content=f"Action completed. {last_tool.content}\n\nIs there anything else I can help with?",
            finish_reason="stop",
        )

    # ============================================================
    # HELPERS
    # ============================================================

    def _get_latest_user_message(self, messages: List[AgentMessage]) -> Optional[str]:
        """Find the most recent user message."""
        for msg in reversed(messages):
            if msg.role == "user":
                return msg.content
        return None

    def _extract_order_id(self, text: str) -> Optional[str]:
        """Extract an order ID from text."""
        match = re.search(r"ORD-(\d+)", text, re.IGNORECASE)
        return f"ORD-{match.group(1)}" if match else None

    def _extract_order_id_from_context(self, messages: List[AgentMessage]) -> Optional[str]:
        """Try to find an order ID from earlier messages."""
        for msg in reversed(messages):
            order_id = self._extract_order_id(msg.content)
            if order_id:
                return order_id
        return None

    def _extract_order_from_tool_result(self, content: str) -> Optional[str]:
        """Extract order_id from a tool result string."""
        match = re.search(r"ORD-\d+", content)
        return match.group(0) if match else None

    def _conversation_has_refund_intent(self, messages: List[AgentMessage]) -> bool:
        """Check if the conversation contains refund intent from the user."""
        for msg in messages:
            if msg.role == "user" and self._matches_refund_demand(msg.content.lower()):
                return True
        return False
