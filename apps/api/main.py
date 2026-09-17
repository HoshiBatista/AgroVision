"""FastAPI application composition root."""

from __future__ import annotations

import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from agrovision import __version__
from agrovision.application.ports import DetectorPort
from agrovision.config import Settings, get_settings
from agrovision.infrastructure.db.engine import create_engine, create_session_factory
from agrovision.infrastructure.ml.yolo_detector import build_detector
from agrovision.infrastructure.security.passwords import Argon2PasswordHasher
from agrovision.infrastructure.security.tokens import JwtTokenService
from agrovision.infrastructure.storage.local_storage import LocalStorage
from agrovision.infrastructure.streaming.manager import StreamManager, build_stream_manager
from apps.api.errors import register_error_handlers, request_id_middleware
from apps.api.routes import auth, dashboard, health, predictions, reports, streams


def create_app(
    settings: Settings | None = None,
    *,
    detector: DetectorPort | None = None,
    stream_manager: StreamManager | None = None,
) -> FastAPI:
    """Build the FastAPI app.

    Inject ``detector`` and/or ``stream_manager`` in tests to avoid loading model
    weights or starting background threads.
    """
    settings = settings or get_settings()
    logging.basicConfig(level=settings.log_level)

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        app.state.settings = settings
        resolved_detector = detector if detector is not None else build_detector(settings)
        app.state.detector = resolved_detector
        app.state.password_hasher = Argon2PasswordHasher()
        app.state.token_service = JwtTokenService(settings)
        engine = create_engine(settings)
        app.state.engine = engine
        app.state.session_factory = create_session_factory(engine)

        if stream_manager is not None:
            manager = stream_manager
        else:
            manager = build_stream_manager(settings, resolved_detector)
            manager.start()
        app.state.stream_manager = manager

        try:
            yield
        finally:
            manager.stop()
            closer = getattr(resolved_detector, "close", None)
            if callable(closer):
                closer()
            await engine.dispose()

    # Hide interactive API docs and the OpenAPI schema outside development.
    docs_url = "/docs" if settings.is_development else None
    app = FastAPI(
        title="AgroVision API",
        version=__version__,
        description="Aerial sheep detection and counting.",
        lifespan=lifespan,
        docs_url=docs_url,
        redoc_url="/redoc" if settings.is_development else None,
        openapi_url="/openapi.json" if settings.is_development else None,
    )
    app.state.settings = settings
    storage = LocalStorage(settings.storage_root)
    settings.demo_artifacts_root.mkdir(parents=True, exist_ok=True)
    app.state.storage = storage

    # Never combine a wildcard origin with credentials; browsers reject it and it
    # would be unsafe. Fall back to no-credentials CORS if "*" is configured.
    origins = settings.cors_origins
    allow_credentials = "*" not in origins
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=allow_credentials,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.middleware("http")(request_id_middleware)
    register_error_handlers(app)

    app.include_router(health.router)
    app.include_router(auth.router)
    app.include_router(predictions.router)
    app.include_router(streams.router)
    app.include_router(dashboard.router)
    app.include_router(reports.router)
    app.mount("/media", StaticFiles(directory=str(storage.root)), name="media")
    app.mount(
        "/demo-media",
        StaticFiles(directory=str(settings.demo_artifacts_root)),
        name="demo-media",
    )
    return app


app = create_app()
