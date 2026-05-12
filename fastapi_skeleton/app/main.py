from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routes import auth, access, plans, score, workspace, admin

app = FastAPI(
    title="KURGIN Backend API",
    version="1.0.0",
    description="Minimal scaffold for Backend Auth Contract V1."
)

# TODO: Replace wildcard origins with strict CORS from environment variables.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://kurgin-website.vercel.app", "https://cvdrap.ru", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

@app.get("/health")
def health():
    return {"status": "ok", "service": "kurgin-backend"}

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(access.router, prefix="/access", tags=["access"])
app.include_router(plans.router, prefix="/plans", tags=["plans"])
app.include_router(score.router, prefix="/score", tags=["score"])
app.include_router(workspace.router, prefix="/workspace", tags=["workspace"])
app.include_router(admin.router, prefix="/admin", tags=["admin"])
