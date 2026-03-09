"""
FastAPI application for the DDD pipeline API.

Provides a REST API for the HITL pipeline workflow:
- Create sessions with requirements + model config
- Run phases individually with human review between each
- Edit artifacts and re-validate

Run with:
    uvicorn main:app --reload --port 8000
"""

import logging

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Load environment variables before any LangChain/DB imports
load_dotenv()

from api.routes import health, sessions, phases  # noqa: E402
from db.database import Base, engine  # noqa: E402

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    application = FastAPI(
        title="DDD Pipeline API",
        description=(
            "AI-Assisted Domain-Driven Design artifact generation pipeline. "
            "Supports phase-by-phase execution with human review."
        ),
        version="0.1.0",
    )

    # CORS — allow frontend dev server and Vercel deployments
    application.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:3000",
            "http://localhost:3001",
            "http://localhost:5173",
        ],
        allow_origin_regex=r"https://.*\.vercel\.app",
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register routes
    application.include_router(health.router, prefix="/api")
    application.include_router(sessions.router, prefix="/api")
    application.include_router(phases.router, prefix="/api")

    @application.on_event("startup")
    def on_startup() -> None:
        """Create database tables on startup."""
        # Import models so Base.metadata knows about them
        import db.models  # noqa: F401
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created/verified")

    return application


app = create_app()
