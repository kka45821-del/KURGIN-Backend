"""Local smoke test for KURGIN Backend Auth MVP V1.

Run from fastapi_skeleton:
    python tools/local_smoke_test.py
"""

from __future__ import annotations

import os
import uuid
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

# Configure a deterministic local test DB before importing the app.
os.environ.setdefault("KURGIN_ENVIRONMENT", "development")
os.environ.setdefault("KURGIN_DATABASE_URL", "sqlite:///./data/kurgin_smoke_test.db")
os.environ.setdefault("KURGIN_JWT_SECRET", "local-smoke-test-secret-change-me-32chars")

from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402


def expect(response, status_code: int, label: str):
    ok = response.status_code == status_code
    print(f"{label}: {response.status_code} expected {status_code} {'OK' if ok else 'FAIL'}")
    if response.headers.get("content-type", "").startswith("application/json"):
        print(response.json())
    if not ok:
        raise AssertionError(f"{label} failed")


def main() -> None:
    Path("data").mkdir(exist_ok=True)
    with TestClient(app) as client:
        return run_checks(client)


def run_checks(client: TestClient) -> None:
    email = f"qa-{uuid.uuid4().hex[:8]}@example.com"
    password = "strongpassword123"

    expect(client.get("/health"), 200, "GET /health")
    expect(client.get("/docs"), 200, "GET /docs")

    register = client.post(
        "/auth/register",
        json={"email": email, "password": password, "requested_role": "jeweler"},
    )
    expect(register, 201, "POST /auth/register")
    token = register.json()["access_token"]

    duplicate = client.post(
        "/auth/register",
        json={"email": email, "password": password, "requested_role": "jeweler"},
    )
    expect(duplicate, 409, "POST /auth/register duplicate")

    login = client.post("/auth/login", json={"email": email, "password": password})
    expect(login, 200, "POST /auth/login")
    token = login.json()["access_token"]

    auth_headers = {"Authorization": f"Bearer {token}"}
    me = client.get("/auth/me", headers=auth_headers)
    expect(me, 200, "GET /auth/me")
    assert "jeweler" in me.json()["roles"]

    expect(
        client.post("/access/check", json={"resource": "single_report", "context": {}}),
        401,
        "POST /access/check no auth",
    )

    workspace_access = client.post(
        "/access/check",
        headers=auth_headers,
        json={"resource": "workspace", "context": {}},
    )
    expect(workspace_access, 200, "POST /access/check workspace")
    assert workspace_access.json()["allowed"] is True

    single_access = client.post(
        "/access/check",
        headers=auth_headers,
        json={"resource": "single_report", "context": {}},
    )
    expect(single_access, 200, "POST /access/check single_report")
    assert single_access.json()["allowed"] is False

    expect(client.get("/plans"), 200, "GET /plans")

    checkout = client.post(
        "/payments/checkout",
        json={"plan_id": "single_report", "guest_email": "guest@example.com"},
    )
    expect(checkout, 201, "POST /payments/checkout guest")
    payment_id = checkout.json()["id"]
    expect(client.get(f"/payments/{payment_id}"), 200, "GET /payments/{id}")

    collection = client.post(
        "/workspace/collections",
        headers=auth_headers,
        json={"title": "Client shortlist", "client_name": "Demo Client", "notes": "Round 1ct options"},
    )
    expect(collection, 201, "POST /workspace/collections")
    expect(client.get("/workspace/collections", headers=auth_headers), 200, "GET /workspace/collections")

    expect(client.get("/admin/audit", headers=auth_headers), 403, "GET /admin/audit non-admin")

    print("KURGIN backend auth MVP smoke test passed.")


if __name__ == "__main__":
    main()
