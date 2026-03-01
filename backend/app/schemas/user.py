from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class UserBase(BaseModel):
    email: str
    name: str
    phone: Optional[str] = None
    membership_tier: str = "standard"


class UserResponse(UserBase):
    id: int
    address: Optional[dict] = None
    created_at: datetime

    class Config:
        from_attributes = True


class UserBrief(BaseModel):
    id: int
    name: str
    email: str
    membership_tier: str

    class Config:
        from_attributes = True
