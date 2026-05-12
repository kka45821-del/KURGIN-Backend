from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from ..access_policy import evaluate_access
from ..db import create_collection, list_collections
from ..models import CollectionCreateRequest, CollectionPublic
from ..security import get_current_user

router = APIRouter()


def require_workspace_access(user: dict) -> None:
    allowed, reason = evaluate_access(user, "workspace")
    if not allowed:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=reason)


@router.get("/collections", response_model=list[CollectionPublic])
def get_collections(user: dict = Depends(get_current_user)):
    require_workspace_access(user)
    return [CollectionPublic(**item) for item in list_collections(user["id"])]


@router.post("/collections", status_code=status.HTTP_201_CREATED, response_model=CollectionPublic)
def post_collection(payload: CollectionCreateRequest, user: dict = Depends(get_current_user)):
    require_workspace_access(user)
    item = create_collection(
        owner_user_id=user["id"],
        title=payload.title,
        client_name=payload.client_name,
        notes=payload.notes,
    )
    return CollectionPublic(**item)
