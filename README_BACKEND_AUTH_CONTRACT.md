# KURGIN Backend Auth Contract V1

## Status

Current production status: **NOT READY FOR REAL AUTH DATA**.

The public website, Analyzer, and Admin shells are prepared for the next backend phase, but no production-ready authentication backend is confirmed yet.

This package defines the minimum backend contract required before KURGIN can safely accept:

- real user registration;
- login credentials;
- roles for jewelers / partners / admins;
- paid access state;
- saved Analyzer reports;
- Workspace collections;
- B2B prices;
- Admin-controlled settings.

## Do not do before backend is implemented

Do not store any of the following in public frontend code or public JSON:

- passwords;
- admin flags;
- B2B prices;
- API keys;
- payment status;
- user roles;
- private report history;
- personal client data.

## Recommended stack options

Option A — Fast MVP:

```txt
FastAPI + PostgreSQL + JWT access token + HttpOnly refresh cookie
```

Option B — Managed auth:

```txt
Supabase Auth + PostgreSQL + RLS + API layer
```

Option C — Yandex Cloud production path:

```txt
Yandex Cloud Functions / Serverless Containers
+ Managed PostgreSQL
+ Object Storage
+ API Gateway
```

## Minimum implementation order

```txt
1. Database schema
2. Auth endpoints
3. Role checks
4. Plan / access checks
5. Payment status contract
6. Analyzer report persistence
7. Workspace collections
8. Admin audit logs
9. Formula API integration
10. Index API integration
```

## Package structure

```txt
openapi/kurgin_backend_auth_openapi_v1.yaml
  API contract.

database/schema_postgres.sql
  PostgreSQL schema for users, roles, plans, payments, reports, workspace, audit logs.

database/seed_roles_plans.sql
  Initial roles and plans.

security/SECURITY_CHECKLIST.md
  Security readiness checklist.

security/ENVIRONMENT_VARIABLES.md
  Required env vars. No real secrets included.

fastapi_skeleton/
  Minimal implementation scaffold. Not production-ready until configured.

integration/
  Contracts for Website, Analyzer, Admin.

tests/smoke_test_examples.http
  Manual API smoke tests.

Final Report.txt
  Summary and decision status.
```
