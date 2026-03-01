from __future__ import annotations

"""Order service for retrieving order details and tracking information."""

import logging
import time

from sqlalchemy.orm import Session, joinedload

from app.db.models import Order, OrderItem, Product

logger = logging.getLogger(__name__)


def get_order_by_number(db: Session, order_number: str) -> dict | None:
    """Retrieve a full order by its order number, including line items with product names.

    Args:
        db: Database session.
        order_number: The unique order number string.

    Returns:
        Full order dict with nested items, or None if not found.
    """
    t0 = time.perf_counter()
    try:
        order = (
            db.query(Order)
            .options(joinedload(Order.items).joinedload(OrderItem.product))
            .filter(Order.order_number == order_number)
            .first()
        )
        elapsed_ms = (time.perf_counter() - t0) * 1000
        if order is None:
            logger.info(f"[PERF] get_order_by_number('{order_number}'): NOT FOUND in {elapsed_ms:.2f}ms")
            return None

        result = _order_to_dict(order)
        total_ms = (time.perf_counter() - t0) * 1000
        logger.info(
            f"[PERF] get_order_by_number('{order_number}'): "
            f"FOUND (status={order.status}, items={len(order.items)}) "
            f"query={elapsed_ms:.2f}ms, total={total_ms:.2f}ms"
        )
        return result
    except Exception:
        logger.exception(
            "Error retrieving order with order_number='%s'", order_number
        )
        return None


def get_orders_by_user(db: Session, user_id: int) -> list[dict]:
    """Retrieve all orders for a given user, each including line items.

    Args:
        db: Database session.
        user_id: The user's primary key.

    Returns:
        List of order dicts, each with nested items.
    """
    t0 = time.perf_counter()
    try:
        orders = (
            db.query(Order)
            .options(joinedload(Order.items).joinedload(OrderItem.product))
            .filter(Order.user_id == user_id)
            .order_by(Order.created_at.desc())
            .all()
        )
        elapsed_ms = (time.perf_counter() - t0) * 1000

        result = [_order_to_dict(o) for o in orders]
        total_ms = (time.perf_counter() - t0) * 1000
        logger.info(
            f"[PERF] get_orders_by_user(user_id={user_id}): "
            f"{len(orders)} orders, query={elapsed_ms:.2f}ms, total={total_ms:.2f}ms"
        )
        return result
    except Exception:
        logger.exception("Error retrieving orders for user_id=%d", user_id)
        return []


def get_order_status(db: Session, order_number: str) -> dict | None:
    """Retrieve the shipping and status information for an order.

    Args:
        db: Database session.
        order_number: The unique order number string.

    Returns:
        Dict with status and tracking details, or None if not found.
    """
    t0 = time.perf_counter()
    try:
        order = (
            db.query(Order)
            .filter(Order.order_number == order_number)
            .first()
        )
        elapsed_ms = (time.perf_counter() - t0) * 1000

        if order is None:
            logger.info(f"[PERF] get_order_status('{order_number}'): NOT FOUND in {elapsed_ms:.2f}ms")
            return None

        logger.info(
            f"[PERF] get_order_status('{order_number}'): "
            f"status={order.status} in {elapsed_ms:.2f}ms"
        )
        return {
            "order_number": order.order_number,
            "status": order.status,
            "tracking_number": order.tracking_number,
            "carrier": order.carrier,
            "estimated_delivery": (
                order.estimated_delivery.isoformat()
                if order.estimated_delivery
                else None
            ),
            "last_updated": (
                order.updated_at.isoformat() if order.updated_at else None
            ),
        }
    except Exception:
        logger.exception(
            "Error retrieving status for order_number='%s'", order_number
        )
        return None


def _order_to_dict(order: Order) -> dict:
    """Convert an Order ORM instance to a dictionary with nested items.

    Args:
        order: The Order model instance (with items eagerly loaded).

    Returns:
        Dictionary containing all order fields and a list of item dicts.
    """
    items = []
    for item in order.items:
        product_name = item.product.name if item.product else "Unknown Product"
        items.append(
            {
                "id": item.id,
                "product_id": item.product_id,
                "product_name": product_name,
                "quantity": item.quantity,
                "unit_price": item.unit_price,
                "subtotal": round(item.unit_price * item.quantity, 2),
            }
        )

    return {
        "id": order.id,
        "order_number": order.order_number,
        "user_id": order.user_id,
        "status": order.status,
        "total_amount": order.total_amount,
        "shipping_address": order.shipping_address,
        "tracking_number": order.tracking_number,
        "carrier": order.carrier,
        "estimated_delivery": (
            order.estimated_delivery.isoformat()
            if order.estimated_delivery
            else None
        ),
        "created_at": (
            order.created_at.isoformat() if order.created_at else None
        ),
        "updated_at": (
            order.updated_at.isoformat() if order.updated_at else None
        ),
        "items": items,
    }
