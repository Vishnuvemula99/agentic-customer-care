from __future__ import annotations

from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel


class ReturnPolicyResponse(BaseModel):
    id: int
    category: str
    return_window_days: int
    conditions: List[str]
    restocking_fee_percent: float
    refund_method: str
    exceptions: List[str]

    class Config:
        from_attributes = True


class ReturnEligibilityCheck(BaseModel):
    eligible: bool
    reason: str
    policy: Optional[ReturnPolicyResponse] = None
    estimated_refund: Optional[float] = None
    restocking_fee: Optional[float] = None
    days_remaining: Optional[int] = None


class ReturnRequestCreate(BaseModel):
    order_id: int
    product_id: int
    reason: str


class ReturnRequestResponse(BaseModel):
    id: int
    order_id: int
    user_id: int
    product_id: Optional[int] = None
    reason: str
    status: str
    refund_amount: Optional[float] = None
    created_at: datetime

    class Config:
        from_attributes = True
