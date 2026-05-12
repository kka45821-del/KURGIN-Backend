"""Local smoke test for KURGIN Backend FastAPI skeleton.
Run from fastapi_skeleton:
    python tools/local_smoke_test.py
"""

from fastapi.testclient import TestClient

from app.main import app


def main() -> None:
    client = TestClient(app)

    checks = [
        ("GET /health", client.get("/health"), 200),
        ("GET /docs", client.get("/docs"), 200),
        (
            "POST /auth/register",
            client.post(
                "/auth/register",
                json={
                    "email": "qa@example.com",
                    "password": "strongpassword123",
                    "requested_role": "jeweler",
                },
            ),
            201,
        ),
        (
            "POST /auth/login",
            client.post(
                "/auth/login",
                json={"email": "qa@example.com", "password": "strongpassword123"},
            ),
            200,
        ),
        (
            "POST /access/check no auth",
            client.post("/access/check", json={"resource": "single_report", "context": {}}),
            401,
        ),
        (
            "POST /access/check stub auth",
            client.post(
                "/access/check",
                headers={"Authorization": "Bearer stub.access.token"},
                json={"resource": "single_report", "context": {}},
            ),
            200,
        ),
    ]

    failed = False
    for name, response, expected in checks:
        ok = response.status_code == expected
        failed = failed or not ok
        print(f"{name}: {response.status_code} expected {expected} {'OK' if ok else 'FAIL'}")
        if response.headers.get("content-type", "").startswith("application/json"):
            print(response.json())

    if failed:
        raise SystemExit(1)

    print("KURGIN backend skeleton smoke test passed.")


if __name__ == "__main__":
    main()
