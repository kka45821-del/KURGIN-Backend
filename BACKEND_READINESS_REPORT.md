# Backend Readiness Report — KURGIN

## Executive decision

KURGIN Backend Auth MVP V1 is now ready for local and Docker-based cloud readiness testing.

The backend is still **not production identity infrastructure** until PostgreSQL, refresh-token sessions, email verification, password reset, rate limiting, real payment sync, audit expansion and deployment secret management are completed.

## Confirmed completed layers

```txt
/score/ gateway
/diamonds/ → Analyzer URL parameter bridge
/workspace/ access page
Backend Auth MVP V1
Dockerfile
docker-compose.yml
GitHub Actions CI/deploy-readiness workflow
Frontend KurginAPI bridge
Workspace auth-aware UI script
```

## Current backend runtime

```txt
FastAPI
JWT access tokens
passlib/bcrypt password hashing
SQLite local MVP persistence
role/plan access policy
payment status contract only
workspace collections MVP
```

## Cloud deployment readiness

### Docker

`fastapi_skeleton/Dockerfile` uses `python:3.11-slim`, installs runtime dependencies, creates a non-root app user, exposes port 8000 and runs:

```bash
uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
```

### Local Docker Compose

`docker-compose.yml` runs the backend with persistent SQLite data volume:

```bash
docker compose up --build
```

Health check:

```txt
http://127.0.0.1:8000/health
```

### GitHub Actions

`.github/workflows/deploy.yml` checks:

```txt
ruff lint
local smoke test
Docker build
optional Render deploy hook
```

## SQLite to cloud / PostgreSQL plan

### Fastest first deploy with SQLite

Use SQLite only for a temporary private preview. Persist the SQLite file in a mounted platform volume.

Set:

```txt
KURGIN_DATABASE_URL=sqlite:////app/data/kurgin_auth_mvp.sqlite3
```

This is acceptable only for initial smoke tests and private demos.

### Recommended first public backend

Switch to PostgreSQL before accepting real users. The existing `database/schema_postgres.sql` is the contract baseline.

Required steps:

```txt
1. Create managed PostgreSQL database.
2. Run database/schema_postgres.sql.
3. Seed database/seed_roles_plans.sql.
4. Set KURGIN_DATABASE_URL to the provider PostgreSQL URL.
5. Replace SQLite db.py implementation with PostgreSQL adapter.
6. Re-run smoke tests against staging.
```

Until step 5 is implemented, PostgreSQL remains a contract target, not the active runtime.

## Required environment variables

```txt
KURGIN_ENVIRONMENT=production
KURGIN_DATABASE_URL=<sqlite preview url or postgres url>
KURGIN_JWT_SECRET=<strong secret from platform env>
KURGIN_ALLOWED_ORIGINS=https://kurgin-website.vercel.app,https://cvdrap.ru
```

Never commit `.env` or real secrets.

## Go / No-go

### Allowed now

```txt
Private deploy preview
Health check
Swagger review
Frontend bridge integration
Auth smoke tests
Payment status contract testing
Workspace role UI testing
```

### Not allowed yet

```txt
Real payments
Real B2B price exposure
Production customer auth
Password reset promises
Email verification promises
Permanent customer report storage
```

## Next priority

```txt
Deploy private backend preview → connect KurginAPI baseURL → test Website ↔ Backend auth bridge.
```
