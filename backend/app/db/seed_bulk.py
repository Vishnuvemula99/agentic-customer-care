"""
Bulk seed script — generates 1,000 users and 1,000,000 orders over the last 6 months.

Distribution:
  - 1,000 users (70% standard, 20% premium, 10% VIP)
  - 1,000,000 orders across 6 months with realistic date distribution
  - ~1.5M order items (1–3 items per order from 25 products)
  - Status distribution: 40% delivered, 20% shipped, 15% in_transit, 10% confirmed, 10% pending, 5% cancelled

Recent orders (this month) have statuses that test return window policies:
  - Delivered 3-5 days ago  → within ALL return windows
  - Delivered 15-20 days ago → within 30/60 day windows, outside 14-day (books)
  - Delivered 35-45 days ago → within 60-day (clothing), outside 30-day (electronics/home)
  - Delivered 50-70 days ago → outside most windows except long ones
  - Delivered 90+ days ago   → outside ALL return windows

Performance note: Uses SQLAlchemy Core bulk insert for speed (~2-3 min for 1M orders).
"""

import json
import random
import sys
import time
from datetime import datetime, timedelta

from sqlalchemy import text, Index
from sqlalchemy.orm import Session

from app.db.database import Base, engine, SessionLocal
from app.db.models import Order, OrderItem, User, Product, ReturnPolicy, ReturnRequest


# ── Configuration ────────────────────────────────────────────────────────────
NUM_USERS = 1000
NUM_ORDERS = 1_000_000
BATCH_SIZE = 10_000  # Bulk insert batch size

CARRIERS = ["UPS", "FedEx", "USPS", "DHL", "OnTrac"]
STATUSES = ["delivered", "shipped", "in_transit", "confirmed", "pending", "cancelled"]
STATUS_WEIGHTS = [40, 20, 15, 10, 10, 5]  # Percentage distribution

STREETS = [
    "Main St", "Oak Ave", "Maple Dr", "Cedar Ln", "Pine Rd",
    "Elm St", "Birch Way", "Walnut Blvd", "Spruce Ct", "Willow Pl",
    "Park Ave", "Lake Dr", "River Rd", "Hill St", "Valley Way",
    "Forest Ln", "Meadow Dr", "Sunset Blvd", "Ocean Ave", "Mountain Rd",
]
CITIES = [
    ("Springfield", "IL", "62704"), ("New York", "NY", "10001"),
    ("Los Angeles", "CA", "90001"), ("Chicago", "IL", "60601"),
    ("Houston", "TX", "77001"), ("Phoenix", "AZ", "85001"),
    ("Philadelphia", "PA", "19101"), ("San Antonio", "TX", "78201"),
    ("San Diego", "CA", "92101"), ("Dallas", "TX", "75201"),
    ("Austin", "TX", "73301"), ("Denver", "CO", "80201"),
    ("Seattle", "WA", "98101"), ("Portland", "OR", "97201"),
    ("Miami", "FL", "33101"), ("Atlanta", "GA", "30301"),
    ("Boston", "MA", "02101"), ("Nashville", "TN", "37201"),
    ("Minneapolis", "MN", "55401"), ("Detroit", "MI", "48201"),
]
FIRST_NAMES = [
    "James", "Mary", "Robert", "Patricia", "John", "Jennifer", "Michael",
    "Linda", "David", "Elizabeth", "William", "Barbara", "Richard", "Susan",
    "Joseph", "Jessica", "Thomas", "Sarah", "Christopher", "Karen", "Charles",
    "Lisa", "Daniel", "Nancy", "Matthew", "Betty", "Anthony", "Margaret",
    "Mark", "Sandra", "Donald", "Ashley", "Steven", "Kimberly", "Andrew",
    "Emily", "Paul", "Donna", "Joshua", "Michelle", "Kenneth", "Dorothy",
    "Kevin", "Carol", "Brian", "Amanda", "George", "Melissa", "Timothy", "Deborah",
]
LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller",
    "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez",
    "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin",
    "Lee", "Perez", "Thompson", "White", "Harris", "Sanchez", "Clark",
    "Ramirez", "Lewis", "Robinson", "Walker", "Young", "Allen", "King",
    "Wright", "Scott", "Torres", "Nguyen", "Hill", "Flores", "Green",
    "Adams", "Nelson", "Baker", "Hall", "Rivera", "Campbell", "Mitchell", "Carter", "Roberts",
]


