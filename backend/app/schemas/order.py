from __future__ import annotations

from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel


class OrderItemResponse(BaseModel):
    id: int
    product_id: int
    product_name: str
    quantity: int
    unit_price: float

    class Config:
        from_attributes = True


class OrderResponse(BaseModel):
    id: int
    order_number: str
    user_id: int
    status: str
    total_amount: float
    shipping_address: Optional[str] = None
    tracking_number: Optional[str] = None
    carrier: Optional[str] = None
    estimated_delivery: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    items: List[OrderItemResponse] = []

    class Config:
        from_attributes = True


class OrderStatusResponse(BaseModel):
    order_number: str
    status: str
    tracking_number: Optional[str] = None
    carrier: Optional[str] = None
    estimated_delivery: Optional[datetime] = None
    last_updated: datetime


class ShippingUpdate(BaseModel):
    order_number: str
    status: str
    location: Optional[str] = None
    estimated_delivery: Optional[datetime] = None
