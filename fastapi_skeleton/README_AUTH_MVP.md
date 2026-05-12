# KURGIN Backend Auth MVP V1

This patch turns the existing FastAPI contract scaffold into a locally runnable
Auth MVP.

It implements:

- local SQLite database initialization;
- password hashing via passlib/bcrypt;
- JWT access tokens via python-jose;
- `/auth/register`;
- `/auth/login`;
- `/auth/me`;
- role/plan-based `/access/check`;
- server-side payment status contract;
- Workspace collection persistence for authorized professional roles;
- smoke tests.

## Important boundary

This is **not production auth** yet.

Still required before real users:

- email verification;
- password reset;
- refresh token rotation;
- rate limiting;
- audit logging expansion;
- provider-backed payments;
- PostgreSQL migration;
- deployment secrets and environment hardening.

## Local run

From `fastapi_skeleton`:

```bat
py -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements-dev.txt
python tools/local_smoke_test.py
uvicorn app.main:app --reload
```

Open:

```txt
http://127.0.0.1:8000/health
http://127.0.0.1:8000/docs
```

Expected `/health`:

```json
{
  "status": "ok",
  "service": "kurgin-backend",
  "version": "1.1.0-auth-mvp",
  "environment": "development"
}
```

## Environment

Copy:

```txt
.env.example
```

to:

```txt
.env
```

for local overrides.

Never commit real `.env` files.
