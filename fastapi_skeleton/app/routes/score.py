from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from ..security import get_current_user

router = APIRouter()


class ScoreRequest(BaseModel):
    shape: str
    crownAngle: float | None = None
    pavilionAngle: float | None = None
    tablePercent: float | None = None
    depthPercent: float | None = None
    crownPercent: float | None = None
    pavilionPercent: float | None = None
    girdlePercent: float | None = None


@router.post("/calculate")
def calculate_score(payload: ScoreRequest, user: dict = Depends(get_current_user)):
    # TODO: Call private Formula Engine. Do not expose formula in frontend.
    if payload.shape.upper() != "ROUND":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported shape in V1")
    return {
        "status": "STUB_ONLY",
        "message": "Formula engine not connected in scaffold",
        "result": None,
    }
