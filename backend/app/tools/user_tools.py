from __future__ import annotations

"""LangChain tools for user profile lookup and identification."""

from langchain_core.tools import tool

from app.db.database import SessionLocal
from app.services import user_service


@tool
def get_user_profile(user_id: int) -> str:
    """Get user profile information by user ID. Returns the user's name, email, phone, address, and membership tier. Use when you need to look up or verify customer account details."""
    db = SessionLocal()
    try:
        user = user_service.get_user_by_id(db, user_id)
        if not user:
            return f"User with ID {user_id} not found."

        lines = [
            f"User Profile (ID: {user['id']})",
            f"Name: {user['name']}",
            f"Email: {user['email']}",
            f"Phone: {user.get('phone') or 'Not provided'}",
            f"Membership Tier: {user.get('membership_tier', 'standard')}",
            f"Member Since: {user.get('created_at', 'N/A')}",
        ]

        address = user.get("address")
        if address and isinstance(address, dict):
            lines.append("Address:")
            if address.get("street"):
                lines.append(f"  {address['street']}")
            city_state_zip = ", ".join(
                filter(
                    None,
                    [
                        address.get("city"),
                        address.get("state"),
                        address.get("zip"),
                    ],
                )
            )
            if city_state_zip:
                lines.append(f"  {city_state_zip}")
            if address.get("country"):
                lines.append(f"  {address['country']}")
        elif address and isinstance(address, str):
            lines.append(f"Address: {address}")
        else:
            lines.append("Address: Not provided")

        return "\n".join(lines)
    except Exception as e:
        return f"Error retrieving user profile: {e}"
    finally:
        db.close()


@tool
def lookup_user_by_email(email: str) -> str:
    """Find a user by their email address. Returns user ID, name, email, and membership tier. Use when a customer provides their email to identify their account."""
    db = SessionLocal()
    try:
        user = user_service.get_user_by_email(db, email)
        if not user:
            return f"No user found with email '{email}'."

        lines = [
            f"User Found:",
            f"User ID: {user['id']}",
            f"Name: {user['name']}",
            f"Email: {user['email']}",
            f"Membership Tier: {user.get('membership_tier', 'standard')}",
        ]
        return "\n".join(lines)
    except Exception as e:
        return f"Error looking up user by email: {e}"
    finally:
        db.close()
