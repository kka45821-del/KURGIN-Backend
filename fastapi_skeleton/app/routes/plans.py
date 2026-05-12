from __future__ import annotations

from fastapi import APIRouter

from ..db import list_plans
from ..models import PlanPublic

router = APIRouter()


@router.get("", response_model=list[PlanPublic])
def get_plans():
    return [PlanPublic(**plan) for plan in list_plans()]
