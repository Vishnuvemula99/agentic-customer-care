from __future__ import annotations

"""Returns service for eligibility checks, return request creation, and status tracking."""

import json
import logging
from datetime import datetime, timedelta

from sqlalchemy.orm import Session, joinedload

from app.db.models import Order, OrderItem, Product, ReturnPolicy, ReturnRequest

logger = logging.getLogger(__name__)


def check_return_eligibility(
    db: Session, order_number: str, product_id: int
) -> dict:
    """Check whether a product from a specific order is eligible for return.

    Validates that the order exists, is delivered, the product is part of the order,
    a return policy exists for the product's category, and the return window has not
    expired.

    Args:
        db: Database session.
        order_number: The unique order number string.
        product_id: The product's primary key.

    Returns:
        Dict describing eligibility status, reason, policy details, and estimated refund.
    """
    try:
        # Look up the order with its items
        order = (
            db.query(Order)
            .options(joinedload(Order.items))
            .filter(Order.order_number == order_number)
            .first()
        )
        if order is None:
            return {
                "eligible": False,
                "reason": f"Order '{order_number}' not found.",
            }

        if order.status != "delivered":
            return {
                "eligible": False,
                "reason": (
                    f"Order is currently '{order.status}'. "
                    "Returns are only accepted for delivered orders."
                ),
            }

        # Find the specific order item for the product
        order_item = next(
            (item for item in order.items if item.product_id == product_id),
            None,
        )
        if order_item is None:
            return {
                "eligible": False,
                "reason": (
                    f"Product ID {product_id} is not part of order '{order_number}'."
                ),
            }

        # Get the product and its category
        product = db.query(Product).filter(Product.id == product_id).first()
        if product is None:
            return {
                "eligible": False,
                "reason": f"Product ID {product_id} not found in catalog.",
            }

        # Look up the return policy for the product's category
        policy = (
            db.query(ReturnPolicy)
            .filter(ReturnPolicy.category == product.category)
            .first()
        )
        if policy is None:
            return {
                "eligible": False,
                "reason": (
                    f"No return policy found for category '{product.category}'."
                ),
            }

        # Use order.updated_at as the delivery date for delivered orders
        delivery_date = order.updated_at
        if delivery_date is None:
            return {
                "eligible": False,
                "reason": "Unable to determine delivery date for this order.",
            }

        # Calculate remaining return window
        return_deadline = delivery_date + timedelta(days=policy.return_window_days)
        now = datetime.utcnow()
        days_remaining = (return_deadline - now).days

        if days_remaining < 0:
            return {
                "eligible": False,
                "reason": (
                    f"Return window of {policy.return_window_days} days has expired. "
                    f"The deadline was {return_deadline.strftime('%Y-%m-%d')}."
                ),
                "policy": _policy_to_dict(policy),
                "days_remaining": 0,
            }

        # Calculate estimated refund
        item_total = order_item.unit_price * order_item.quantity
        restocking_fee = round(
            (policy.restocking_fee_percent / 100) * item_total, 2
        )
        estimated_refund = round(item_total - restocking_fee, 2)

        return {
            "eligible": True,
            "reason": "Product is eligible for return.",
            "policy": _policy_to_dict(policy),
            "estimated_refund": estimated_refund,
            "restocking_fee": restocking_fee,
            "days_remaining": days_remaining,
            "return_deadline": return_deadline.isoformat(),
            "item_total": item_total,
        }
    except Exception:
        logger.exception(
            "Error checking return eligibility for order='%s', product_id=%d",
            order_number,
            product_id,
        )
        return {
            "eligible": False,
            "reason": "An internal error occurred while checking return eligibility.",
        }


