from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Annotated, Any, Dict, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from passlib.context import CryptContext

from .config import settings
from .db import get_user_by_id, public_user

bearer = HTTPBearer(auto_error=False)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash a password for storage.

    Never store raw passwords. This MVP uses passlib/bcrypt.
    Production should also add breach-password checks and rate limiting.
    """

    return pwd_context.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return pwd_context.verify(password, password_hash)


def create_access_token(user: Dict[str, Any]) -> str:
    now = datetime.now(timezone.utc)
    expires_at = now + timedelta(minutes=settings.access_token_expire_minutes)

    payload = {
        "iss": settings.jwt_issuer,
        "aud": settings.jwt_audience,
        "iat": int(now.timestamp()),
        "exp": int(expires_at.timestamp()),
        "sub": user["id"],
        "email": user["email"],
        "roles": list(user.get("roles", [])),
        "plan": user.get("plan", "free"),
        "typ": "access",
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> Dict[str, Any]:
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm],
            audience=settings.jwt_audience,
            issuer=settings.jwt_issuer,
        )
    except JWTError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token") from exc

    if payload.get("typ") != "access":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type")

    return payload


def get_optional_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)]
) -> Optional[Dict[str, Any]]:
    if credentials is None:
        return None

    payload = decode_access_token(credentials.credentials)
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token subject")

    user = get_user_by_id(str(user_id))
    if user is None or user.get("status") != "active":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found or inactive")

    return public_user(user)


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)]
) -> Dict[str, Any]:
    user = get_optional_current_user(credentials)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    return user


def require_admin(user: Annotated[Dict[str, Any], Depends(get_current_user)]) -> Dict[str, Any]:
    if "admin" not in user.get("roles", []):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin role required")
    return user
