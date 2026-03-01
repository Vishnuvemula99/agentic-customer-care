from __future__ import annotations

"""Return policy enforcement engine — validates return eligibility and calculates refunds."""

import logging
from dataclasses import dataclass
from datetime import datetime, timedelta

from app.db.database import SessionLocal
from app.db.models import Order, OrderItem, Product, ReturnPolicy, User

logger = logging.getLogger(__name__)


@dataclass
class PolicyDecision:
    """Result of a return eligibility check."""
    allowed: bool
    reason: str
    policy_details: str
    restocking_fee_percent: float
    refund_amount: float
    refund_method: str
    return_window_days: int
    days_since_delivery: int


def check_eligibility(order_id: int, product_id: int, user_id: int) -> PolicyDecision:
    """Check if a product from an order is eligible for return.

    Enforces:
        - Order must exist and be in 'delivered' status
        - Delivery date must be within the category's return window
        - Product must not be in the exceptions list
        - VIP members get waived restocking fees
    """
    db = SessionLocal()
    try:
        order = db.query(Order).filter(Order.id == order_id).first()
        if not order:
            return PolicyDecision(
                allowed=False,
                reason="Order not found.",
                policy_details="",
                restocking_fee_percent=0,
                refund_amount=0,
                refund_method="",
                return_window_days=0,
                days_since_delivery=0,
            )

        if order.status != "delivered":
            return PolicyDecision(
                allowed=False,
                reason=f"Order status is '{order.status}'. Returns are only accepted for delivered orders.",
                policy_details="",
                restocking_fee_percent=0,
                refund_amount=0,
                refund_method="",
                return_window_days=0,
                days_since_delivery=0,
            )

        # Find the order item and product
        order_item = (
            db.query(OrderItem)
            .filter(OrderItem.order_id == order_id, OrderItem.product_id == product_id)
            .first()
        )
        if not order_item:
            return PolicyDecision(
                allowed=False,
                reason="This product was not found in the specified order.",
                policy_details="",
                restocking_fee_percent=0,
                refund_amount=0,
                refund_method="",
                return_window_days=0,
                days_since_delivery=0,
            )

        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            return PolicyDecision(
                allowed=False,
                reason="Product not found.",
                policy_details="",
                restocking_fee_percent=0,
                refund_amount=0,
                refund_method="",
                return_window_days=0,
                days_since_delivery=0,
            )

        # Get return policy for the product category
        policy = (
            db.query(ReturnPolicy)
            .filter(ReturnPolicy.category == product.category)
            .first()
        )
        if not policy:
            return PolicyDecision(
                allowed=False,
                reason=f"No return policy found for category '{product.category}'.",
                policy_details="",
                restocking_fee_percent=0,
                refund_amount=0,
                refund_method="",
                return_window_days=0,
                days_since_delivery=0,
            )

        # Check return window
        delivery_date = order.estimated_delivery or order.updated_at
        days_since = (datetime.utcnow() - delivery_date).days

        if days_since > policy.return_window_days:
            return PolicyDecision(
                allowed=False,
                reason=(
                    f"Return window has expired. The {product.category} return policy "
                    f"allows returns within {policy.return_window_days} days of delivery. "
                    f"Your order was delivered {days_since} days ago."
                ),
                policy_details=f"Category: {product.category}, Window: {policy.return_window_days} days",
                restocking_fee_percent=policy.restocking_fee_percent,
                refund_amount=0,
                refund_method=policy.refund_method,
                return_window_days=policy.return_window_days,
                days_since_delivery=days_since,
            )

        # Calculate refund
        item_total = order_item.unit_price * order_item.quantity

        # Check VIP status for fee waiver
        user = db.query(User).filter(User.id == user_id).first()
        fee_percent = policy.restocking_fee_percent
        if user and user.membership_tier == "vip":
            fee_percent = 0.0  # VIP members get waived restocking fees

        restocking_fee = item_total * (fee_percent / 100.0)
        refund_amount = round(item_total - restocking_fee, 2)

        fee_note = ""
        if fee_percent > 0:
            fee_note = f" A {fee_percent}% restocking fee (${restocking_fee:.2f}) applies."
        elif policy.restocking_fee_percent > 0 and user and user.membership_tier == "vip":
            fee_note = " Restocking fee waived for VIP members."

        conditions_str = ", ".join(policy.conditions_list) if policy.conditions_list else "Standard conditions"

        return PolicyDecision(
            allowed=True,
            reason=(
                f"This item is eligible for return.{fee_note} "
                f"Refund of ${refund_amount:.2f} to {policy.refund_method.replace('_', ' ')}. "
                f"Conditions: {conditions_str}."
            ),
            policy_details=f"Category: {product.category}, Window: {policy.return_window_days} days, Fee: {fee_percent}%",
            restocking_fee_percent=fee_percent,
            refund_amount=refund_amount,
            refund_method=policy.refund_method,
            return_window_days=policy.return_window_days,
            days_since_delivery=days_since,
        )

    finally:
        db.close()
