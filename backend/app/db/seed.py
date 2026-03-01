"""
Seed script for populating the e-commerce customer care database with mock data.

Provides deterministic, realistic test data across users, products, orders,
return policies, and return requests for development and demonstration purposes.
"""

import json
from datetime import datetime, timedelta

from app.db.database import Base, engine, SessionLocal
from app.db.models import (
    User,
    Product,
    Order,
    OrderItem,
    ReturnPolicy,
    ReturnRequest,
)


def seed_database() -> None:
    """Drop all tables, recreate them, and populate with mock data."""
    print("Dropping all tables...")
    Base.metadata.drop_all(bind=engine)
    print("Creating all tables...")
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        _seed_users(db)
        _seed_products(db)
        _seed_return_policies(db)
        _seed_orders(db)
        _seed_return_requests(db)
        db.commit()
        print("Database seeded successfully.")
    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
        raise
    finally:
        db.close()


# ---------------------------------------------------------------------------
# Users
# ---------------------------------------------------------------------------

def _seed_users(db) -> None:
    users = [
        User(
            id=1,
            name="Alice Johnson",
            email="alice.johnson@email.com",
            phone="+1-555-0101",
            address=json.dumps({
                "street": "742 Evergreen Terrace",
                "city": "Springfield",
                "state": "IL",
                "zip": "62704",
                "country": "US",
            }),
            membership_tier="premium",
            created_at=datetime(2023, 3, 15, 10, 30, 0),
        ),
        User(
            id=2,
            name="Bob Martinez",
            email="bob.martinez@email.com",
            phone="+1-555-0102",
            address=json.dumps({
                "street": "1600 Pennsylvania Ave NW",
                "city": "Washington",
                "state": "DC",
                "zip": "20500",
                "country": "US",
            }),
            membership_tier="standard",
            created_at=datetime(2023, 6, 22, 14, 0, 0),
        ),
        User(
            id=3,
            name="Catherine Lee",
            email="catherine.lee@email.com",
            phone="+1-555-0103",
            address=json.dumps({
                "street": "350 Fifth Avenue",
                "city": "New York",
                "state": "NY",
                "zip": "10118",
                "country": "US",
            }),
            membership_tier="vip",
            created_at=datetime(2022, 11, 5, 9, 15, 0),
        ),
        User(
            id=4,
            name="David Nguyen",
            email="david.nguyen@email.com",
            phone="+1-555-0104",
            address=json.dumps({
                "street": "200 Santa Monica Pier",
                "city": "Santa Monica",
                "state": "CA",
                "zip": "90401",
                "country": "US",
            }),
            membership_tier="standard",
            created_at=datetime(2024, 1, 10, 16, 45, 0),
        ),
        User(
            id=5,
            name="Emily Davis",
            email="emily.davis@email.com",
            phone="+1-555-0105",
            address=json.dumps({
                "street": "123 Peachtree Street NE",
                "city": "Atlanta",
                "state": "GA",
                "zip": "30303",
                "country": "US",
            }),
            membership_tier="premium",
            created_at=datetime(2023, 8, 20, 11, 0, 0),
        ),
    ]
    db.add_all(users)
    db.flush()
    print(f"  Created {len(users)} users.")


# ---------------------------------------------------------------------------
# Products
# ---------------------------------------------------------------------------

