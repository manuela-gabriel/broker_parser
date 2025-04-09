"""Shared type definitions for broker parsers."""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional, Union


class OperationType(str, Enum):
    """Types of operations that can be performed."""

    TRADE = "TRADE"
    MONETARY_FLOW = "MONETARY_FLOW"
    SECURITY_FLOW = "SECURITY_FLOW"
    MUTUAL_FUND = "MUTUAL_FUND"


@dataclass
class Operation:
    """Base class for all broker operations."""

    date: datetime
    operation_type: OperationType
    description: str
    amount: float
    currency: str = "ARS"
    broker: str = ""


@dataclass
class Trade(Operation):
    """Represents a trade operation."""

    symbol: str
    quantity: float
    price: float
    total_amount: float
    commission: Optional[float] = None
    taxes: Optional[float] = None


@dataclass
class MonetaryFlow(Operation):
    """Represents a monetary flow operation."""

    flow_type: str  # "IN" or "OUT"
    reference: Optional[str] = None


@dataclass
class SecurityFlow(Operation):
    """Represents a security flow operation."""

    symbol: str
    quantity: float
    flow_type: str  # "IN" or "OUT"


@dataclass
class MutualFund(Operation):
    """Represents a mutual fund operation."""

    fund_name: str
    quantity: float
    nav: float
    total_amount: float


BrokerOperation = Union[Trade, MonetaryFlow, SecurityFlow, MutualFund] 