def _generate_tracking_number(carrier: str, idx: int) -> str:
    """Generate a realistic-ish tracking number."""
    if carrier == "UPS":
        return f"1Z999AA1{idx:010d}"
    elif carrier == "FedEx":
        return f"7946{idx:08d}"
    elif carrier == "USPS":
        return f"9400{idx:012d}"
    elif carrier == "DHL":
        return f"JD01{idx:010d}"
    else:
        return f"OT{idx:012d}"


def _generate_address() -> str:
    num = random.randint(100, 9999)
    street = random.choice(STREETS)
    city, state, zipcode = random.choice(CITIES)
    return json.dumps({
        "street": f"{num} {street}",
        "city": city,
        "state": state,
        "zip": zipcode,
        "country": "US",
    })


def seed_users(db: Session) -> None:
    """Generate 1,000 users with realistic distribution of membership tiers."""
    print(f"\n[1/5] Generating {NUM_USERS} users...")
    start = time.time()

    users = []
    tiers = ["standard"] * 700 + ["premium"] * 200 + ["vip"] * 100
    random.shuffle(tiers)

    used_emails = set()
    for i in range(1, NUM_USERS + 1):
        first = random.choice(FIRST_NAMES)
        last = random.choice(LAST_NAMES)

        # Ensure unique emails
        email = f"{first.lower()}.{last.lower()}{i}@email.com"
        while email in used_emails:
            email = f"{first.lower()}.{last.lower()}{i}{random.randint(1,99)}@email.com"
        used_emails.add(email)

        users.append({
            "id": i,
            "name": f"{first} {last}",
            "email": email,
            "phone": f"+1-555-{i:04d}",
            "address": _generate_address(),
            "membership_tier": tiers[i - 1],
            "created_at": datetime.utcnow() - timedelta(days=random.randint(30, 730)),
        })

    db.execute(User.__table__.insert(), users)
    db.flush()
    elapsed = time.time() - start
    print(f"  ✓ {NUM_USERS} users created in {elapsed:.1f}s")


def seed_products_and_policies(db: Session) -> None:
    """Re-use the original 25 products and 5 return policies from seed.py."""
    from app.db.seed import _seed_products, _seed_return_policies
    print("\n[2/5] Seeding 25 products and 5 return policies...")
    start = time.time()
    _seed_products(db)
    _seed_return_policies(db)
    db.flush()
    elapsed = time.time() - start
    print(f"  ✓ Products and policies created in {elapsed:.1f}s")


