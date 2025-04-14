"""Shared type definitions for broker parsers."""

from dataclasses import dataclass, field
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
class BaseOperation:
    """Base class for all broker operations."""

    date: datetime
    operation_type: OperationType
    description: str
    amount: float
    broker: str = ""
    currency: str = "ARS"


@dataclass
class Trade:
    """Represents a trade operation."""

    date: datetime
    operation_type: OperationType
    description: str
    amount: float
    broker: str = ""
    currency: str = "ARS"
    symbol: str = ""
    quantity: float = 0.0
    price: float = 0.0
    total_amount: float = 0.0
    commission: Optional[float] = None
    taxes: Optional[float] = None


@dataclass
class MonetaryFlow:
    """Represents a monetary flow operation."""

    date: datetime
    operation_type: OperationType
    description: str
    amount: float
    broker: str = ""
    currency: str = "ARS"
    flow_type: str = "IN"  # "IN" or "OUT"
    reference: Optional[str] = None


@dataclass
class SecurityFlow:
    """Represents a security flow operation."""

    date: datetime
    operation_type: OperationType
    description: str
    amount: float
    broker: str = ""
    currency: str = "ARS"
    symbol: str = ""
    quantity: float = 0.0
    flow_type: str = "IN"  # "IN" or "OUT"


@dataclass
class MutualFund:
    """Represents a mutual fund operation."""

    date: datetime
    operation_type: OperationType
    description: str
    amount: float
    broker: str = ""
    currency: str = "ARS"
    fund_name: str = ""
    quantity: float = 0.0
    nav: float = 0.0
    total_amount: float = 0.0


BrokerOperation = Union[Trade, MonetaryFlow, SecurityFlow, MutualFund] 