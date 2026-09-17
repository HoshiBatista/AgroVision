"""Contract tests for the authentication endpoints (fake repository, no DB)."""

from __future__ import annotations

from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from apps.api.dependencies import get_user_repository
from apps.api.main import create_app
from tests.fakes import FakeDetector, FakeUserRepository


@pytest.fixture
def client() -> Iterator[TestClient]:
    app = create_app(detector=FakeDetector())
    users = FakeUserRepository()
    app.dependency_overrides[get_user_repository] = lambda: users
    with TestClient(app) as test_client:
        yield test_client


def test_register_login_me_flow(client: TestClient) -> None:
    register = client.post(
        "/v1/auth/register", json={"email": "farmer@example.com", "password": "password123"}
    )
    assert register.status_code == 201
    access = register.json()["access_token"]

    me = client.get("/v1/auth/me", headers={"Authorization": f"Bearer {access}"})
    assert me.status_code == 200
    assert me.json()["email"] == "farmer@example.com"
    assert me.json()["role"] == "operator"


def test_login_after_register(client: TestClient) -> None:
    client.post("/v1/auth/register", json={"email": "a@b.com", "password": "password123"})
    login = client.post("/v1/auth/login", json={"email": "a@b.com", "password": "password123"})
    assert login.status_code == 200
    assert login.json()["access_token"]


def test_me_requires_token(client: TestClient) -> None:
    response = client.get("/v1/auth/me")
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "unauthorized"


def test_login_rejects_bad_credentials(client: TestClient) -> None:
    client.post("/v1/auth/register", json={"email": "a@b.com", "password": "password123"})
    response = client.post("/v1/auth/login", json={"email": "a@b.com", "password": "nope-nope-1"})
    assert response.status_code == 401


def test_duplicate_registration_conflicts(client: TestClient) -> None:
    client.post("/v1/auth/register", json={"email": "a@b.com", "password": "password123"})
    again = client.post("/v1/auth/register", json={"email": "a@b.com", "password": "password123"})
    assert again.status_code == 409
    assert again.json()["error"]["code"] == "conflict"
