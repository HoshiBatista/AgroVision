"""Dashboard aggregate endpoints: REST snapshot and WebSocket stream."""

from __future__ import annotations

import asyncio
import contextlib

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from agrovision.application.use_cases.dashboard import BuildDashboard
from agrovision.presentation.presenters import dashboard_to_snapshot
from agrovision.presentation.schemas import DashboardSnapshot
from apps.api.dependencies import StreamManagerDep

router = APIRouter(prefix="/v1/dashboard", tags=["dashboard"])

_PUSH_INTERVAL_S = 1.0


@router.get("", response_model=DashboardSnapshot)
async def dashboard_snapshot(manager: StreamManagerDep) -> DashboardSnapshot:
    """Return the current aggregate dashboard snapshot."""
    state = BuildDashboard(manager.bus).execute()
    return dashboard_to_snapshot(state)


@router.websocket("/ws")
async def dashboard_ws(websocket: WebSocket) -> None:
    """Push aggregate dashboard snapshots to the client roughly once per second."""
    await websocket.accept()
    manager = websocket.app.state.stream_manager
    use_case = BuildDashboard(manager.bus)
    try:
        while True:
            snapshot = dashboard_to_snapshot(use_case.execute())
            await websocket.send_json(snapshot.model_dump())
            await asyncio.sleep(_PUSH_INTERVAL_S)
    except WebSocketDisconnect:
        return
    finally:
        with contextlib.suppress(RuntimeError):
            await websocket.close()
