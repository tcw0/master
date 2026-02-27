"""
Health check endpoint.
"""

from fastapi import APIRouter

from api.schemas import HealthResponse
from pipeline_config import PHASES

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Check API health and basic configuration."""
    return HealthResponse(
        status="ok",
        version="0.1.0",
        phases_available=len(PHASES),
    )
