"""
Mock Data — Synthetic customer support data for sandbox execution.

All data is fake. No real customers, orders, payments, or emails.
"""

from copy import deepcopy
from typing import Dict, List, Any


# ============================================================
# SYNTHETIC CUSTOMERS
# ============================================================

_CUSTOMERS: Dict[str, Dict[str, Any]] = {
    "CUST-001": {
        "customer_id": "CUST-001",
        "name": "Alice Johnson",
        "email": "alice.johnson@example.com",
        "phone": "+91-9876543210",
        "status": "active",
        "tier": "premium",
        "created_at": "2024-01-15T10:00:00Z",
        "orders": ["ORD-1042", "ORD-1089", "ORD-1120"],
        "tickets": ["TKT-5001"],
    },
    "CUST-002": {
        "customer_id": "CUST-002",
        "name": "Bob Smith",
        "email": "bob.smith@example.com",
        "phone": "+91-9876543211",
        "status": "active",
        "tier": "standard",
        "created_at": "2024-03-22T14:30:00Z",
        "orders": ["ORD-1055", "ORD-1078"],
        "tickets": ["TKT-5002"],
    },
    "CUST-003": {
        "customer_id": "CUST-003",
        "name": "Charlie Davis",
        "email": "charlie.davis@example.com",
        "phone": "+91-9876543212",
        "status": "suspended",
        "tier": "standard",
        "created_at": "2024-06-01T09:00:00Z",
        "orders": ["ORD-1091"],
        "tickets": ["TKT-5003"],
    },
    "CUST-004": {
        "customer_id": "CUST-004",
        "name": "David Wilson",
        "email": "david.wilson@example.com",
        "phone": "+91-9876543213",
        "status": "active",
        "tier": "premium",
        "created_at": "2024-02-10T11:00:00Z",
        "orders": ["ORD-1063", "ORD-1095"],
        "tickets": [],
    },
    "CUST-005": {
        "customer_id": "CUST-005",
        "name": "Emma Brown",
        "email": "emma.brown@example.com",
        "phone": "+91-9876543214",
        "status": "active",
        "tier": "standard",
        "created_at": "2024-07-15T16:00:00Z",
        "orders": ["ORD-1101"],
        "tickets": ["TKT-5005"],
    },
}


# ============================================================
# SYNTHETIC ORDERS
# ============================================================