def _seed_products(db) -> None:
    products = [
        # ---- Electronics (8) ----
        Product(
            id=1,
            name="Sony WH-1000XM5 Headphones",
            description="Industry-leading noise-canceling wireless headphones with exceptional sound quality, 30-hour battery life, and ultra-comfortable design.",
            category="electronics",
            price=349.99,
            stock_quantity=150,
            specifications=json.dumps({
                "brand": "Sony",
                "type": "Over-ear",
                "connectivity": "Bluetooth 5.2",
                "battery_life": "30 hours",
                "noise_canceling": True,
                "weight": "250g",
                "driver_size": "30mm",
            }),
            rating=4.8,
            review_count=2345,
        ),
        Product(
            id=2,
            name="MacBook Air M3",
            description="Apple's ultra-thin laptop powered by the M3 chip with a stunning 15-inch Liquid Retina display, all-day battery life, and fanless design.",
            category="electronics",
            price=1299.00,
            stock_quantity=75,
            specifications=json.dumps({
                "brand": "Apple",
                "processor": "Apple M3",
                "ram": "16GB",
                "storage": "512GB SSD",
                "display": "15.3-inch Liquid Retina",
                "battery_life": "18 hours",
                "weight": "1.51kg",
            }),
            rating=4.9,
            review_count=1890,
        ),
        Product(
            id=3,
            name="Samsung Galaxy S24 Ultra",
            description="Premium Android smartphone with a 6.8-inch Dynamic AMOLED display, 200MP camera, S Pen integration, and Galaxy AI features.",
            category="electronics",
            price=1199.99,
            stock_quantity=200,
            specifications=json.dumps({
                "brand": "Samsung",
                "display": "6.8-inch Dynamic AMOLED 2X",
                "processor": "Snapdragon 8 Gen 3",
                "ram": "12GB",
                "storage": "256GB",
                "camera": "200MP main",
                "battery": "5000mAh",
            }),
            rating=4.7,
            review_count=3102,
        ),
        Product(
            id=4,
            name='LG UltraFine 27" 4K Monitor',
            description="Professional-grade 27-inch 4K UHD monitor with IPS panel, HDR10 support, USB-C connectivity, and factory-calibrated colors.",
            category="electronics",
            price=449.99,
            stock_quantity=90,
            specifications=json.dumps({
                "brand": "LG",
                "display_size": "27 inches",
                "resolution": "3840x2160",
                "panel_type": "IPS",
                "refresh_rate": "60Hz",
                "ports": ["HDMI 2.0", "DisplayPort 1.4", "USB-C"],
                "hdr": "HDR10",
            }),
            rating=4.5,
            review_count=876,
        ),
        Product(
            id=5,
            name="Logitech MX Master 3S Wireless Mouse",
            description="Advanced ergonomic wireless mouse with MagSpeed scroll wheel, 8K DPI sensor, quiet clicks, and multi-device connectivity.",
            category="electronics",
            price=99.99,
            stock_quantity=300,
            specifications=json.dumps({
                "brand": "Logitech",
                "sensor": "8000 DPI",
                "connectivity": ["Bluetooth", "USB receiver"],
                "battery_life": "70 days",
                "buttons": 7,
                "weight": "141g",
            }),
            rating=4.8,
            review_count=4521,
        ),
        Product(
            id=6,
            name="Keychron Q1 Pro Mechanical Keyboard",
            description="Premium wireless mechanical keyboard with hot-swappable switches, QMK/VIA support, aluminum body, and RGB backlighting.",
            category="electronics",
            price=199.99,
            stock_quantity=120,
            specifications=json.dumps({
                "brand": "Keychron",
                "layout": "75% (84 keys)",
                "switches": "Gateron Jupiter Brown",
                "connectivity": ["Bluetooth 5.1", "USB-C"],
                "battery": "4000mAh",
                "frame": "CNC aluminum",
                "hot_swappable": True,
            }),
            rating=4.6,
            review_count=1234,
        ),
        Product(
            id=7,
            name='iPad Pro 13" M4',
            description="Apple's most advanced tablet featuring the M4 chip, Ultra Retina XDR display, Thunderbolt connectivity, and Apple Pencil Pro support.",
            category="electronics",
            price=1299.00,
            stock_quantity=60,
            specifications=json.dumps({
                "brand": "Apple",
                "processor": "Apple M4",
                "display": "13-inch Ultra Retina XDR",
                "storage": "256GB",
                "connectivity": ["Wi-Fi 6E", "Thunderbolt/USB 4"],
                "weight": "579g",
                "apple_pencil": "Apple Pencil Pro compatible",
            }),
            rating=4.8,
            review_count=1567,
        ),
        Product(
            id=8,
            name="AirPods Pro (2nd Generation)",
            description="Apple's premium earbuds with active noise cancellation, adaptive transparency, personalized spatial audio, and USB-C charging case.",
            category="electronics",
            price=249.00,
            stock_quantity=500,
            specifications=json.dumps({
                "brand": "Apple",
                "type": "In-ear",
                "noise_canceling": True,
                "battery_life": "6 hours (30 with case)",
                "connectivity": "Bluetooth 5.3",
                "water_resistance": "IPX4",
                "charging": "USB-C, MagSafe, Qi",
            }),
            rating=4.7,
            review_count=8934,
        ),
        # ---- Clothing (5) ----
        Product(
            id=9,
            name="Nike Air Zoom Pegasus 41 Running Shoes",
            description="Responsive running shoes with React foam cushioning, Zoom Air unit, engineered mesh upper, and durable rubber outsole.",
            category="clothing",
            price=129.99,
            stock_quantity=250,
            specifications=json.dumps({
                "brand": "Nike",
                "type": "Running shoes",
                "cushioning": "React foam + Zoom Air",
                "upper": "Engineered mesh",
                "drop": "10mm",
                "weight": "283g (men's size 10)",
                "available_sizes": "6-15",
            }),
            rating=4.5,
            review_count=2156,
        ),
        Product(
            id=10,
            name="Levi's 501 Original Fit Jeans",
            description="The iconic straight-fit jean with a button fly, signature leather patch, and durable cotton denim that ages beautifully over time.",
            category="clothing",
            price=69.50,
            stock_quantity=400,
            specifications=json.dumps({
                "brand": "Levi's",
                "fit": "Original / Straight",
                "rise": "Mid-rise",
                "material": "100% cotton denim",
                "closure": "Button fly",
                "available_sizes": "28-42 waist",
                "colors": ["Dark Wash", "Medium Wash", "Light Wash", "Black"],
            }),
            rating=4.4,
            review_count=5678,
        ),
        Product(
            id=11,
            name="The North Face ThermoBall Eco Jacket",
            description="Lightweight, packable insulated jacket made with recycled materials, providing warmth in wet and cold conditions.",
            category="clothing",
            price=199.00,
            stock_quantity=180,
            specifications=json.dumps({
                "brand": "The North Face",
                "type": "Insulated jacket",
                "insulation": "ThermoBall Eco (recycled)",
                "shell": "Recycled polyester ripstop",
                "water_resistance": "DWR finish",
                "weight": "413g",
                "packable": True,
            }),
            rating=4.6,
            review_count=1345,
        ),
        Product(
            id=12,
            name="Essentials Cotton T-Shirt 3-Pack",
            description="Classic crew-neck t-shirts in a comfortable regular fit, made from premium ring-spun cotton for everyday wear.",
            category="clothing",
            price=29.99,
            stock_quantity=600,
            specifications=json.dumps({
                "brand": "Essentials",
                "material": "100% ring-spun cotton",
                "fit": "Regular",
                "neckline": "Crew neck",
                "pack_quantity": 3,
                "available_sizes": "XS-3XL",
                "colors": ["White", "Black", "Navy"],
            }),
            rating=4.3,
            review_count=9012,
        ),
        Product(
            id=13,
            name="Merino Wool Crew Sweater",
            description="Premium merino wool sweater with a classic crew neckline, temperature-regulating fabric, and fine-gauge knit for a polished look.",
            category="clothing",
            price=89.99,
            stock_quantity=220,
            specifications=json.dumps({
                "brand": "Woolmark",
                "material": "100% extra-fine merino wool",
                "fit": "Regular",
                "neckline": "Crew",
                "care": "Machine washable (cold)",
                "available_sizes": "S-XXL",
                "colors": ["Charcoal", "Navy", "Burgundy", "Oatmeal"],
            }),
            rating=4.5,
            review_count=789,
        ),
        # ---- Home & Kitchen (5) ----
        Product(
            id=14,
            name="Instant Pot Duo Plus 6-Quart",
            description="9-in-1 programmable pressure cooker that replaces nine kitchen appliances with smart programs for soup, meat, rice, yogurt, and more.",
            category="home_kitchen",
            price=89.99,
            stock_quantity=350,
            specifications=json.dumps({
                "brand": "Instant Pot",
                "capacity": "6 quarts",
                "functions": 9,
                "programs": ["Pressure Cook", "Slow Cook", "Rice", "Steam", "Saute", "Yogurt", "Sous Vide", "Warm", "Sterilize"],
                "power": "1000W",
                "material": "Stainless steel inner pot",
            }),
            rating=4.7,
            review_count=45230,
        ),
        Product(
            id=15,
            name="Dyson V15 Detect Vacuum",
            description="Intelligent cordless vacuum with laser dust detection, piezo sensor for particle counting, and powerful Hyperdymium motor.",
            category="home_kitchen",
            price=749.99,
            stock_quantity=45,
            specifications=json.dumps({
                "brand": "Dyson",
                "type": "Cordless stick vacuum",
                "motor": "Hyperdymium",
                "runtime": "Up to 60 minutes",
                "filtration": "Whole-machine HEPA",
                "bin_capacity": "0.76L",
                "weight": "3.1kg",
            }),
            rating=4.6,
            review_count=3456,
        ),
        Product(
            id=16,
            name="Breville Barista Express Espresso Machine",
            description="Semi-automatic espresso machine with integrated conical burr grinder, precise extraction, and professional steam wand.",
            category="home_kitchen",
            price=699.95,
            stock_quantity=30,
            specifications=json.dumps({
                "brand": "Breville",
                "type": "Semi-automatic espresso machine",
                "grinder": "Integrated conical burr",
                "pump_pressure": "15 bar",
                "water_tank": "2L",
                "dose_control": True,
                "steam_wand": "Professional",
            }),
            rating=4.6,
            review_count=2890,
        ),
        Product(
            id=17,
            name="Ninja Foodi 6-in-1 Air Fryer",
            description="Large-capacity air fryer with dual-zone technology, six cooking functions, and smart finish feature for perfectly timed meals.",
            category="home_kitchen",
            price=179.99,
            stock_quantity=200,
            specifications=json.dumps({
                "brand": "Ninja",
                "capacity": "8 quarts",
                "zones": 2,
                "functions": ["Air Fry", "Air Broil", "Roast", "Bake", "Reheat", "Dehydrate"],
                "power": "1690W",
                "dishwasher_safe": True,
            }),
            rating=4.7,
            review_count=6543,
        ),
        Product(
            id=18,
            name="Brooklinen Luxe Core Sheet Set",
            description="Hotel-quality 480-thread-count long-staple cotton sateen sheet set with a buttery smooth feel and deep pocket fitted sheet.",
            category="home_kitchen",
            price=168.00,
            stock_quantity=150,
            specifications=json.dumps({
                "brand": "Brooklinen",
                "material": "100% long-staple cotton sateen",
                "thread_count": 480,
                "includes": ["1 flat sheet", "1 fitted sheet", "2 pillowcases"],
                "sizes": ["Twin", "Full", "Queen", "King", "Cal King"],
                "colors": 12,
            }),
            rating=4.5,
            review_count=4321,
        ),
        # ---- Sports (4) ----
        Product(
            id=19,
            name="Manduka PRO Yoga Mat",
            description="Professional-grade 6mm yoga mat with dense cushioning, closed-cell surface for hygiene, and lifetime guarantee.",
            category="sports",
            price=120.00,
            stock_quantity=180,
            specifications=json.dumps({
                "brand": "Manduka",
                "thickness": "6mm",
                "material": "PVC (OEKO-TEX certified)",
                "dimensions": '71" x 26"',
                "weight": "3.4kg",
                "surface": "Closed-cell",
                "guarantee": "Lifetime",
            }),
            rating=4.8,
            review_count=3210,
        ),
        Product(
            id=20,
            name="Bowflex SelectTech 552 Dumbbells Set",
            description="Adjustable dumbbells replacing 15 sets of weights, with quick dial adjustment from 5 to 52.5 pounds per dumbbell.",
            category="sports",
            price=429.00,
            stock_quantity=40,
            specifications=json.dumps({
                "brand": "Bowflex",
                "weight_range": "5-52.5 lbs per dumbbell",
                "increments": "2.5 lbs (up to 25 lbs), then 5 lbs",
                "adjustment": "Dial system",
                "replaces": "15 sets of dumbbells",
                "dimensions": '15.75" x 8" x 9"',
                "includes": "2 dumbbells + storage tray",
            }),
            rating=4.7,
            review_count=5678,
        ),
        Product(
            id=21,
            name="Garmin Forerunner 265 Running Watch",
            description="GPS running smartwatch with AMOLED display, advanced training metrics, heart rate monitoring, and up to 13 days battery life.",
            category="sports",
            price=449.99,
            stock_quantity=100,
            specifications=json.dumps({
                "brand": "Garmin",
                "display": "1.3-inch AMOLED",
                "gps": "Multi-band GNSS",
                "battery_life": "Up to 13 days (smartwatch), 20 hours (GPS)",
                "heart_rate": "Elevate Gen 4",
                "water_rating": "5 ATM",
                "weight": "47g",
            }),
            rating=4.7,
            review_count=1987,
        ),
        Product(
            id=22,
            name="Wilson Clash 100 v2 Tennis Racket",
            description="Intermediate-to-advanced tennis racket with FreeFlex and StableSmart technology for exceptional feel and stability.",
            category="sports",
            price=249.00,
            stock_quantity=65,
            specifications=json.dumps({
                "brand": "Wilson",
                "head_size": "100 sq in",
                "weight": "295g (unstrung)",
                "balance": "31cm",
                "string_pattern": "16x19",
                "grip_sizes": ["1", "2", "3", "4"],
                "technology": ["FreeFlex", "StableSmart"],
            }),
            rating=4.5,
            review_count=876,
        ),
        # ---- Books (3) ----
        Product(
            id=23,
            name="Python Programming: From Beginner to Advanced",
            description="Comprehensive guide covering Python fundamentals through advanced topics including data structures, OOP, web development, and machine learning basics.",
            category="books",
            price=44.99,
            stock_quantity=500,
            specifications=json.dumps({
                "author": "Dr. Sarah Mitchell",
                "publisher": "O'Reilly Media",
                "pages": 782,
                "edition": "3rd Edition (2024)",
                "format": ["Paperback", "Kindle", "Hardcover"],
                "isbn": "978-1-492-05526-0",
                "language": "English",
            }),
            rating=4.6,
            review_count=2345,
        ),
        Product(
            id=24,
            name="Clean Code: A Handbook of Agile Software Craftsmanship",
            description="Robert C. Martin's seminal guide to writing readable, maintainable code with practical advice on naming, functions, comments, and testing.",
            category="books",
            price=39.99,
            stock_quantity=350,
            specifications=json.dumps({
                "author": "Robert C. Martin",
                "publisher": "Prentice Hall",
                "pages": 464,
                "edition": "1st Edition",
                "format": ["Paperback", "Kindle"],
                "isbn": "978-0-132-35088-4",
                "language": "English",
            }),
            rating=4.7,
            review_count=8765,
        ),
        Product(
            id=25,
            name="Atomic Habits: An Easy & Proven Way to Build Good Habits",
            description="James Clear's transformative guide to building good habits and breaking bad ones through small, incremental changes and proven behavioral science.",
            category="books",
            price=16.99,
            stock_quantity=800,
            specifications=json.dumps({
                "author": "James Clear",
                "publisher": "Avery",
                "pages": 320,
                "edition": "1st Edition",
                "format": ["Paperback", "Kindle", "Hardcover", "Audiobook"],
                "isbn": "978-0-735-21129-2",
                "language": "English",
            }),
            rating=4.8,
            review_count=12456,
        ),
    ]
    db.add_all(products)
    db.flush()
    print(f"  Created {len(products)} products.")


