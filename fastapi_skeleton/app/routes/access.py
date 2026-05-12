from fastapi import APIRouter, Depends

from ..models import AccessCheckRequest, AccessCheckResponse
from ..security import get_current_user

router = APIRouter()

PROFESSIONAL_ROLES = {"jeweler", "designer", "gemologist", "partner", "admin"}
PAID_PLANS = {"single_report", "pro", "partner"}
PRO_PLANS = {"pro", "partner"}


@router.post("/check", response_model=AccessCheckResponse)
def check_access(payload: AccessCheckRequest, user: dict = Depends(get_current_user)):
    roles = set(user.get("roles", []))
    plan = user.get("plan", "free")
    resource = payload.resource.strip().lower()

    allowed = False
    reason = "not_allowed"

    if resource in {"public", "catalog", "diamonds"}:
        allowed = True
        reason = "public_resource"
    elif resource in {"single_report", "score_single"}:
        allowed = plan in PAID_PLANS or bool(roles & PROFESSIONAL_ROLES)
        reason = "paid_or_professional" if allowed else "paid_plan_required"
    elif resource in {"professional_analytics", "workspace", "excel_batch"}:
        allowed = plan in PRO_PLANS or bool(roles & PROFESSIONAL_ROLES)
        reason = "professional_access" if allowed else "professional_access_required"
    elif resource == "admin" or resource.startswith("admin:"):
        allowed = "admin" in roles
        reason = "admin_role" if allowed else "admin_role_required"

    return AccessCheckResponse(
        resource=resource,
        allowed=allowed,
        reason=reason,
        user_plan=plan,
        user_roles=sorted(roles),
    )
