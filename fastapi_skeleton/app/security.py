from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

bearer = HTTPBearer(auto_error=False)


# NOTE: This is a scaffold. Replace with real JWT validation and database role lookup.
def get_current_user(credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)]):
    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    return {
        "id": "stub-user-id",
        "email": "stub@example.com",
        "roles": ["buyer"],
        "plan": "free",
    }


def require_admin(user: Annotated[dict, Depends(get_current_user)]):
    if "admin" not in user.get("roles", []):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin role required")
    return user