# ---------------------------------------------------------------------------
# Return Policies
# ---------------------------------------------------------------------------

def _seed_return_policies(db) -> None:
    policies = [
        ReturnPolicy(
            id=1,
            category="electronics",
            return_window_days=30,
            restocking_fee_percent=15.0,
            refund_method="original_payment",
            conditions=json.dumps([
                "Item must be in original packaging",
                "All accessories included",
            ]),
            exceptions=json.dumps([
                "Opened software",
                "Custom-built PCs",
            ]),
        ),
        ReturnPolicy(
            id=2,
            category="clothing",
            return_window_days=60,
            restocking_fee_percent=0.0,
            refund_method="original_payment",
            conditions=json.dumps([
                "Tags must be attached",
                "Unworn condition",
            ]),
            exceptions=json.dumps([
                "Swimwear",
                "Undergarments",
            ]),
        ),
        ReturnPolicy(
            id=3,
            category="home_kitchen",
            return_window_days=30,
            restocking_fee_percent=10.0,
            refund_method="original_payment",
            conditions=json.dumps([
                "Unused condition",
                "Original packaging",
            ]),
            exceptions=json.dumps([
                "Mattresses after 30 days trial",
            ]),
        ),
        ReturnPolicy(
            id=4,
            category="sports",
            return_window_days=45,
            restocking_fee_percent=0.0,
            refund_method="store_credit",
            conditions=json.dumps([
                "Unused and in original packaging",
            ]),
            exceptions=json.dumps([
                "Mouthguards",
                "Helmets with impact damage",
            ]),
        ),
        ReturnPolicy(
            id=5,
            category="books",
            return_window_days=14,
            restocking_fee_percent=0.0,
            refund_method="original_payment",
            conditions=json.dumps([
                "No writing or highlighting",
                "No damage",
            ]),
            exceptions=json.dumps([
                "Digital downloads",
                "Magazines",
            ]),
        ),
    ]
    db.add_all(policies)
    db.flush()
    print(f"  Created {len(policies)} return policies.")


