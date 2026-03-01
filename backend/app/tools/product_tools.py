from __future__ import annotations

"""LangChain tools for product search, details, and comparison."""

from langchain_core.tools import tool

from app.db.database import SessionLocal
from app.services import product_service


@tool
def search_products(
    query: str,
    category: str = "",
    min_price: float = 0,
    max_price: float = 0,
) -> str:
    """Search for products in the catalog by keyword. Optionally filter by category (electronics, clothing, home_kitchen, sports, books) and price range.

    Use this tool when a customer asks about products, what's available, or wants recommendations.
    Returns a list of matching products with name, price, category, and rating.
    """
    db = SessionLocal()
    try:
        cat = category if category else None
        mn = min_price if min_price > 0 else None
        mx = max_price if max_price > 0 else None
        results = product_service.search_products(db, query, cat, mn, mx)
        if not results:
            msg = f"No products found matching '{query}'."
            if category:
                msg += f" in category '{category}'"
            return msg

        lines = [f"Found {len(results)} product(s):"]
        for p in results:
            stock = "In Stock" if p.get("in_stock") else "Out of Stock"
            lines.append(
                f"  - [{p['id']}] {p['name']} | ${p['price']:.2f} "
                f"| {p['category']} | Rating: {p['rating']}/5 "
                f"({p['review_count']} reviews) | {stock}"
            )
        return "\n".join(lines)
    except Exception as e:
        return f"Error searching products: {e}"
    finally:
        db.close()


@tool
def get_product_details(product_id: int) -> str:
    """Get detailed information about a specific product by its ID.

    Use this when a customer wants to know more about a specific product including full description, specifications, and availability.
    """
    db = SessionLocal()
    try:
        product = product_service.get_product_by_id(db, product_id)
        if not product:
            return f"Product with ID {product_id} not found."

        lines = [
            f"Product: {product['name']}",
            f"Category: {product['category']}",
            f"Price: ${product['price']:.2f}",
            f"Rating: {product['rating']}/5 ({product['review_count']} reviews)",
            f"Stock: {product['stock_quantity']} units available",
            f"Description: {product['description']}",
        ]
        if product.get("specifications"):
            lines.append("Specifications:")
            for key, val in product["specifications"].items():
                lines.append(f"  - {key}: {val}")
        return "\n".join(lines)
    except Exception as e:
        return f"Error retrieving product details: {e}"
    finally:
        db.close()


@tool
def compare_products(product_ids: str) -> str:
    """Compare multiple products side by side. Pass product IDs as a comma-separated string (e.g., '1,2,3').

    Use this when a customer wants to compare features, prices, or specifications of multiple products.
    """
    db = SessionLocal()
    try:
        ids = [int(x.strip()) for x in product_ids.split(",")]
        products = product_service.compare_products(db, ids)
        if not products:
            return "No products found for the given IDs."

        lines = [f"Comparing {len(products)} products:\n"]
        for p in products:
            lines.append(f"--- {p['name']} ---")
            lines.append(f"  Price: ${p['price']:.2f}")
            lines.append(
                f"  Rating: {p['rating']}/5 ({p['review_count']} reviews)"
            )
            lines.append(f"  Stock: {p['stock_quantity']} units")
            if p.get("specifications"):
                for key, val in p["specifications"].items():
                    lines.append(f"  {key}: {val}")
            lines.append("")
        return "\n".join(lines)
    except ValueError:
        return "Invalid product IDs. Please provide comma-separated integers (e.g., '1,2,3')."
    except Exception as e:
        return f"Error comparing products: {e}"
    finally:
        db.close()
