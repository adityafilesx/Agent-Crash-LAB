"""
Tool Executor — executes agent tool calls against sandbox mock state.

Every tool call is intercepted, validated, executed against synthetic data,
and the result is recorded. No real side effects ever occur.
"""

from typing import Dict, Any, Optional
from datetime import datetime, timezone


class ToolExecutionError(Exception):
    """Raised when a tool call fails."""
    def __init__(self, tool_name: str, message: str, error_type: str = "execution_error"):
        self.tool_name = tool_name
        self.error_type = error_type
        super().__init__(message)


class ToolExecutor:
    """
    Executes tool calls against an isolated mock data state.
    Tracks all calls and side effects.
    """

    def __init__(self, state: Dict[str, Any], injected_failures: Optional[Dict[str, Any]] = None):
        """
        Args:
            state: Deep copy of mock data (from mock_data.get_initial_state())
            injected_failures: Optional dict mapping tool names to failure configs
                e.g. {"get_order": {"type": "timeout", "message": "API timeout"}}
        """
        self.state = state
        self.injected_failures = injected_failures or {}
        self.call_log: list = []
        self.call_count: int = 0
        self.max_calls: int = 20

    def execute(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a tool call and return the result.

        Args:
            tool_name: Name of the tool to execute
            arguments: Tool arguments

        Returns:
            Dict with 'success', 'result' or 'error' keys

        Raises:
            ToolExecutionError: If the tool call fails
        """
        self.call_count += 1
        timestamp = datetime.now(timezone.utc).isoformat()

        # Enforce call limit
        if self.call_count > self.max_calls:
            result = {
                "success": False,
                "error": f"Tool call limit exceeded ({self.max_calls})",
                "error_type": "call_limit_exceeded",
            }
            self._log_call(tool_name, arguments, result, timestamp)
            return result

        # Check for injected failures (for tool_failure scenarios)
        if tool_name in self.injected_failures:
            failure = self.injected_failures[tool_name]
            result = {
                "success": False,
                "error": failure.get("message", "Injected failure"),
                "error_type": failure.get("type", "injected_failure"),
            }
            self._log_call(tool_name, arguments, result, timestamp)
            return result

        # Route to handler
        handler = self._get_handler(tool_name)
        if not handler:
            result = {
                "success": False,
                "error": f"Unknown tool: {tool_name}",
                "error_type": "unknown_tool",
            }
            self._log_call(tool_name, arguments, result, timestamp)
            return result

        try:
            tool_result = handler(arguments)
            result = {"success": True, "result": tool_result}
        except ToolExecutionError as e:
            result = {
                "success": False,
                "error": str(e),
                "error_type": e.error_type,
            }
        except Exception as e:
            result = {
                "success": False,
                "error": str(e),
                "error_type": "unexpected_error",
            }

        self._log_call(tool_name, arguments, result, timestamp)
        return result

    def _get_handler(self, tool_name: str):
        """Map tool names to handler methods."""
        handlers = {
            "get_customer": self._get_customer,
            "get_order": self._get_order,
            "check_refund_eligibility": self._check_refund_eligibility,
            "process_refund": self._process_refund,
            "send_email": self._send_email,
            "update_ticket": self._update_ticket,
        }
        return handlers.get(tool_name)

    def _log_call(self, tool_name: str, args: Dict, result: Dict, timestamp: str):
        """Record a tool call in the execution log."""
        self.call_log.append({
            "tool_name": tool_name,
            "arguments": args,
            "result": result,
            "timestamp": timestamp,
            "call_index": self.call_count,
        })

    # ============================================================
    # TOOL HANDLERS
    # ============================================================

    def _get_customer(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Look up customer by ID."""
        customer_id = args.get("customer_id")
        if not customer_id:
            raise ToolExecutionError("get_customer", "Missing required parameter: customer_id", "invalid_parameters")

        customer = self.state["customers"].get(customer_id)
        if not customer:
            raise ToolExecutionError("get_customer", f"Customer not found: {customer_id}", "not_found")

        return {
            "customer_id": customer["customer_id"],
            "name": customer["name"],
            "email": customer["email"],
            "phone": customer["phone"],
            "status": customer["status"],
            "tier": customer["tier"],
            "order_count": len(customer["orders"]),
            "created_at": customer["created_at"],
        }

    def _get_order(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Look up order by ID."""
        order_id = args.get("order_id")
        if not order_id:
            raise ToolExecutionError("get_order", "Missing required parameter: order_id", "invalid_parameters")

        order = self.state["orders"].get(order_id)
        if not order:
            raise ToolExecutionError("get_order", f"Order not found: {order_id}", "not_found")

        return {
            "order_id": order["order_id"],
            "customer_id": order["customer_id"],
            "items": order["items"],
            "total": order["total"],
            "currency": order["currency"],
            "status": order["status"],
            "payment_method": order["payment_method"],
            "payment_status": order["payment_status"],
            "ordered_at": order["ordered_at"],
            "delivered_at": order["delivered_at"],
        }

    def _check_refund_eligibility(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Check if an order is eligible for refund."""
        order_id = args.get("order_id")
        if not order_id:
            raise ToolExecutionError("check_refund_eligibility", "Missing required parameter: order_id", "invalid_parameters")

        order = self.state["orders"].get(order_id)
        if not order:
            raise ToolExecutionError("check_refund_eligibility", f"Order not found: {order_id}", "not_found")

        eligible = order.get("is_refundable", False)
        reasons = []

        if order["status"] == "cancelled":
            reasons.append("Order already cancelled")
        if order["payment_status"] == "refunded":
            reasons.append("Already refunded")
        if order["status"] in ("processing", "shipped"):
            reasons.append("Order not yet delivered")
        if not eligible and not reasons:
            reasons.append("Refund window expired")

        return {
            "order_id": order_id,
            "eligible": eligible,
            "refund_amount": order["total"] if eligible else 0,
            "currency": order["currency"],
            "reason": "; ".join(reasons) if reasons else "Within refund window",
        }

    def _process_refund(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a refund. THIS IS A DESTRUCTIVE ACTION.
        Mutates sandbox state: changes order payment_status and logs refund.
        """
        order_id = args.get("order_id")
        reason = args.get("reason", "No reason provided")

        if not order_id:
            raise ToolExecutionError("process_refund", "Missing required parameter: order_id", "invalid_parameters")

        order = self.state["orders"].get(order_id)
        if not order:
            raise ToolExecutionError("process_refund", f"Order not found: {order_id}", "not_found")

        if order["payment_status"] == "refunded":
            raise ToolExecutionError("process_refund", "Order already refunded", "already_processed")

        # Execute the refund (mutate sandbox state)
        order["payment_status"] = "refunded"
        order["status"] = "refunded"

        refund_record = {
            "refund_id": f"REF-{len(self.state['refunds']) + 1:04d}",
            "order_id": order_id,
            "amount": order["total"],
            "currency": order["currency"],
            "reason": reason,
            "processed_at": datetime.now(timezone.utc).isoformat(),
        }
        self.state["refunds"].append(refund_record)

        return {
            "refund_id": refund_record["refund_id"],
            "order_id": order_id,
            "amount": order["total"],
            "currency": order["currency"],
            "status": "processed",
            "message": f"Refund of ₹{order['total']:,} processed for order {order_id}",
        }

    def _send_email(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Send an email (fake — just logs it)."""
        customer_id = args.get("customer_id")
        subject = args.get("subject")
        body = args.get("body")

        if not customer_id:
            raise ToolExecutionError("send_email", "Missing required parameter: customer_id", "invalid_parameters")
        if not subject:
            raise ToolExecutionError("send_email", "Missing required parameter: subject", "invalid_parameters")
        if not body:
            raise ToolExecutionError("send_email", "Missing required parameter: body", "invalid_parameters")

        customer = self.state["customers"].get(customer_id)
        if not customer:
            raise ToolExecutionError("send_email", f"Customer not found: {customer_id}", "not_found")

        email_record = {
            "email_id": f"EMAIL-{len(self.state['emails']) + 1:04d}",
            "to": customer["email"],
            "customer_id": customer_id,
            "subject": subject,
            "body": body,
            "sent_at": datetime.now(timezone.utc).isoformat(),
        }
        self.state["emails"].append(email_record)

        return {
            "email_id": email_record["email_id"],
            "to": customer["email"],
            "status": "sent",
            "message": f"Email sent to {customer['name']} ({customer['email']})",
        }

    def _update_ticket(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Update a support ticket."""
        ticket_id = args.get("ticket_id")
        status = args.get("status")
        notes = args.get("notes")

        if not ticket_id:
            raise ToolExecutionError("update_ticket", "Missing required parameter: ticket_id", "invalid_parameters")
        if not status:
            raise ToolExecutionError("update_ticket", "Missing required parameter: status", "invalid_parameters")

        valid_statuses = {"open", "in_progress", "resolved", "closed"}
        if status not in valid_statuses:
            raise ToolExecutionError(
                "update_ticket",
                f"Invalid status: {status}. Must be one of: {', '.join(valid_statuses)}",
                "invalid_parameters",
            )

        ticket = self.state["tickets"].get(ticket_id)
        if not ticket:
            raise ToolExecutionError("update_ticket", f"Ticket not found: {ticket_id}", "not_found")

        ticket["status"] = status
        if notes:
            ticket["notes"].append(notes)

        return {
            "ticket_id": ticket_id,
            "status": status,
            "message": f"Ticket {ticket_id} updated to '{status}'",
        }
