from fastapi import APIRouter

from ..db import list_plans

router = APIRouter()


@router.get("")
def plans():
    # DB-backed local MVP. Production values should be synced from Admin.
    return [
        {
            "code": plan["id"],
            "title": plan["name"],
            "price_minor": plan["price_minor"],
            "currency": plan["currency"],
        }
        for plan in list_plans()
    ]
