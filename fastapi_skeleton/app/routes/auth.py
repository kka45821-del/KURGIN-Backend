from fastapi import APIRouter, Depends, HTTPException, status

from ..config import settings
from ..db import create_user, get_user_by_email
from ..models import LoginRequest, RegisterRequest, TokenResponse, UserPublic
from ..security import create_access_token, get_current_user, hash_password, token_expires_in_seconds, verify_password

router = APIRouter()

ALLOWED_REQUESTED_ROLES = {"buyer", "jeweler", "designer", "gemologist", "partner"}


def public_user(user: dict) -> UserPublic:
    return UserPublic(
        id=user["id"],
        email=user["email"],
        roles=user.get("roles", []),
        plan=user.get("plan", "free"),
        status=user.get("status", "active"),
    )


def token_response(user: dict) -> TokenResponse:
    return TokenResponse(
        access_token=create_access_token(user),
        expires_in=token_expires_in_seconds(),
        user=public_user(user),
    )


@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=TokenResponse)
def register(payload: RegisterRequest):
    email = payload.email.strip().lower()
    requested_role = payload.requested_role.strip().lower()
    if requested_role not in ALLOWED_REQUESTED_ROLES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported requested role")
    if get_user_by_email(email):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User already exists")

    # Safe default: users cannot grant themselves professional access.
    roles = ["buyer"]
    if requested_role != "buyer" and settings.allow_self_assign_professional_roles:
        roles.append(requested_role)

    user = create_user(email=email, password_hash=hash_password(payload.password), roles=roles, plan="free")
    return token_response(user)


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest):
    user = get_user_by_email(payload.email)
    if user is None or not verify_password(payload.password, user["password_hash"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    if user.get("status") != "active":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is not active")
    return token_response(user)


@router.get("/me", response_model=UserPublic)
def me(user: dict = Depends(get_current_user)):
    return public_user(user)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout():
    # MVP uses stateless access tokens. Production should revoke refresh sessions server-side.
    return None
