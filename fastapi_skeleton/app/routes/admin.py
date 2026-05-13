from fastapi import APIRouter, Depends, HTTPException, status

from ..db import decide_role_request, list_audit_logs, list_role_requests
from ..security import require_admin

router = APIRouter()


@router.get("/audit")
def audit_log(user: dict = Depends(require_admin)):
    return list_audit_logs()


@router.get("/role-requests")
def role_requests(status_filter: str | None = None, user: dict = Depends(require_admin)):
    return {"items": list_role_requests(status_filter)}


@router.post("/role-requests/{request_id}/approve")
def approve_role_request(request_id: str, user: dict = Depends(require_admin)):
    try:
        return decide_role_request(request_id, "approved", admin_user_id=user["id"])
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.post("/role-requests/{request_id}/reject")
def reject_role_request(request_id: str, user: dict = Depends(require_admin)):
    try:
        return decide_role_request(request_id, "rejected", admin_user_id=user["id"])
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
