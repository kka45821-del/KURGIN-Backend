from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr, Field

router = APIRouter()


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=10)
    requested_role: str = "buyer"


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest):
    # TODO: Hash password, create user, assign default role, send verification if required.
    return {"status": "pending_backend", "email": payload.email, "roles": [payload.requested_role]}


@router.post("/login")
def login(payload: LoginRequest):
    # TODO: Validate credentials against database and issue short-lived access token.
    if payload.email.endswith("@example.invalid"):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    return {
        "access_token": "stub.access.token",
        "token_type": "bearer",
        "expires_in": 900,
        "user": {"id": "stub-user-id", "email": payload.email, "roles": ["buyer"], "plan": "free"},
    }


@router.get("/me")
def me():
    # TODO: Return current user from validated token.
    return {"id": "stub-user-id", "email": "stub@example.com", "roles": ["buyer"], "plan": "free"}


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout():
    # TODO: Revoke refresh token/session.
    return None
