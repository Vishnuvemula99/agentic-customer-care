from __future__ import annotations

"""LangChain tools for return eligibility checks and return request creation."""

from langchain_core.tools import tool

from app.db.database import SessionLocal
from app.services import returns_service


@tool
def check_return_eligibility(order_number: str, product_id: int) -> str:
    """Check if a product from a specific order is eligible for return. Returns eligibility status, return window remaining, restocking fee info, and estimated refund amount. ALWAYS use this tool before telling a customer whether they can return an item."""
    db = SessionLocal()
    try:
        result = returns_service.check_return_eligibility(
            db, order_number, product_id
        )

        if not result.get("eligible"):
            lines = [
                "Return Eligibility: NOT ELIGIBLE",
                f"Reason: {result.get('reason', 'Unknown reason')}",
            ]
            if result.get("policy"):
                policy = result["policy"]
                lines.append(
                    f"Policy: {policy['return_window_days']}-day return window "
                    f"for {policy['category']} items"
                )
            return "\n".join(lines)

        policy = result.get("policy", {})
        lines = [
            "Return Eligibility: ELIGIBLE",
            f"Reason: {result.get('reason')}",
            f"Days Remaining in Return Window: {result.get('days_remaining')}",
            f"Return Deadline: {result.get('return_deadline')}",
            f"Item Total: ${result.get('item_total', 0):.2f}",
            f"Restocking Fee: ${result.get('restocking_fee', 0):.2f} "
            f"({policy.get('restocking_fee_percent', 0)}%)",
            f"Estimated Refund: ${result.get('estimated_refund', 0):.2f}",
            f"Refund Method: {policy.get('refund_method', 'N/A')}",
        ]

        if policy.get("conditions"):
            lines.append("Conditions:")
            for condition in policy["conditions"]:
                lines.append(f"  - {condition}")

        if policy.get("exceptions"):
            lines.append("Exceptions:")
            for exception in policy["exceptions"]:
                lines.append(f"  - {exception}")

        return "\n".join(lines)
    except Exception as e:
        return f"Error checking return eligibility: {e}"
    finally:
        db.close()


@tool
def initiate_return(
    order_number: str,
    product_id: int,
    user_id: int,
    reason: str,
) -> str:
    """Initiate a return request for a product. Only call this AFTER confirming eligibility with check_return_eligibility AND getting the customer's reason for the return. Returns the created return request details."""
    db = SessionLocal()
    try:
        result = returns_service.create_return_request(
            db, order_number, product_id, user_id, reason
        )

        if not result.get("success"):
            return (
                f"Return request could not be created. "
                f"Reason: {result.get('error', 'Unknown error')}"
            )

        rr = result["return_request"]
        lines = [
            "Return request created successfully!",
            f"Return ID: {rr['id']}",
            f"Order: {rr['order_number']}",
            f"Product ID: {rr['product_id']}",
            f"Status: {rr['status']}",
            f"Reason: {rr['reason']}",
            f"Refund Amount: ${rr['refund_amount']:.2f}",
            f"Created At: {rr['created_at']}",
        ]
        return "\n".join(lines)
    except Exception as e:
        return f"Error initiating return: {e}"
    finally:
        db.close()