def seed_orders(db: Session) -> None:
    """Generate 1,000,000 orders distributed over the last 6 months.

    Date distribution strategy:
      - 60% of orders: 30-180 days ago (bulk historical)
      - 20% of orders: 7-30 days ago (recent — active returns window)
      - 15% of orders: 1-7 days ago (very recent — all windows open)
      - 5% of orders: today (pending/confirmed)
    """
    print(f"\n[3/5] Generating {NUM_ORDERS:,} orders...")
    start = time.time()
    now = datetime.utcnow()

    # Pre-calculate status for each order
    statuses_pool = random.choices(STATUSES, weights=STATUS_WEIGHTS, k=NUM_ORDERS)

    orders_batch = []
    total_inserted = 0

    for i in range(1, NUM_ORDERS + 1):
        user_id = random.randint(1, NUM_USERS)
        status = statuses_pool[i - 1]
        order_number = f"ORD-2025-{i:07d}"

        # Determine order date based on distribution
        rand = random.random()
        if rand < 0.05:
            # 5%: today — pending/confirmed
            days_ago = 0
            status = random.choice(["pending", "confirmed"])
        elif rand < 0.20:
            # 15%: 1-7 days ago — very recent
            days_ago = random.randint(1, 7)
        elif rand < 0.40:
            # 20%: 7-30 days ago — active return window
            days_ago = random.randint(7, 30)
        else:
            # 60%: 30-180 days ago — historical
            days_ago = random.randint(30, 180)

        created_at = now - timedelta(
            days=days_ago,
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59),
        )

        # Status-appropriate dates
        carrier = random.choice(CARRIERS)
        tracking_number = None
        estimated_delivery = None
        updated_at = created_at

        if status == "delivered":
            # Delivered: delivery was days_ago - random(1-5) days before now
            delivery_offset = max(1, days_ago - random.randint(1, 5))
            estimated_delivery = now - timedelta(days=delivery_offset)
            updated_at = estimated_delivery
            tracking_number = _generate_tracking_number(carrier, i)
        elif status in ("shipped", "in_transit"):
            estimated_delivery = now + timedelta(days=random.randint(1, 7))
            updated_at = created_at + timedelta(days=random.randint(1, 3))
            tracking_number = _generate_tracking_number(carrier, i)
        elif status == "confirmed":
            estimated_delivery = now + timedelta(days=random.randint(5, 14))
            updated_at = created_at + timedelta(hours=random.randint(1, 12))
        elif status == "cancelled":
            updated_at = created_at + timedelta(hours=random.randint(1, 48))
            carrier = None
        elif status == "pending":
            carrier = None

        # Random items: 1-3 products, total price
        num_items = random.choices([1, 2, 3], weights=[50, 35, 15])[0]
        product_ids = random.sample(range(1, 26), num_items)
        # Approximate total (we'll calculate exact from items)
        total_amount = round(random.uniform(15.0, 2500.0), 2)

        orders_batch.append({
            "id": i,
            "user_id": user_id,
            "order_number": order_number,
            "status": status,
            "total_amount": total_amount,
            "shipping_address": _generate_address(),
            "tracking_number": tracking_number,
            "carrier": carrier,
            "estimated_delivery": estimated_delivery,
            "created_at": created_at,
            "updated_at": updated_at,
        })

        if len(orders_batch) >= BATCH_SIZE:
            db.execute(Order.__table__.insert(), orders_batch)
            total_inserted += len(orders_batch)
            orders_batch = []
            elapsed = time.time() - start
            rate = total_inserted / elapsed
            print(f"  ... {total_inserted:>10,} / {NUM_ORDERS:,} orders ({rate:,.0f}/s)", end="\r")
            sys.stdout.flush()

    # Insert remaining
    if orders_batch:
        db.execute(Order.__table__.insert(), orders_batch)
        total_inserted += len(orders_batch)

    db.flush()
    elapsed = time.time() - start
    print(f"\n  ✓ {total_inserted:,} orders created in {elapsed:.1f}s ({total_inserted/elapsed:,.0f}/s)")


