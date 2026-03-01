import logging

from fastapi import FastAPI

from app.api.middleware.cors import setup_cors
from app.api.middleware.error_handler import setup_error_handlers
from app.api.router import api_router
from app.config import get_settings
from app.db.database import init_db


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    settings = get_settings()

    # Configure logging
    logging.basicConfig(
        level=getattr(logging, settings.log_level),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    app = FastAPI(
        title=settings.app_name,
        description="Autonomous multi-agent customer care system powered by LLMs",
        version=settings.app_version,
    )

    # Middleware
    setup_cors(app)
    setup_error_handlers(app)

    # Routes
    app.include_router(api_router)

    # Startup event
    @app.on_event("startup")
    async def startup():
        logging.info("Initializing database...")
        init_db()

        # Auto-seed demo data if the database is empty
        from app.db.database import SessionLocal
        from app.db.models import User
        db = SessionLocal()
        try:
            if db.query(User).count() == 0:
                logging.info("Empty database detected — seeding demo data...")
                from app.db.seed import seed_database
                seed_database()
                logging.info("Demo data seeded successfully")
            else:
                logging.info("Database already has data — skipping seed")
        finally:
            db.close()

        logging.info("Application started successfully")

    return app


app = create_app()
