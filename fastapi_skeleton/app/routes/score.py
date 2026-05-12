from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from ..access_policy import evaluate_access
from ..models import ScoreRequest
from ..security import get_current_user

router = APIRouter()


@router.post("/calculate")
def calculate_score(payload: ScoreRequest, user: dict = Depends(get_current_user)):
    """Formula API boundary.

    This endpoint intentionally does not expose the proprietary formula. It only
    validates access and shape support. Private Formula Engine integration is
    the next backend milestone.
    """

    allowed, reason = evaluate_access(user, "single_report")
    if not allowed:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=reason)

    if payload.shape.upper() != "ROUND":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported shape in V1")

    return {
        "status": "FORMULA_API_NOT_CONNECTED",
        "message": "Private Formula Engine is not connected in Auth MVP V1.",
        "result": None,
    }
