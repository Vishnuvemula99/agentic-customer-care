from __future__ import annotations

"""Product service for searching, retrieving, and comparing products."""

import json
import logging

from sqlalchemy.orm import Session

from app.db.models import Product

logger = logging.getLogger(__name__)


def search_products(
    db: Session,
    query: str,
    category: str | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
) -> list[dict]:
    """Search products by keyword in name and description with optional filters.

    Args:
        db: Database session.
        query: Search keyword to match against product name and description.
        category: Optional category filter.
        min_price: Optional minimum price filter (inclusive).
        max_price: Optional maximum price filter (inclusive).

    Returns:
        List of product summary dicts.
    """
    try:
        search_pattern = f"%{query}%"
        filters = (
            Product.name.ilike(search_pattern)
            | Product.description.ilike(search_pattern)
        )

        stmt = db.query(Product).filter(filters)

        if category is not None:
            stmt = stmt.filter(Product.category == category)
        if min_price is not None:
            stmt = stmt.filter(Product.price >= min_price)
        if max_price is not None:
            stmt = stmt.filter(Product.price <= max_price)

        products = stmt.all()

        return [
            {
                "id": p.id,
                "name": p.name,
                "category": p.category,
                "price": p.price,
                "rating": p.rating,
                "review_count": p.review_count,
                "in_stock": p.stock_quantity > 0,
            }
            for p in products
        ]
    except Exception:
        logger.exception("Error searching products with query='%s'", query)
        return []


def get_product_by_id(db: Session, product_id: int) -> dict | None:
    """Retrieve full product details by ID, including parsed specifications.

    Args:
        db: Database session.
        product_id: The product's primary key.

    Returns:
        Full product dict or None if not found.
    """
    try:
        product = db.query(Product).filter(Product.id == product_id).first()
        if product is None:
            return None

        return _product_to_full_dict(product)
    except Exception:
        logger.exception("Error retrieving product id=%d", product_id)
        return None


def compare_products(db: Session, product_ids: list[int]) -> list[dict]:
    """Retrieve full product details for a list of product IDs for comparison.

    Args:
        db: Database session.
        product_ids: List of product primary keys to compare.

    Returns:
        List of full product dicts for the requested IDs.
    """
    try:
        if not product_ids:
            return []

        products = db.query(Product).filter(Product.id.in_(product_ids)).all()

        return [_product_to_full_dict(p) for p in products]
    except Exception:
        logger.exception("Error comparing products ids=%s", product_ids)
        return []


def get_products_by_category(db: Session, category: str) -> list[dict]:
    """Retrieve all products belonging to a specific category.

    Args:
        db: Database session.
        category: The category name to filter by.

    Returns:
        List of full product dicts in the given category.
    """
    try:
        products = db.query(Product).filter(Product.category == category).all()

        return [_product_to_full_dict(p) for p in products]
    except Exception:
        logger.exception("Error retrieving products for category='%s'", category)
        return []


def _product_to_full_dict(product: Product) -> dict:
    """Convert a Product ORM instance to a full detail dictionary.

    Args:
        product: The Product model instance.

    Returns:
        Dictionary containing all product fields with parsed specifications.
    """
    specifications = {}
    if product.specifications:
        try:
            specifications = json.loads(product.specifications)
        except (json.JSONDecodeError, TypeError):
            logger.warning(
                "Invalid JSON in specifications for product id=%d", product.id
            )

    return {
        "id": product.id,
        "name": product.name,
        "description": product.description,
        "category": product.category,
        "price": product.price,
        "stock_quantity": product.stock_quantity,
        "in_stock": product.stock_quantity > 0,
        "specifications": specifications,
        "image_url": product.image_url,
        "rating": product.rating,
        "review_count": product.review_count,
    }
