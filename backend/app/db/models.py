import json
from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.db.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    phone = Column(String, nullable=True)
    address = Column(Text, nullable=True)  # JSON string
    membership_tier = Column(String, default="standard")  # standard, premium, vip
    created_at = Column(DateTime, default=datetime.utcnow)

    orders = relationship("Order", back_populates="user")
    return_requests = relationship("ReturnRequest", back_populates="user")

    @property
    def address_dict(self) -> dict:
        return json.loads(self.address) if self.address else {}


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    description = Column(Text, nullable=False)
    category = Column(String, nullable=False, index=True)
    price = Column(Float, nullable=False)
    stock_quantity = Column(Integer, default=0)
    specifications = Column(Text, nullable=True)  # JSON string
    image_url = Column(String, nullable=True)
    rating = Column(Float, default=0.0)
    review_count = Column(Integer, default=0)

    order_items = relationship("OrderItem", back_populates="product")

    @property
    def specs_dict(self) -> dict:
        return json.loads(self.specifications) if self.specifications else {}


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    order_number = Column(String, unique=True, index=True, nullable=False)
    status = Column(String, default="pending")  # pending, confirmed, shipped, in_transit, delivered, cancelled
    total_amount = Column(Float, nullable=False)
    shipping_address = Column(Text, nullable=True)
    tracking_number = Column(String, nullable=True)
    carrier = Column(String, nullable=True)  # UPS, FedEx, USPS
    estimated_delivery = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="orders")
    items = relationship("OrderItem", back_populates="order")
    return_requests = relationship("ReturnRequest", back_populates="order")


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)

    order = relationship("Order", back_populates="items")
    product = relationship("Product", back_populates="order_items")


class ReturnPolicy(Base):
    __tablename__ = "return_policies"

    id = Column(Integer, primary_key=True, index=True)
    category = Column(String, unique=True, nullable=False)
    return_window_days = Column(Integer, nullable=False)
    conditions = Column(Text, nullable=True)  # JSON string
    restocking_fee_percent = Column(Float, default=0.0)
    refund_method = Column(String, default="original_payment")  # original_payment, store_credit
    exceptions = Column(Text, nullable=True)  # JSON string

    @property
    def conditions_list(self) -> list:
        return json.loads(self.conditions) if self.conditions else []

    @property
    def exceptions_list(self) -> list:
        return json.loads(self.exceptions) if self.exceptions else []


class ReturnRequest(Base):
    __tablename__ = "return_requests"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=True)
    reason = Column(String, nullable=False)
    status = Column(String, default="requested")  # requested, approved, denied, completed
    refund_amount = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    order = relationship("Order", back_populates="return_requests")
    user = relationship("User", back_populates="return_requests")
