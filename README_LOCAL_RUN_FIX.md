# KURGIN Backend Local Run Fix V1

## What this patch fixes

The original `fastapi_skeleton/requirements.txt` used:

```txt
psycopg[binary]==3.2.1
```

That pin fails on Python 3.13 because the matching `psycopg-binary` wheel is not available for that interpreter.

This patch changes it to:

```txt
psycopg[binary]>=3.2.13,<3.4
```

It also adds:

```txt
fastapi_skeleton/requirements-dev.txt
fastapi_skeleton/tools/local_smoke_test.py
```

`requirements-dev.txt` includes `httpx`, which is needed by FastAPI/Starlette `TestClient` for local smoke tests.

## How to apply

Upload the content of this patch to `KURGIN-Backend`, preserving paths:

```txt
fastapi_skeleton/requirements.txt
fastapi_skeleton/requirements-dev.txt
fastapi_skeleton/tools/local_smoke_test.py
README_LOCAL_RUN_FIX.md
```

## Local test

From `fastapi_skeleton`:

```bash
python -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements-dev.txt
python tools/local_smoke_test.py
uvicorn app.main:app --reload
```

Then open:

```txt
http://127.0.0.1:8000/health
```

Expected:

```json
{"status":"ok","service":"kurgin-backend"}
```
