# Backend Readiness Report — KURGIN

## Executive decision

Backend-auth is currently **not confirmed as production-ready**.

The frontend audit is complete for:

```txt
/score/ gateway
/diamonds/ → Analyzer
/workspace/ access page
```

The next blocker is backend readiness for authorization and private data.

## Confirmed frontend/app layers

```txt
KURGIN Website
→ public PWA / Vercel / static frontend

KURGIN Analyzer
→ Streamlit analytical application

KURGIN Admin
→ internal CMS/admin shell
```

## Missing production backend confirmations

```txt
Auth provider
User database
Role model
Session model
Password strategy
Protected API endpoints
Payment status storage
Workspace storage
Admin audit logs
Secrets management
Rate limiting
CORS policy
```

## Readiness matrix

| Area | Status | Notes |
|---|---|---|
| Public Website | Ready for current phase | Static public layer only |
| Score Gateway | Ready | Does not expose formula |
| Diamonds → Analyzer | Ready frontend-side | Passes stone params to Analyzer URL |
| Workspace V1 | Ready as landing/access page | No private data simulation |
| Analyzer | MVP ready | Local formula default, cloud-ready architecture |
| Admin | Skeleton/MVP | Needs real backend sync |
| Auth backend | Not ready | Must be implemented before real users |
| Database | Not ready | Schema proposed in this package |
| Payment backend | Not ready | Guest checkout must be persisted server-side |
| Formula API | Not ready production-side | Cloud API contract required |

## Go / No-go

### Allowed now

```txt
Public pages
Mock catalog data
Precomputed public score display
Analyzer link passing URL params
Workspace access page
Admin UI mock/skeleton
```

### Not allowed yet

```txt
Real login
Password collection
Admin credentials
Role-based access enforcement
B2B price exposure
Payment confirmation
Saved reports with personal data
Client cards
Private Workspace collections
```

## Required backend decision

KURGIN must choose one of these paths:

```txt
Path A: FastAPI + PostgreSQL
Path B: Supabase Auth + PostgreSQL
Path C: Yandex Cloud API + Managed PostgreSQL
```

Recommended current path:

```txt
FastAPI contract + PostgreSQL schema first.
Deployment target can remain flexible.
```