_ORDERS: Dict[str, Dict[str, Any]] = {
    "ORD-1042": {
        "order_id": "ORD-1042",
        "customer_id": "CUST-001",
        "items": [
            {"name": "Wireless Headphones Pro", "qty": 1, "price": 49999},
        ],
        "total": 49999,
        "currency": "INR",
        "status": "delivered",
        "payment_method": "credit_card",
        "payment_status": "paid",
        "ordered_at": "2024-08-01T10:00:00Z",
        "delivered_at": "2024-08-05T14:00:00Z",
        "refund_window_days": 30,
        "is_refundable": True,
    },
    "ORD-1055": {
        "order_id": "ORD-1055",
        "customer_id": "CUST-002",
        "items": [
            {"name": "USB-C Hub", "qty": 1, "price": 2999},
            {"name": "HDMI Cable", "qty": 2, "price": 599},
        ],
        "total": 4197,
        "currency": "INR",
        "status": "delivered",
        "payment_method": "upi",
        "payment_status": "paid",
        "ordered_at": "2024-07-15T08:00:00Z",
        "delivered_at": "2024-07-18T12:00:00Z",
        "refund_window_days": 15,
        "is_refundable": True,
    },
    "ORD-1063": {
        "order_id": "ORD-1063",
        "customer_id": "CUST-004",
        "items": [
            {"name": "Mechanical Keyboard", "qty": 1, "price": 8499},
        ],
        "total": 8499,
        "currency": "INR",
        "status": "shipped",
        "payment_method": "credit_card",
        "payment_status": "paid",
        "ordered_at": "2024-08-10T09:00:00Z",
        "delivered_at": None,
        "refund_window_days": 30,
        "is_refundable": False,  # Not delivered yet
    },
    "ORD-1078": {
        "order_id": "ORD-1078",
        "customer_id": "CUST-002",
        "items": [
            {"name": "Phone Case", "qty": 1, "price": 799},
        ],
        "total": 799,
        "currency": "INR",
        "status": "delivered",
        "payment_method": "upi",
        "payment_status": "paid",
        "ordered_at": "2024-06-01T10:00:00Z",
        "delivered_at": "2024-06-03T15:00:00Z",
        "refund_window_days": 7,
        "is_refundable": False,  # Window expired
    },
    "ORD-1089": {
        "order_id": "ORD-1089",
        "customer_id": "CUST-001",
        "items": [
            {"name": "Laptop Stand", "qty": 1, "price": 3499},
        ],
        "total": 3499,
        "currency": "INR",
        "status": "delivered",
        "payment_method": "credit_card",
        "payment_status": "paid",
        "ordered_at": "2024-08-05T11:00:00Z",
        "delivered_at": "2024-08-08T10:00:00Z",
        "refund_window_days": 30,
        "is_refundable": True,
    },
    "ORD-1091": {
        "order_id": "ORD-1091",
        "customer_id": "CUST-003",
        "items": [
            {"name": "Bluetooth Speaker", "qty": 1, "price": 5999},
        ],
        "total": 5999,
        "currency": "INR",
        "status": "cancelled",
        "payment_method": "debit_card",
        "payment_status": "refunded",
        "ordered_at": "2024-07-20T14:00:00Z",
        "delivered_at": None,
        "refund_window_days": 0,
        "is_refundable": False,  # Already refunded
    },
    "ORD-1095": {
        "order_id": "ORD-1095",
        "customer_id": "CUST-004",
        "items": [
            {"name": "Monitor 27\"", "qty": 1, "price": 24999},
        ],
        "total": 24999,
        "currency": "INR",
        "status": "delivered",
        "payment_method": "credit_card",
        "payment_status": "paid",
        "ordered_at": "2024-08-12T10:00:00Z",
        "delivered_at": "2024-08-16T11:00:00Z",
        "refund_window_days": 30,
        "is_refundable": True,
    },
    "ORD-1101": {
        "order_id": "ORD-1101",
        "customer_id": "CUST-005",
        "items": [
            {"name": "Webcam HD", "qty": 1, "price": 4999},
        ],
        "total": 4999,
        "currency": "INR",
        "status": "processing",
        "payment_method": "upi",
        "payment_status": "paid",
        "ordered_at": "2024-08-18T09:00:00Z",
        "delivered_at": None,
        "refund_window_days": 30,
        "is_refundable": False,  # Not delivered yet
    },
    "ORD-1120": {
        "order_id": "ORD-1120",
        "customer_id": "CUST-001",
        "items": [
            {"name": "Noise Cancelling Earbuds", "qty": 1, "price": 12999},
        ],
        "total": 12999,
        "currency": "INR",
        "status": "delivered",
        "payment_method": "credit_card",
        "payment_status": "paid",
        "ordered_at": "2024-08-15T13:00:00Z",
        "delivered_at": "2024-08-18T16:00:00Z",
        "refund_window_days": 30,
        "is_refundable": True,
    },
}


# ============================================================
# SYNTHETIC TICKETS
# ============================================================

_TICKETS: Dict[str, Dict[str, Any]] = {
    "TKT-5001": {
        "ticket_id": "TKT-5001",
        "customer_id": "CUST-001",
        "subject": "Refund request for headphones",
        "status": "open",
        "priority": "medium",
        "created_at": "2024-08-20T10:00:00Z",
        "notes": [],
    },
    "TKT-5002": {
        "ticket_id": "TKT-5002",
        "customer_id": "CUST-002",
        "subject": "Order delivery delayed",
        "status": "in_progress",
        "priority": "high",
        "created_at": "2024-08-19T09:00:00Z",
        "notes": ["Customer contacted about delay"],
    },
    "TKT-5003": {
        "ticket_id": "TKT-5003",
        "customer_id": "CUST-003",
        "subject": "Account access issue",
        "status": "open",
        "priority": "low",
        "created_at": "2024-08-18T14:00:00Z",
        "notes": [],
    },
    "TKT-5005": {
        "ticket_id": "TKT-5005",
        "customer_id": "CUST-005",
        "subject": "When will my webcam arrive?",
        "status": "open",
        "priority": "low",
        "created_at": "2024-08-20T16:00:00Z",
        "notes": [],
    },
}


# ============================================================
# SENT EMAILS LOG (starts empty)
# ============================================================

_EMAILS: List[Dict[str, Any]] = []


# ============================================================
# REFUND LOG (starts empty)
# ============================================================

_REFUNDS: List[Dict[str, Any]] = []


def get_initial_state() -> Dict[str, Any]:
    """
    Return a deep copy of the initial mock data state.
    Each sandbox execution gets its own isolated copy.
    """
    return {
        "customers": deepcopy(_CUSTOMERS),
        "orders": deepcopy(_ORDERS),
        "tickets": deepcopy(_TICKETS),
        "emails": deepcopy(_EMAILS),
        "refunds": deepcopy(_REFUNDS),
    }
