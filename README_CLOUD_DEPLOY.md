# KURGIN Backend Cloud Deploy Readiness V1

## Current target

The backend is deploy-ready as a Dockerized FastAPI MVP. It is still an Auth MVP, not production identity infrastructure.

## Local Docker run

From repository root:

```bash
docker compose up --build
```

Open:

```txt
http://127.0.0.1:8000/health
http://127.0.0.1:8000/docs
```

## Render

Use `render.yaml` or create a Web Service manually:

```txt
Environment: Docker
Root directory: fastapi_skeleton
Health check path: /health
```

Required env vars:

```txt
KURGIN_ENVIRONMENT=production
KURGIN_DATABASE_URL=<provider database url>
KURGIN_JWT_SECRET=<strong generated secret, never commit>
KURGIN_ALLOWED_ORIGINS=https://kurgin-website.vercel.app,https://cvdrap.ru
```

## Railway

Use `railway.json`. Set the same env vars in Railway Variables.

## GitHub Actions

`.github/workflows/deploy.yml` runs:

```txt
ruff check
local smoke test
Docker build
optional Render deploy hook
```

To enable Render deploy from GitHub Actions, add repository secret:

```txt
RENDER_DEPLOY_HOOK_URL
```

No secrets are included in this repository.
