from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from ..security import get_current_user

router = APIRouter()


class CollectionCreateRequest(BaseModel):
    title: str = Field(min_length=1, max_length=160)
    client_name: str | None = Field(default=None, max_length=160)
    notes: str | None = Field(default=None, max_length=2000)


@router.get("/collections")
def list_collections(user: dict = Depends(get_current_user)):
    # TODO: Query workspace_collections by current user id.
    return {"items": [], "owner": user["id"], "status": "db_not_connected_for_workspace"}


@router.post("/collections", status_code=201)
def create_collection(payload: CollectionCreateRequest, user: dict = Depends(get_current_user)):
    # TODO: Persist collection in database when Workspace storage is connected.
    return {
        "id": "mvp-not-persisted",
        "title": payload.title,
        "client_name": payload.client_name,
        "notes": payload.notes,
        "owner": user["id"],
        "status": "not_persisted_in_mvp",
    }
