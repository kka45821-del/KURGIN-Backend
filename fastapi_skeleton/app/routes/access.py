from fastapi import APIRouter, Depends

from ..access_policy import evaluate_access
from ..models import AccessCheckRequest, AccessCheckResponse
from ..security import get_current_user

router = APIRouter()


@router.post("/check", response_model=AccessCheckResponse)
def check_access(payload: AccessCheckRequest, user: dict = Depends(get_current_user)):
    allowed, reason = evaluate_access(user, payload.resource)
    return AccessCheckResponse(
        resource=payload.resource,
        allowed=allowed,
        reason=reason,
        user_plan=user.get("plan", "free"),
        user_roles=user.get("roles", []),
        pending_roles=user.get("pending_roles", []),
    )
