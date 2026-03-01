from __future__ import annotations

"""User service for retrieving user account information."""

import json
import logging

from sqlalchemy.orm import Session

from app.db.models import User

logger = logging.getLogger(__name__)


def get_user_by_id(db: Session, user_id: int) -> dict | None:
    """Retrieve a user by their primary key.

    Args:
        db: Database session.
        user_id: The user's primary key.

    Returns:
        User dict or None if not found.
    """
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if user is None:
            return None

        return _user_to_dict(user)
    except Exception:
        logger.exception("Error retrieving user id=%d", user_id)
        return None


def get_user_by_email(db: Session, email: str) -> dict | None:
    """Retrieve a user by their email address.

    Args:
        db: Database session.
        email: The user's email address.

    Returns:
        User dict or None if not found.
    """
    try:
        user = db.query(User).filter(User.email == email).first()
        if user is None:
            return None

        return _user_to_dict(user)
    except Exception:
        logger.exception("Error retrieving user with email='%s'", email)
        return None


def _user_to_dict(user: User) -> dict:
    """Convert a User ORM instance to a dictionary.

    Args:
        user: The User model instance.

    Returns:
        Dictionary containing all user fields with parsed address JSON.
    """
    address = {}
    if user.address:
        try:
            address = json.loads(user.address)
        except (json.JSONDecodeError, TypeError):
            logger.warning(
                "Invalid JSON in address for user id=%d", user.id
            )

    return {
        "id": user.id,
        "email": user.email,
        "name": user.name,
        "phone": user.phone,
        "address": address,
        "membership_tier": user.membership_tier,
        "created_at": (
            user.created_at.isoformat() if user.created_at else None
        ),
    }
