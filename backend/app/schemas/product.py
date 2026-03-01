from __future__ import annotations

from typing import Optional, List

from pydantic import BaseModel


class ProductBase(BaseModel):
    name: str
    description: str
    category: str
    price: float


class ProductResponse(ProductBase):
    id: int
    stock_quantity: int
    specifications: Optional[dict] = None
    rating: float
    review_count: int
    image_url: Optional[str] = None

    class Config:
        from_attributes = True


class ProductSearchResult(BaseModel):
    id: int
    name: str
    category: str
    price: float
    rating: float
    review_count: int
    in_stock: bool


class ProductComparison(BaseModel):
    products: List[ProductResponse]
