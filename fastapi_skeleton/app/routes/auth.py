from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from ..config import settings
from ..db import create_user, get_password_hash_by_email, get_user_by_email, public_user
from ..models import LoginRequest, RegisterRequest, TokenResponse, UserPublic
from ..security import create_access_token, get_current_user, hash_password, verify_password

router = APIRouter()


def token_response(user: dict) -> TokenResponse:
    token = create_access_token(user)
    return TokenResponse(
        access_token=token,
        expires_in=settings.access_token_expire_minutes * 60,
        user=UserPublic(**public_user(user)),
    )


@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=TokenResponse)
def register(payload: RegisterRequest):
    """Register a local MVP user and issue an access token.

    This is real local auth logic: password is hashed and stored, and the
    returned JWT is signed. It is still not production-ready until rate limits,
    email verification, refresh sessions, password reset and audit controls are
    implemented.
    """

    password_hash = hash_password(payload.password)
    try:
        user = create_user(payload.email, password_hash, payload.requested_role)
    except ValueError as exc:
        reason = str(exc)
        if reason == "email_already_registered":
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered") from exc
        if reason == "requested_role_not_allowed":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Requested role is not self-service") from exc
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Registration failed") from exc

    return token_response(user)


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest):
    user = get_user_by_email(payload.email)
    password_hash = get_password_hash_by_email(payload.email)

    if user is None or password_hash is None or not verify_password(payload.password, password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    if user.get("status") != "active":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is not active")

    return token_response(user)


@router.get("/me", response_model=UserPublic)
def me(user: dict = Depends(get_current_user)):
    return UserPublic(**user)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout():
    # Stateless access tokens cannot be revoked server-side in this MVP.
    # Production must add refresh_sessions and token rotation/revocation.
    return None
