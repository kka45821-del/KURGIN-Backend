from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Annotated, Any

import bcrypt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from passlib.context import CryptContext

from .config import settings
from .db import get_user_by_id

try:  # Preferred dependency from requirements.txt
    from jose import JWTError, jwt
except Exception:  # Local fallback for environments with PyJWT but without python-jose
    import jwt  # type: ignore
    from jwt import InvalidTokenError as JWTError  # type: ignore

bearer = HTTPBearer(auto_error=False)
_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def _bcrypt_bytes(password: str) -> bytes:
    data = password.encode("utf-8")
    if len(data) > 72:
        raise ValueError("Password is too long for bcrypt")
    return data


def hash_password(password: str) -> str:
    """Hash password with passlib/bcrypt and fallback to direct bcrypt.

    The fallback exists because some Python 3.13 environments combine passlib
    1.7.4 with a newer bcrypt backend that raises during backend detection.
    Requirements pin bcrypt to a passlib-compatible range, but this keeps local
    smoke tests resilient.
    """
    try:
        return _pwd_context.hash(password)
    except Exception:
        return bcrypt.hashpw(_bcrypt_bytes(password), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return _pwd_context.verify(password, password_hash)
    except Exception:
        return bcrypt.checkpw(_bcrypt_bytes(password), password_hash.encode("utf-8"))


def create_access_token(user: dict[str, Any]) -> str:
    now = datetime.now(timezone.utc)
    expires = now + timedelta(minutes=settings.access_token_expire_minutes)
    payload = {
        "sub": user["id"],
        "email": user["email"],
        "roles": user.get("roles", []),
        "plan": user.get("plan", "free"),
        "iss": settings.jwt_issuer,
        "aud": settings.jwt_audience,
        "iat": int(now.timestamp()),
        "exp": int(expires.timestamp()),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> dict[str, Any]:
    try:
        return jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm],
            audience=settings.jwt_audience,
            issuer=settings.jwt_issuer,
        )
    except JWTError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token") from exc


def token_expires_in_seconds() -> int:
    return settings.access_token_expire_minutes * 60


def get_current_user(credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)]) -> dict[str, Any]:
    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    payload = decode_access_token(credentials.credentials)
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token subject")
    user = get_user_by_id(str(user_id))
    if user is None or user.get("status") != "active":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found or inactive")
    return user


def require_admin(user: Annotated[dict, Depends(get_current_user)]) -> dict:
    if "admin" not in user.get("roles", []):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin role required")
    return user