def create_return_request(
    db: Session,
    order_number: str,
    product_id: int,
    user_id: int,
    reason: str,
) -> dict:
    """Create a return request after verifying eligibility.

    Args:
        db: Database session.
        order_number: The unique order number string.
        product_id: The product's primary key.
        user_id: The requesting user's primary key.
        reason: The customer's reason for the return.

    Returns:
        Dict with the created return request details, or an error dict if ineligible.
    """
    try:
        # Verify eligibility first
        eligibility = check_return_eligibility(db, order_number, product_id)
        if not eligibility.get("eligible"):
            return {
                "success": False,
                "error": eligibility.get(
                    "reason", "Product is not eligible for return."
                ),
            }

        # Retrieve the order to get its ID
        order = (
            db.query(Order)
            .filter(Order.order_number == order_number)
            .first()
        )
        if order is None:
            return {
                "success": False,
                "error": f"Order '{order_number}' not found.",
            }

        # Create the return request record
        return_request = ReturnRequest(
            order_id=order.id,
            user_id=user_id,
            product_id=product_id,
            reason=reason,
            status="requested",
            refund_amount=eligibility.get("estimated_refund"),
        )
        db.add(return_request)
        db.commit()
        db.refresh(return_request)

        return {
            "success": True,
            "return_request": {
                "id": return_request.id,
                "order_id": return_request.order_id,
                "order_number": order_number,
                "user_id": return_request.user_id,
                "product_id": return_request.product_id,
                "reason": return_request.reason,
                "status": return_request.status,
                "refund_amount": return_request.refund_amount,
                "created_at": (
                    return_request.created_at.isoformat()
                    if return_request.created_at
                    else None
                ),
            },
        }
    except Exception:
        db.rollback()
        logger.exception(
            "Error creating return request for order='%s', product_id=%d, user_id=%d",
            order_number,
            product_id,
            user_id,
        )
        return {
            "success": False,
            "error": "An internal error occurred while creating the return request.",
        }


def get_return_status(db: Session, return_id: int) -> dict | None:
    """Retrieve the current status and details of a return request.

    Args:
        db: Database session.
        return_id: The return request's primary key.

    Returns:
        Dict with return request details, or None if not found.
    """
    try:
        return_request = (
            db.query(ReturnRequest)
            .filter(ReturnRequest.id == return_id)
            .first()
        )
        if return_request is None:
            return None

        # Fetch the associated order number for convenience
        order = (
            db.query(Order).filter(Order.id == return_request.order_id).first()
        )
        order_number = order.order_number if order else None

        return {
            "id": return_request.id,
            "order_id": return_request.order_id,
            "order_number": order_number,
            "user_id": return_request.user_id,
            "product_id": return_request.product_id,
            "reason": return_request.reason,
            "status": return_request.status,
            "refund_amount": return_request.refund_amount,
            "created_at": (
                return_request.created_at.isoformat()
                if return_request.created_at
                else None
            ),
        }
    except Exception:
        logger.exception(
            "Error retrieving return request id=%d", return_id
        )
        return None


def _policy_to_dict(policy: ReturnPolicy) -> dict:
    """Convert a ReturnPolicy ORM instance to a dictionary.

    Args:
        policy: The ReturnPolicy model instance.

    Returns:
        Dictionary containing all policy fields with parsed JSON fields.
    """
    conditions = []
    if policy.conditions:
        try:
            conditions = json.loads(policy.conditions)
        except (json.JSONDecodeError, TypeError):
            logger.warning(
                "Invalid JSON in conditions for policy id=%d", policy.id
            )

    exceptions = []
    if policy.exceptions:
        try:
            exceptions = json.loads(policy.exceptions)
        except (json.JSONDecodeError, TypeError):
            logger.warning(
                "Invalid JSON in exceptions for policy id=%d", policy.id
            )

    return {
        "id": policy.id,
        "category": policy.category,
        "return_window_days": policy.return_window_days,
        "conditions": conditions,
        "restocking_fee_percent": policy.restocking_fee_percent,
        "refund_method": policy.refund_method,
        "exceptions": exceptions,
    }
