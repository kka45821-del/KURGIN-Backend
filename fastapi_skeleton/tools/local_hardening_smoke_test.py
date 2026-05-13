"""Local smoke test for KURGIN Auth + Workspace Hardening V1.

Run from fastapi_skeleton:
    python tools/local_hardening_smoke_test.py
"""

from __future__ import annotations

import time

from fastapi.testclient import TestClient

from app.main import app


def main() -> None:
    client = TestClient(app)
    suffix = str(int(time.time()))
    buyer_email = f"buyer-{suffix}@example.com"
    jeweler_email = f"jeweler-{suffix}@kurgin-test.com"
    password = "strongpassword123"

    checks = []

    health = client.get("/health")
    checks.append(("GET /health", health.status_code == 200 and health.json().get("version") == "1.1.0-auth-hardening"))

    buyer_register = client.post("/auth/register", json={"email": buyer_email, "password": password, "requested_role": "buyer"})
    checks.append(("POST /auth/register buyer", buyer_register.status_code == 201))
    buyer_token = buyer_register.json()["access_token"]

    me = client.get("/auth/me", headers={"Authorization": f"Bearer {buyer_token}"})
    checks.append(("GET /auth/me buyer", me.status_code == 200 and me.json()["roles"] == ["buyer"]))

    workspace_buyer = client.get("/workspace/collections", headers={"Authorization": f"Bearer {buyer_token}"})
    checks.append(("GET /workspace/collections buyer denied", workspace_buyer.status_code == 403))

    jeweler_register = client.post("/auth/register", json={"email": jeweler_email, "password": password, "requested_role": "jeweler"})
    checks.append(("POST /auth/register jeweler pending", jeweler_register.status_code == 201))
    jeweler_data = jeweler_register.json()
    checks.append(("jeweler role pending not granted", "jeweler" not in jeweler_data["user"]["roles"] and "jeweler" in jeweler_data["user"]["pending_roles"]))

    # Refresh token cookie is set by register/login and can be rotated.
    refresh = client.post("/auth/refresh")
    checks.append(("POST /auth/refresh", refresh.status_code == 200 and "access_token" in refresh.json()))

    role_requests = client.get("/role-requests/me", headers={"Authorization": f"Bearer {jeweler_data['access_token']}"})
    checks.append(("GET /role-requests/me", role_requests.status_code == 200 and role_requests.json()["items"]))

    for name, passed in checks:
        print(f"{name}: {'OK' if passed else 'FAIL'}")
        if not passed:
            raise SystemExit(1)

    print("KURGIN Auth + Workspace Hardening smoke test passed.")


if __name__ == "__main__":
    main()
