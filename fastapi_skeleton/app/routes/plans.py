from fastapi import APIRouter

router = APIRouter()


@router.get("")
def list_plans():
    # TODO: Load from database/admin settings.
    return [
        {"code": "free", "title": "Free", "price_minor": 0, "currency": "RUB"},
        {"code": "single_report", "title": "Single Report", "price_minor": 9900, "currency": "RUB"},
        {"code": "pro", "title": "Professional", "price_minor": 49900, "currency": "RUB"},
        {"code": "partner", "title": "Partner", "price_minor": 149900, "currency": "RUB"},
    ]