def seed_order_items(db: Session) -> None:
    """Generate order items for all orders (1-3 items each, ~1.5M total)."""
    print(f"\n[4/5] Generating order items (~1.5M)...")
    start = time.time()

    # Product prices for accurate line items
    product_prices = {
        1: 349.99, 2: 1299.00, 3: 1199.99, 4: 449.99, 5: 99.99,
        6: 199.99, 7: 1299.00, 8: 249.00, 9: 129.99, 10: 69.50,
        11: 199.00, 12: 29.99, 13: 89.99, 14: 89.99, 15: 749.99,
        16: 699.95, 17: 179.99, 18: 168.00, 19: 120.00, 20: 429.00,
        21: 449.99, 22: 249.00, 23: 44.99, 24: 39.99, 25: 16.99,
    }

    items_batch = []
    total_items = 0
    item_id = 1

    for order_id in range(1, NUM_ORDERS + 1):
        num_items = random.choices([1, 2, 3], weights=[50, 35, 15])[0]
        product_ids = random.sample(range(1, 26), num_items)

        for pid in product_ids:
            qty = random.choices([1, 2, 3], weights=[80, 15, 5])[0]
            items_batch.append({
                "id": item_id,
                "order_id": order_id,
                "product_id": pid,
                "quantity": qty,
                "unit_price": product_prices[pid],
            })
            item_id += 1

        if len(items_batch) >= BATCH_SIZE:
            db.execute(OrderItem.__table__.insert(), items_batch)
            total_items += len(items_batch)
            items_batch = []
            elapsed = time.time() - start
            rate = total_items / elapsed if elapsed > 0 else 0
            print(f"  ... {total_items:>10,} items ({rate:,.0f}/s)", end="\r")
            sys.stdout.flush()

    if items_batch:
        db.execute(OrderItem.__table__.insert(), items_batch)
        total_items += len(items_batch)

    db.flush()
    elapsed = time.time() - start
    print(f"\n  ✓ {total_items:,} order items created in {elapsed:.1f}s ({total_items/elapsed:,.0f}/s)")


def add_indexes(db: Session) -> None:
    """Add performance indexes for order lookup queries."""
    print("\n[5/5] Adding performance indexes...")
    start = time.time()

    indexes = [
        "CREATE INDEX IF NOT EXISTS ix_orders_user_id ON orders(user_id)",
        "CREATE INDEX IF NOT EXISTS ix_orders_status ON orders(status)",
        "CREATE INDEX IF NOT EXISTS ix_orders_created_at ON orders(created_at)",
        "CREATE INDEX IF NOT EXISTS ix_orders_user_status ON orders(user_id, status)",
        "CREATE INDEX IF NOT EXISTS ix_order_items_order_id ON order_items(order_id)",
        "CREATE INDEX IF NOT EXISTS ix_order_items_product_id ON order_items(product_id)",
    ]
    for idx_sql in indexes:
        db.execute(text(idx_sql))
        idx_name = idx_sql.split("INDEX IF NOT EXISTS ")[1].split(" ON")[0]
        print(f"  ✓ {idx_name}")

    db.flush()
    elapsed = time.time() - start
    print(f"  Indexes created in {elapsed:.1f}s")


