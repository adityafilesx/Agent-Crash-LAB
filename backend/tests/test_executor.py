import pytest
from app.sandbox.tool_executor import ToolExecutor

def test_tool_executor_safe_execution():
    state = {
        "customers": {
            "CUST-123": {
                "customer_id": "CUST-123",
                "name": "Test",
                "email": "test@test.com",
                "phone": "123",
                "status": "active",
                "tier": "gold",
                "orders": [],
                "created_at": "2023-01-01"
            }
        }
    }
    executor = ToolExecutor(state=state)
    result = executor.execute("get_customer", {"customer_id": "CUST-123"})
    assert result["success"] is True, str(result)
    assert "Test" in str(result["result"])

def test_tool_executor_destructive_action():
    state = {
        "orders": {
            "ORD-123": {
                "payment_status": "paid",
                "status": "shipped",
                "total": 100,
                "currency": "USD"
            }
        },
        "refunds": []
    }
    executor = ToolExecutor(state=state)
    result = executor.execute("process_refund", {"order_id": "ORD-123", "reason": "Test"})
    assert result["success"] is True, str(result)
    assert len(executor.state["refunds"]) == 1

def test_tool_executor_invalid_tool():
    executor = ToolExecutor(state={})
    result = executor.execute("invalid_tool", {})
    assert result["success"] is False
    assert "error" in result
