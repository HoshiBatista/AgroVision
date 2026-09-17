"""Authentication endpoints: register, login, refresh, current user."""

from __future__ import annotations

from fastapi import APIRouter, status

from agrovision.presentation.presenters import user_to_response
from agrovision.presentation.schemas import (
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)
from apps.api.dependencies import AuthServiceDep, CurrentUserDep

router = APIRouter(prefix="/v1/auth", tags=["auth"])


def _tokens(access: str, refresh: str) -> TokenResponse:
    return TokenResponse(access_token=access, refresh_token=refresh)


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(payload: RegisterRequest, auth: AuthServiceDep) -> TokenResponse:
    """Register a new user and return an access/refresh token pair."""
    result = await auth.register(payload.email, payload.password)
    return _tokens(result.tokens.access_token, result.tokens.refresh_token)


@router.post("/login", response_model=TokenResponse)
async def login(payload: LoginRequest, auth: AuthServiceDep) -> TokenResponse:
    """Authenticate a user and return an access/refresh token pair."""
    result = await auth.login(payload.email, payload.password)
    return _tokens(result.tokens.access_token, result.tokens.refresh_token)


@router.post("/refresh", response_model=TokenResponse)
async def refresh(payload: RefreshRequest, auth: AuthServiceDep) -> TokenResponse:
    """Exchange a refresh token for a new token pair."""
    result = await auth.refresh(payload.refresh_token)
    return _tokens(result.tokens.access_token, result.tokens.refresh_token)


@router.get("/me", response_model=UserResponse)
async def me(user: CurrentUserDep) -> UserResponse:
    """Return the currently authenticated user."""
    return user_to_response(user)
