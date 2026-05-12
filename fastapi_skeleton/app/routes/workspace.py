from fastapi import APIRouter, Depends
from pydantic import BaseModel

from ..security import get_current_user

router = APIRouter()


class CollectionCreateRequest(BaseModel):
    title: str
    client_name: str | None = None
    notes: str | None = None


@router.get("/collections")
def list_collections(user: dict = Depends(get_current_user)):
    # TODO: Query workspace_collections by current user id.
    return []


@router.post("/collections", status_code=201)
def create_collection(payload: CollectionCreateRequest, user: dict = Depends(get_current_user)):
    # TODO: Persist collection in database.
    return {"id": "stub-collection-id", "title": payload.title, "owner": user["id"]}
