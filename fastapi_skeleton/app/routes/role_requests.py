from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from ..db import create_role_request, list_role_requests_for_user
from ..models import RoleRequestResponse
from ..security import get_current_user

router = APIRouter()

PROFESSIONAL_ROLES = {"jeweler", "designer", "gemologist", "partner"}


@router.get("/me", response_model=RoleRequestResponse)
def my_role_requests(user: dict = Depends(get_current_user)):
    return RoleRequestResponse(items=list_role_requests_for_user(user["id"]))


@router.post("/{requested_role}", status_code=status.HTTP_201_CREATED)
def request_role(requested_role: str, user: dict = Depends(get_current_user)):
    requested_role = requested_role.strip().lower()
    if requested_role not in PROFESSIONAL_ROLES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported professional role")
    if requested_role in user.get("roles", []):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Role already granted")

    try:
        role_request = create_role_request(user["id"], requested_role, reason="requested_from_profile")
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return role_request
