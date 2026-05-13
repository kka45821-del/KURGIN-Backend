from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status

from ..config import settings
from ..db import (
    create_refresh_session,
    create_role_request,
    create_user,
    generate_refresh_token,
    get_active_refresh_session,
    get_user_by_email,
    get_user_by_id,
    revoke_refresh_session,
    rotate_refresh_session,
)
from ..models import LoginRequest, RegisterRequest, TokenResponse, UserPublic
from ..security import create_access_token, get_current_user, hash_password, token_expires_in_seconds, verify_password

router = APIRouter()

ALLOWED_REQUESTED_ROLES = {"buyer", "jeweler", "designer", "gemologist", "partner"}
PROFESSIONAL_ROLES = {"jeweler", "designer", "gemologist", "partner"}


def public_user(user: dict) -> UserPublic:
    return UserPublic(
        id=user["id"],
        email=user["email"],
        roles=user.get("roles", []),
        plan=user.get("plan", "free"),
        status=user.get("status", "active"),
        pending_roles=user.get("pending_roles", []),
        role_requests=user.get("role_requests", []),
    )


def token_response(user: dict) -> TokenResponse:
    return TokenResponse(
        access_token=create_access_token(user),
        expires_in=token_expires_in_seconds(),
        user=public_user(user),
    )


def set_refresh_cookie(response: Response, refresh_token: str) -> None:
    response.set_cookie(
        key=settings.refresh_token_cookie_name,
        value=refresh_token,
        max_age=settings.refresh_token_expire_days * 24 * 60 * 60,
        httponly=True,
        secure=settings.refresh_cookie_secure,
        samesite=settings.refresh_cookie_samesite,
        path="/auth",
    )


def clear_refresh_cookie(response: Response) -> None:
    response.delete_cookie(
        key=settings.refresh_token_cookie_name,
        path="/auth",
        secure=settings.refresh_cookie_secure,
        samesite=settings.refresh_cookie_samesite,
    )


def start_refresh_session(response: Response, user: dict) -> None:
    refresh_token = generate_refresh_token()
    create_refresh_session(user["id"], refresh_token)
    set_refresh_cookie(response, refresh_token)


@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=TokenResponse)
def register(payload: RegisterRequest, response: Response):
    email = payload.email.strip().lower()
    requested_role = payload.requested_role.strip().lower()

    if requested_role not in ALLOWED_REQUESTED_ROLES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported requested role")
    if get_user_by_email(email):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User already exists")

    roles = ["buyer"]
    if requested_role in PROFESSIONAL_ROLES and settings.allow_self_assign_professional_roles:
        roles.append(requested_role)

    user = create_user(email=email, password_hash=hash_password(payload.password), roles=roles, plan="free")

    if requested_role in PROFESSIONAL_ROLES and requested_role not in user.get("roles", []):
        create_role_request(user["id"], requested_role, reason="requested_during_public_registration")
        user = get_user_by_id(user["id"]) or user

    start_refresh_session(response, user)
    return token_response(user)


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, response: Response):
    user = get_user_by_email(payload.email)
    if user is None or not verify_password(payload.password, user["password_hash"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    if user.get("status") != "active":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is not active")

    start_refresh_session(response, user)
    return token_response(user)


@router.post("/refresh", response_model=TokenResponse)
def refresh(request: Request, response: Response):
    raw_token = request.cookies.get(settings.refresh_token_cookie_name)
    if not raw_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh session not found")

    session = get_active_refresh_session(raw_token)
    if not session:
        clear_refresh_cookie(response)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh session expired or revoked")

    new_token = generate_refresh_token()
    rotated = rotate_refresh_session(raw_token, new_token)
    if rotated is None:
        clear_refresh_cookie(response)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh rotation failed")

    user = get_user_by_id(rotated["user_id"])
    if user is None or user.get("status") != "active":
        clear_refresh_cookie(response)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found or inactive")

    set_refresh_cookie(response, new_token)
    return token_response(user)


@router.get("/me", response_model=UserPublic)
def me(user: dict = Depends(get_current_user)):
    return public_user(user)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(request: Request, response: Response):
    raw_token = request.cookies.get(settings.refresh_token_cookie_name)
    if raw_token:
        revoke_refresh_session(raw_token)
    clear_refresh_cookie(response)
    return None