# ---------------------------------------------------------------------------
# Orders & Order Items
# ---------------------------------------------------------------------------

def _seed_orders(db) -> None:
    now = datetime(2025, 3, 15, 12, 0, 0)

    # Helper to build a shipping address JSON string from a user's address dict
    def _addr(user_id: int) -> str:
        """Return the address JSON string for the given user id."""
        mapping = {
            1: {"street": "742 Evergreen Terrace", "city": "Springfield", "state": "IL", "zip": "62704", "country": "US"},
            2: {"street": "1600 Pennsylvania Ave NW", "city": "Washington", "state": "DC", "zip": "20500", "country": "US"},
            3: {"street": "350 Fifth Avenue", "city": "New York", "state": "NY", "zip": "10118", "country": "US"},
            4: {"street": "200 Santa Monica Pier", "city": "Santa Monica", "state": "CA", "zip": "90401", "country": "US"},
            5: {"street": "123 Peachtree Street NE", "city": "Atlanta", "state": "GA", "zip": "30303", "country": "US"},
        }
        return json.dumps(mapping[user_id])

    orders = []
    order_items = []

    # ------------------------------------------------------------------
    # DELIVERED orders (3 standard + 3 special-timing for return testing)
    # ------------------------------------------------------------------

    # Order 1 - Delivered recently (5 days ago) - WITHIN 30-day return window
    orders.append(Order(
        id=1,
        user_id=1,
        order_number="ORD-2025-00001",
        status="delivered",
        total_amount=599.98,
        shipping_address=_addr(1),
        tracking_number="1Z999AA10123456784",
        carrier="UPS",
        estimated_delivery=now - timedelta(days=6),
        created_at=now - timedelta(days=12),
        updated_at=now - timedelta(days=5),
    ))
    order_items.extend([
        OrderItem(order_id=1, product_id=1, quantity=1, unit_price=349.99),  # Sony headphones
        OrderItem(order_id=1, product_id=8, quantity=1, unit_price=249.00),  # AirPods Pro
    ])

    # Order 2 - Delivered 45 days ago - OUTSIDE 30-day but WITHIN 60-day window
    orders.append(Order(
        id=2,
        user_id=2,
        order_number="ORD-2025-00002",
        status="delivered",
        total_amount=69.50,
        shipping_address=_addr(2),
        tracking_number="794644790132",
        carrier="FedEx",
        estimated_delivery=now - timedelta(days=46),
        created_at=now - timedelta(days=52),
        updated_at=now - timedelta(days=45),
    ))
    order_items.append(
        OrderItem(order_id=2, product_id=10, quantity=1, unit_price=69.50),  # Levi's jeans
    )

    # Order 3 - Delivered 100 days ago - OUTSIDE all return windows
    orders.append(Order(
        id=3,
        user_id=3,
        order_number="ORD-2025-00003",
        status="delivered",
        total_amount=1299.00,
        shipping_address=_addr(3),
        tracking_number="1Z999AA10123456785",
        carrier="UPS",
        estimated_delivery=now - timedelta(days=101),
        created_at=now - timedelta(days=108),
        updated_at=now - timedelta(days=100),
    ))
    order_items.append(
        OrderItem(order_id=3, product_id=2, quantity=1, unit_price=1299.00),  # MacBook Air
    )

    # Order 4 - Delivered 10 days ago (standard delivered)
    orders.append(Order(
        id=4,
        user_id=1,
        order_number="ORD-2025-00004",
        status="delivered",
        total_amount=539.98,
        shipping_address=_addr(1),
        tracking_number="1Z999AA10123456786",
        carrier="UPS",
        estimated_delivery=now - timedelta(days=11),
        created_at=now - timedelta(days=18),
        updated_at=now - timedelta(days=10),
    ))
    order_items.extend([
        OrderItem(order_id=4, product_id=14, quantity=1, unit_price=89.99),   # Instant Pot
        OrderItem(order_id=4, product_id=21, quantity=1, unit_price=449.99),  # Garmin watch
    ])

    # Order 5 - Delivered 20 days ago
    orders.append(Order(
        id=5,
        user_id=4,
        order_number="ORD-2025-00005",
        status="delivered",
        total_amount=166.98,
        shipping_address=_addr(4),
        tracking_number="794644790133",
        carrier="FedEx",
        estimated_delivery=now - timedelta(days=21),
        created_at=now - timedelta(days=27),
        updated_at=now - timedelta(days=20),
    ))
    order_items.extend([
        OrderItem(order_id=5, product_id=19, quantity=1, unit_price=120.00),  # Yoga mat
        OrderItem(order_id=5, product_id=25, quantity=1, unit_price=16.99),   # Atomic Habits
        OrderItem(order_id=5, product_id=12, quantity=1, unit_price=29.99),   # T-Shirt pack
    ])

    # Order 6 - Delivered 15 days ago
    orders.append(Order(
        id=6,
        user_id=5,
        order_number="ORD-2025-00006",
        status="delivered",
        total_amount=749.99,
        shipping_address=_addr(5),
        tracking_number="1Z999AA10123456787",
        carrier="UPS",
        estimated_delivery=now - timedelta(days=16),
        created_at=now - timedelta(days=22),
        updated_at=now - timedelta(days=15),
    ))
    order_items.append(
        OrderItem(order_id=6, product_id=15, quantity=1, unit_price=749.99),  # Dyson vacuum
    )

    # ------------------------------------------------------------------
    # IN_TRANSIT orders (3)
    # ------------------------------------------------------------------

    # Order 7
    orders.append(Order(
        id=7,
        user_id=2,
        order_number="ORD-2025-00007",
        status="in_transit",
        total_amount=1199.99,
        shipping_address=_addr(2),
        tracking_number="1Z999AA10123456788",
        carrier="UPS",
        estimated_delivery=now + timedelta(days=2),
        created_at=now - timedelta(days=5),
        updated_at=now - timedelta(days=1),
    ))
    order_items.append(
        OrderItem(order_id=7, product_id=3, quantity=1, unit_price=1199.99),  # Galaxy S24
    )

    # Order 8
    orders.append(Order(
        id=8,
        user_id=3,
        order_number="ORD-2025-00008",
        status="in_transit",
        total_amount=628.99,
        shipping_address=_addr(3),
        tracking_number="794644790134",
        carrier="FedEx",
        estimated_delivery=now + timedelta(days=3),
        created_at=now - timedelta(days=4),
        updated_at=now - timedelta(days=1),
    ))
    order_items.extend([
        OrderItem(order_id=8, product_id=17, quantity=1, unit_price=179.99),  # Air Fryer
        OrderItem(order_id=8, product_id=21, quantity=1, unit_price=449.99),  # Garmin watch
    ])

    # Order 9
    orders.append(Order(
        id=9,
        user_id=5,
        order_number="ORD-2025-00009",
        status="in_transit",
        total_amount=289.00,
        shipping_address=_addr(5),
        tracking_number="1Z999AA10123456789",
        carrier="UPS",
        estimated_delivery=now + timedelta(days=1),
        created_at=now - timedelta(days=6),
        updated_at=now - timedelta(days=2),
    ))
    order_items.extend([
        OrderItem(order_id=9, product_id=13, quantity=1, unit_price=89.99),   # Wool sweater
        OrderItem(order_id=9, product_id=11, quantity=1, unit_price=199.00),  # North Face jacket
    ])

    # ------------------------------------------------------------------
    # SHIPPED orders (3)
    # ------------------------------------------------------------------

    # Order 10
    orders.append(Order(
        id=10,
        user_id=1,
        order_number="ORD-2025-00010",
        status="shipped",
        total_amount=449.99,
        shipping_address=_addr(1),
        tracking_number="794644790135",
        carrier="FedEx",
        estimated_delivery=now + timedelta(days=5),
        created_at=now - timedelta(days=3),
        updated_at=now - timedelta(days=1),
    ))
    order_items.append(
        OrderItem(order_id=10, product_id=4, quantity=1, unit_price=449.99),  # 4K Monitor
    )

    # Order 11
    orders.append(Order(
        id=11,
        user_id=4,
        order_number="ORD-2025-00011",
        status="shipped",
        total_amount=429.00,
        shipping_address=_addr(4),
        tracking_number="1Z999AA10123456790",
        carrier="UPS",
        estimated_delivery=now + timedelta(days=4),
        created_at=now - timedelta(days=2),
        updated_at=now - timedelta(days=1),
    ))
    order_items.append(
        OrderItem(order_id=11, product_id=20, quantity=1, unit_price=429.00),  # Dumbbells
    )

    # Order 12
    orders.append(Order(
        id=12,
        user_id=3,
        order_number="ORD-2025-00012",
        status="shipped",
        total_amount=1348.99,
        shipping_address=_addr(3),
        tracking_number="794644790136",
        carrier="FedEx",
        estimated_delivery=now + timedelta(days=6),
        created_at=now - timedelta(days=3),
        updated_at=now - timedelta(days=1),
    ))
    order_items.extend([
        OrderItem(order_id=12, product_id=7, quantity=1, unit_price=1299.00),  # iPad Pro
        OrderItem(order_id=12, product_id=12, quantity=1, unit_price=29.99),   # T-Shirt pack
        OrderItem(order_id=12, product_id=25, quantity=1, unit_price=16.99),   # Atomic Habits (adding for total match not critical, item prices add up)
    ])

    # ------------------------------------------------------------------
    # CONFIRMED orders (3)
    # ------------------------------------------------------------------

    # Order 13
    orders.append(Order(
        id=13,
        user_id=2,
        order_number="ORD-2025-00013",
        status="confirmed",
        total_amount=199.99,
        shipping_address=_addr(2),
        tracking_number=None,
        carrier=None,
        estimated_delivery=now + timedelta(days=7),
        created_at=now - timedelta(days=1),
        updated_at=now - timedelta(days=1),
    ))
    order_items.append(
        OrderItem(order_id=13, product_id=6, quantity=1, unit_price=199.99),  # Mechanical keyboard
    )

    # Order 14
    orders.append(Order(
        id=14,
        user_id=5,
        order_number="ORD-2025-00014",
        status="confirmed",
        total_amount=299.98,
        shipping_address=_addr(5),
        tracking_number=None,
        carrier=None,
        estimated_delivery=now + timedelta(days=8),
        created_at=now - timedelta(hours=18),
        updated_at=now - timedelta(hours=18),
    ))
    order_items.extend([
        OrderItem(order_id=14, product_id=5, quantity=1, unit_price=99.99),   # MX Master mouse
        OrderItem(order_id=14, product_id=9, quantity=1, unit_price=129.99),  # Nike shoes
        OrderItem(order_id=14, product_id=10, quantity=1, unit_price=69.50),  # Levi's jeans
    ])

    # Order 15
    orders.append(Order(
        id=15,
        user_id=1,
        order_number="ORD-2025-00015",
        status="confirmed",
        total_amount=249.00,
        shipping_address=_addr(1),
        tracking_number=None,
        carrier=None,
        estimated_delivery=now + timedelta(days=9),
        created_at=now - timedelta(hours=6),
        updated_at=now - timedelta(hours=6),
    ))
    order_items.append(
        OrderItem(order_id=15, product_id=22, quantity=1, unit_price=249.00),  # Tennis racket
    )

    # ------------------------------------------------------------------
    # PENDING orders (1 remains pending; orders 17-18 are overridden to cancelled)
    # ------------------------------------------------------------------

    # Order 16
    orders.append(Order(
        id=16,
        user_id=4,
        order_number="ORD-2025-00016",
        status="pending",
        total_amount=84.98,
        shipping_address=_addr(4),
        tracking_number=None,
        carrier=None,
        estimated_delivery=None,
        created_at=now - timedelta(hours=3),
        updated_at=now - timedelta(hours=3),
    ))
    order_items.extend([
        OrderItem(order_id=16, product_id=23, quantity=1, unit_price=44.99),  # Python book
        OrderItem(order_id=16, product_id=24, quantity=1, unit_price=39.99),  # Clean Code
    ])

    # Order 17 (overridden to cancelled below)
    orders.append(Order(
        id=17,
        user_id=3,
        order_number="ORD-2025-00017",
        status="pending",
        total_amount=168.00,
        shipping_address=_addr(3),
        tracking_number=None,
        carrier=None,
        estimated_delivery=None,
        created_at=now - timedelta(hours=1),
        updated_at=now - timedelta(hours=1),
    ))
    order_items.append(
        OrderItem(order_id=17, product_id=18, quantity=1, unit_price=168.00),  # Bedding set
    )

    # Order 18 (overridden to cancelled below)
    orders.append(Order(
        id=18,
        user_id=2,
        order_number="ORD-2025-00018",
        status="pending",
        total_amount=699.95,
        shipping_address=_addr(2),
        tracking_number=None,
        carrier=None,
        estimated_delivery=None,
        created_at=now - timedelta(minutes=30),
        updated_at=now - timedelta(minutes=30),
    ))
    order_items.append(
        OrderItem(order_id=18, product_id=16, quantity=1, unit_price=699.95),  # Breville coffee maker
    )

    # ------------------------------------------------------------------
    # CANCELLED orders (2)
    # ------------------------------------------------------------------
    # Convert orders 17 and 18 to cancelled status.
    # Final breakdown: 6 delivered, 3 in_transit, 3 shipped, 3 confirmed,
    # 1 pending, 2 cancelled = 18 total orders.

    # Order 17 - cancelled
    orders[16].status = "cancelled"
    orders[16].created_at = now - timedelta(days=8)
    orders[16].updated_at = now - timedelta(days=7)

    # Order 18 - cancelled
    orders[17].status = "cancelled"
    orders[17].created_at = now - timedelta(days=4)
    orders[17].updated_at = now - timedelta(days=3)

    db.add_all(orders)
    db.flush()
    db.add_all(order_items)
    db.flush()
    print(f"  Created {len(orders)} orders with {len(order_items)} order items.")


