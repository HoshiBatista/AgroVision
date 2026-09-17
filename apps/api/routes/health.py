"""Health and readiness endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Request, Response

from agrovision import __version__
from agrovision.presentation.schemas import HealthResponse, ReadyResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    """Return process health."""
    return HealthResponse(status="ok", version=__version__)


@router.get("/ready", response_model=ReadyResponse)
async def ready(request: Request, response: Response) -> ReadyResponse:
    """Return whether the model is loaded and the service can serve predictions."""
    loaded = getattr(request.app.state, "detector", None) is not None
    if not loaded:
        response.status_code = 503
    return ReadyResponse(ready=loaded, model_loaded=loaded)
