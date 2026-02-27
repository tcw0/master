"""
FastAPI application factory for the DDD pipeline API.

Provides a REST API for the HITL (Human-in-the-Loop) pipeline workflow:
- Create sessions with requirements + model config
- Run phases individually with human review between each
- Edit artifacts and re-validate
- Track progress across all 5 DDD phases

Run with:
    uvicorn main:app --reload --port 8000
"""

import logging

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Load environment variables before LangChain imports (enables LangSmith tracing)
load_dotenv()

from api.routes import health, sessions, phases  # noqa: E402

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%H:%M:%S",
)


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

    # CORS — allow frontend dev server
    application.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:3000",  # Next.js dev server
            "http://localhost:5173",  # Vite dev server
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register routes
    application.include_router(health.router, prefix="/api")
    application.include_router(sessions.router, prefix="/api")
    application.include_router(phases.router, prefix="/api")

    return application


app = create_app()