def run_benchmarks(db: Session) -> None:
    """Run order lookup benchmarks against the 1M order database."""
    print("\n" + "=" * 70)
    print("PERFORMANCE BENCHMARKS — 1,000,000 orders")
    print("=" * 70)

    from app.services.order_service import get_order_by_number, get_order_status, get_orders_by_user

    # --- Benchmark 1: Single order lookup by order_number ---
    test_order_numbers = [
        f"ORD-2025-{random.randint(1, NUM_ORDERS):07d}" for _ in range(100)
    ]

    print("\n1. Single order lookup by order_number (100 queries):")
    times = []
    for on in test_order_numbers:
        t0 = time.perf_counter()
        result = get_order_by_number(db, on)
        t1 = time.perf_counter()
        times.append((t1 - t0) * 1000)  # ms

    print(f"   Min:    {min(times):.2f} ms")
    print(f"   Max:    {max(times):.2f} ms")
    print(f"   Avg:    {sum(times)/len(times):.2f} ms")
    print(f"   Median: {sorted(times)[len(times)//2]:.2f} ms")
    print(f"   P95:    {sorted(times)[int(len(times)*0.95)]:.2f} ms")
    print(f"   P99:    {sorted(times)[int(len(times)*0.99)]:.2f} ms")

    # --- Benchmark 2: Order status lookup ---
    print("\n2. Order status lookup by order_number (100 queries):")
    times = []
    for on in test_order_numbers:
        t0 = time.perf_counter()
        result = get_order_status(db, on)
        t1 = time.perf_counter()
        times.append((t1 - t0) * 1000)

    print(f"   Min:    {min(times):.2f} ms")
    print(f"   Max:    {max(times):.2f} ms")
    print(f"   Avg:    {sum(times)/len(times):.2f} ms")
    print(f"   Median: {sorted(times)[len(times)//2]:.2f} ms")
    print(f"   P95:    {sorted(times)[int(len(times)*0.95)]:.2f} ms")
    print(f"   P99:    {sorted(times)[int(len(times)*0.99)]:.2f} ms")

    # --- Benchmark 3: All orders by user_id ---
    test_user_ids = [random.randint(1, NUM_USERS) for _ in range(50)]

    print("\n3. All orders by user_id (50 queries):")
    times = []
    counts = []
    for uid in test_user_ids:
        t0 = time.perf_counter()
        result = get_orders_by_user(db, uid)
        t1 = time.perf_counter()
        times.append((t1 - t0) * 1000)
        counts.append(len(result))

    print(f"   Min:    {min(times):.2f} ms")
    print(f"   Max:    {max(times):.2f} ms")
    print(f"   Avg:    {sum(times)/len(times):.2f} ms")
    print(f"   Median: {sorted(times)[len(times)//2]:.2f} ms")
    print(f"   P95:    {sorted(times)[int(len(times)*0.95)]:.2f} ms")
    print(f"   P99:    {sorted(times)[int(len(times)*0.99)]:.2f} ms")
    print(f"   Avg orders per user: {sum(counts)/len(counts):.0f}")

    # --- Benchmark 4: Worst-case user (most orders) ---
    print("\n4. Finding user with most orders...")
    result = db.execute(text(
        "SELECT user_id, COUNT(*) as cnt FROM orders GROUP BY user_id ORDER BY cnt DESC LIMIT 1"
    )).fetchone()
    if result:
        top_user, top_count = result[0], result[1]
        t0 = time.perf_counter()
        orders = get_orders_by_user(db, top_user)
        t1 = time.perf_counter()
        print(f"   User {top_user} has {top_count} orders")
        print(f"   Lookup time: {(t1-t0)*1000:.2f} ms")

    # --- Benchmark 5: Order by non-existent number ---
    print("\n5. Lookup non-existent order (miss):")
    times = []
    for _ in range(100):
        t0 = time.perf_counter()
        result = get_order_by_number(db, f"ORD-FAKE-{random.randint(1,999999):07d}")
        t1 = time.perf_counter()
        times.append((t1 - t0) * 1000)

    print(f"   Min:    {min(times):.2f} ms")
    print(f"   Max:    {max(times):.2f} ms")
    print(f"   Avg:    {sum(times)/len(times):.2f} ms")

    # --- DB Stats ---
    print("\n" + "-" * 70)
    print("DATABASE STATISTICS:")
    for table in ["users", "orders", "order_items", "products", "return_policies"]:
        count = db.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar()
        print(f"   {table:20s}: {count:>12,} rows")

    db_size = db.execute(text("SELECT page_count * page_size FROM pragma_page_count(), pragma_page_size()")).scalar()
    print(f"   {'DB file size':20s}: {db_size/1024/1024:>10.1f} MB")
    print("=" * 70)


def seed_bulk() -> None:
    """Main entry point — drops, recreates, and bulk-seeds the database."""
    total_start = time.time()

    print("=" * 70)
    print(f"BULK SEED: {NUM_USERS:,} users, {NUM_ORDERS:,} orders")
    print("=" * 70)

    print("\nDropping all tables...")
    Base.metadata.drop_all(bind=engine)
    print("Creating all tables...")
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        seed_users(db)
        seed_products_and_policies(db)
        seed_orders(db)
        seed_order_items(db)

        print("\nCommitting all data...")
        commit_start = time.time()
        db.commit()
        print(f"  ✓ Commit done in {time.time() - commit_start:.1f}s")

        add_indexes(db)
        db.commit()

        total_elapsed = time.time() - total_start
        print(f"\n🎉 Total seeding time: {total_elapsed:.1f}s ({total_elapsed/60:.1f} min)")

        # Run benchmarks
        run_benchmarks(db)

    except Exception as e:
        db.rollback()
        print(f"\n❌ Error: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_bulk()
