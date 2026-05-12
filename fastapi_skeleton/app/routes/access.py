from fastapi import APIRouter, Depends
from pydantic import BaseModel

from ..security import get_current_user

router = APIRouter()


class AccessCheckRequest(BaseModel):
    resource: str
    context: dict = {}


@router.post("/check")
def check_access(payload: AccessCheckRequest, user: dict = Depends(get_current_user)):
    # TODO: Replace with DB-backed role/plan matrix.
    roles = set(user.get("roles", []))
    plan = user.get("plan")
    allowed = False
    reason = "not_allowed"

    if payload.resource in {"single_report"} and plan in {"single_report", "pro", "partner"}:
        allowed = True
        reason = "paid_plan"
    if payload.resource in {"professional_analytics", "workspace"} and (plan in {"pro", "partner"} or roles & {"jeweler", "partner", "admin"}):
        allowed = True
        reason = "professional_access"
    if payload.resource.startswith("admin") or payload.resource == "admin":
        allowed = "admin" in roles
        reason = "admin_role" if allowed else "admin_role_required"

    return {"resource": payload.resource, "allowed": allowed, "reason": reason}
