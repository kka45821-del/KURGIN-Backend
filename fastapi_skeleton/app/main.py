from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .db import init_db
from .routes import access, admin, auth, payments, plans, role_requests, score, workspace


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title=settings.app_name,
    version=settings.api_version,
    description="KURGIN Backend Auth + Workspace Hardening V1.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "kurgin-backend",
        "version": settings.api_version,
        "environment": settings.environment,
    }


app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(access.router, prefix="/access", tags=["access"])
app.include_router(role_requests.router, prefix="/role-requests", tags=["role-requests"])
app.include_router(plans.router, prefix="/plans", tags=["plans"])
app.include_router(payments.router, prefix="/payments", tags=["payments"])
app.include_router(score.router, prefix="/score", tags=["score"])
app.include_router(workspace.router, prefix="/workspace", tags=["workspace"])
app.include_router(admin.router, prefix="/admin", tags=["admin"])
