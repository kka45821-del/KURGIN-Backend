from fastapi import APIRouter, Depends, HTTPException, status

from ..access_policy import evaluate_access
from ..db import create_collection, list_collections
from ..models import CollectionCreateRequest, CollectionListResponse, CollectionPublic
from ..security import get_current_user

router = APIRouter()


def require_workspace_access(user: dict) -> None:
    allowed, reason = evaluate_access(user, "workspace")
    if not allowed:
        pending = user.get("pending_roles", [])
        detail = "Workspace access requires confirmed professional role."
        if pending:
            detail = f"Role request pending: {', '.join(pending)}"
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail={"code": reason, "message": detail})


@router.get("/collections", response_model=CollectionListResponse)
def get_collections(user: dict = Depends(get_current_user)):
    require_workspace_access(user)
    return CollectionListResponse(
        items=[CollectionPublic(**item) for item in list_collections(user["id"])],
        owner=user["id"],
        status="ok",
    )


@router.post("/collections", status_code=201, response_model=CollectionPublic)
def post_collection(payload: CollectionCreateRequest, user: dict = Depends(get_current_user)):
    require_workspace_access(user)
    return CollectionPublic(**create_collection(
        owner_user_id=user["id"],
        title=payload.title,
        client_name=payload.client_name,
        notes=payload.notes,
    ))
