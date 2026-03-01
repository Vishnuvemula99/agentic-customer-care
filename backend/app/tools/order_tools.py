from __future__ import annotations

"""LangChain tools for order lookup, status tracking, and order history."""

from langchain_core.tools import tool

from app.db.database import SessionLocal
from app.services import order_service


@tool
def lookup_order(order_number: str) -> str:
    """Look up an order by its order number (e.g., ORD-2025-00001). Returns full order details including items, status, and shipping info. Use when customer asks about a specific order."""
    db = SessionLocal()
    try:
        order = order_service.get_order_by_number(db, order_number)
        if not order:
            return f"Order '{order_number}' not found. Please verify the order number and try again."

        lines = [
            f"Order: {order['order_number']}",
            f"Status: {order['status']}",
            f"Total: ${order['total_amount']:.2f}",
            f"Shipping Address: {order['shipping_address']}",
        ]

        if order.get("tracking_number"):
            lines.append(f"Tracking Number: {order['tracking_number']}")
        if order.get("carrier"):
            lines.append(f"Carrier: {order['carrier']}")
        if order.get("estimated_delivery"):
            lines.append(f"Estimated Delivery: {order['estimated_delivery']}")

        lines.append(f"Placed: {order['created_at']}")

        if order.get("items"):
            lines.append(f"\nItems ({len(order['items'])}):")
            for item in order["items"]:
                lines.append(
                    f"  - {item['product_name']} (Product ID: {item['product_id']}) "
                    f"| Qty: {item['quantity']} | Unit Price: ${item['unit_price']:.2f} "
                    f"| Subtotal: ${item['subtotal']:.2f}"
                )

        return "\n".join(lines)
    except Exception as e:
        return f"Error looking up order: {e}"
    finally:
        db.close()


@tool
def get_order_status(order_number: str) -> str:
    """Get the current shipping and tracking status of an order. Returns status, tracking number, carrier, and estimated delivery. Use when customer asks 'where is my order' or about delivery."""
    db = SessionLocal()
    try:
        status = order_service.get_order_status(db, order_number)
        if not status:
            return f"Order '{order_number}' not found. Please verify the order number and try again."

        lines = [
            f"Order: {status['order_number']}",
            f"Status: {status['status']}",
        ]

        if status.get("tracking_number"):
            lines.append(f"Tracking Number: {status['tracking_number']}")
        else:
            lines.append("Tracking Number: Not yet available")

        if status.get("carrier"):
            lines.append(f"Carrier: {status['carrier']}")

        if status.get("estimated_delivery"):
            lines.append(f"Estimated Delivery: {status['estimated_delivery']}")
        else:
            lines.append("Estimated Delivery: Not yet determined")

        if status.get("last_updated"):
            lines.append(f"Last Updated: {status['last_updated']}")

        return "\n".join(lines)
    except Exception as e:
        return f"Error retrieving order status: {e}"
    finally:
        db.close()


@tool
def get_user_orders(user_id: int) -> str:
    """Get all orders for a specific user by their user ID. Returns a summary list of all orders. Use when customer says 'show me my orders' or 'my recent orders' without specifying an order number."""
    db = SessionLocal()
    try:
        orders = order_service.get_orders_by_user(db, user_id)
        if not orders:
            return f"No orders found for user ID {user_id}."

        lines = [f"Found {len(orders)} order(s) for user {user_id}:\n"]
        for order in orders:
            item_count = len(order.get("items", []))
            lines.append(f"  - {order['order_number']} | Status: {order['status']} "
                         f"| Total: ${order['total_amount']:.2f} | Items: {item_count} "
                         f"| Placed: {order['created_at']}")
            for item in order.get("items", []):
                lines.append(
                    f"      {item['product_name']} | Qty: {item['quantity']} "
                    f"| ${item['unit_price']:.2f} each"
                )
        return "\n".join(lines)
    except Exception as e:
        return f"Error retrieving orders: {e}"
    finally:
        db.close()
