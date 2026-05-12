"""Local smoke test for KURGIN Backend Auth MVP V1.
Run from fastapi_skeleton:
    python tools/local_smoke_test.py
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from uuid import uuid4

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Set local test env before importing app/settings.
os.environ.setdefault("LOCAL_DB_PATH", ".local/smoke_test.sqlite")
os.environ.setdefault("JWT_SECRET", "local-smoke-test-secret-change-me-32chars")
os.environ.setdefault("ALLOW_SELF_ASSIGN_PROFESSIONAL_ROLES", "true")

smoke_db = ROOT / os.environ["LOCAL_DB_PATH"]
if smoke_db.exists():
    smoke_db.unlink()

from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402


def assert_status(name: str, response, expected: int) -> None:
    ok = response.status_code == expected
    print(f"{name}: {response.status_code} expected {expected} {'OK' if ok else 'FAIL'}")
    if response.headers.get("content-type", "").startswith("application/json"):
        print(response.json())
    if not ok:
        raise AssertionError(f"{name}: expected {expected}, got {response.status_code}: {response.text}")


def main() -> None:
    suffix = uuid4().hex[:8]
    buyer_email = f"buyer-{suffix}@example.com"
    jeweler_email = f"jeweler-{suffix}@example.com"
    password = "strongpassword123"

    with TestClient(app) as client:
        assert_status("GET /health", client.get("/health"), 200)
        assert_status("GET /docs", client.get("/docs"), 200)
        assert_status("GET /auth/me no token", client.get("/auth/me"), 401)

        register = client.post(
            "/auth/register",
            json={"email": buyer_email, "password": password, "requested_role": "buyer"},
        )
        assert_status("POST /auth/register buyer", register, 201)

        duplicate = client.post(
            "/auth/register",
            json={"email": buyer_email, "password": password, "requested_role": "buyer"},
        )
        assert_status("POST /auth/register duplicate", duplicate, 409)

        bad_login = client.post("/auth/login", json={"email": buyer_email, "password": "wrongpassword"})
        assert_status("POST /auth/login bad password", bad_login, 401)

        login = client.post("/auth/login", json={"email": buyer_email, "password": password})
        assert_status("POST /auth/login buyer", login, 200)
        buyer_token = login.json()["access_token"]

        me = client.get("/auth/me", headers={"Authorization": f"Bearer {buyer_token}"})
        assert_status("GET /auth/me buyer", me, 200)

        no_auth_access = client.post("/access/check", json={"resource": "single_report", "context": {}})
        assert_status("POST /access/check no auth", no_auth_access, 401)

        free_single = client.post(
            "/access/check",
            headers={"Authorization": f"Bearer {buyer_token}"},
            json={"resource": "single_report", "context": {}},
        )
        assert_status("POST /access/check free single_report", free_single, 200)
        assert free_single.json()["allowed"] is False

        jeweler = client.post(
            "/auth/register",
            json={"email": jeweler_email, "password": password, "requested_role": "jeweler"},
        )
        assert_status("POST /auth/register jeweler", jeweler, 201)
        jeweler_token = jeweler.json()["access_token"]
        assert "jeweler" in jeweler.json()["user"]["roles"]

        workspace_access = client.post(
            "/access/check",
            headers={"Authorization": f"Bearer {jeweler_token}"},
            json={"resource": "workspace", "context": {}},
        )
        assert_status("POST /access/check jeweler workspace", workspace_access, 200)
        assert workspace_access.json()["allowed"] is True

        plans = client.get("/plans")
        assert_status("GET /plans", plans, 200)

        checkout = client.post("/payments/checkout", json={"plan_id": "single_report", "guest_email": "guest@example.com"})
        assert_status("POST /payments/checkout guest", checkout, 201)
        payment_id = checkout.json()["id"]
        payment_status = client.get(f"/payments/status/{payment_id}")
        assert_status("GET /payments/status/{id}", payment_status, 200)

        collections_before = client.get("/workspace/collections", headers={"Authorization": f"Bearer {jeweler_token}"})
        assert_status("GET /workspace/collections", collections_before, 200)

        collection = client.post(
            "/workspace/collections",
            headers={"Authorization": f"Bearer {jeweler_token}"},
            json={"title": "Client round diamonds", "client_name": "Demo Client", "notes": "MVP smoke test"},
        )
        assert_status("POST /workspace/collections", collection, 201)

        admin_forbidden = client.get("/admin/audit", headers={"Authorization": f"Bearer {buyer_token}"})
        assert_status("GET /admin/audit buyer forbidden", admin_forbidden, 403)

    print("KURGIN backend auth MVP smoke test passed.")


if __name__ == "__main__":
    main()