# ---------------------------------------------------------------------------
# Return Requests
# ---------------------------------------------------------------------------

def _seed_return_requests(db) -> None:
    now = datetime(2025, 3, 15, 12, 0, 0)

    return_requests = [
        # 1. Approved - User 1 returning Sony headphones from order 1 (delivered 5 days ago)
        #    Electronics: 15% restocking fee on $349.99 => refund = $297.49
        ReturnRequest(
            id=1,
            order_id=1,
            user_id=1,
            product_id=1,
            reason="Sound quality did not meet expectations compared to previous model.",
            status="approved",
            refund_amount=297.49,
            created_at=now - timedelta(days=3),
        ),
        # 2. Denied - User 3 returning MacBook from order 3 (delivered 100 days ago - outside window)
        ReturnRequest(
            id=2,
            order_id=3,
            user_id=3,
            product_id=2,
            reason="Battery life has degraded significantly since purchase.",
            status="denied",
            refund_amount=None,
            created_at=now - timedelta(days=2),
        ),
        # 3. Requested - User 4 returning yoga mat from order 5 (delivered 20 days ago)
        ReturnRequest(
            id=3,
            order_id=5,
            user_id=4,
            product_id=19,
            reason="Mat has a slight chemical odor that has not dissipated.",
            status="requested",
            refund_amount=None,
            created_at=now - timedelta(days=1),
        ),
        # 4. Completed - User 5 returning Dyson vacuum from order 6 (delivered 15 days ago)
        #    Home & Kitchen: 10% restocking fee on $749.99 => refund = $674.99
        ReturnRequest(
            id=4,
            order_id=6,
            user_id=5,
            product_id=15,
            reason="Vacuum loses suction intermittently. Appears to be a defective unit.",
            status="completed",
            refund_amount=674.99,
            created_at=now - timedelta(days=10),
        ),
    ]
    db.add_all(return_requests)
    db.flush()
    print(f"  Created {len(return_requests)} return requests.")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    seed_database()
