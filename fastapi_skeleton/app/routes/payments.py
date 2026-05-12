from fastapi import APIRouter, Depends, HTTPException, status

from ..db import create_payment_contract, get_payment
from ..models import PaymentCheckoutRequest, PaymentStatusResponse
from ..security import bearer, decode_access_token

router = APIRouter()


def optional_user_id(credentials=Depends(bearer)) -> str | None:
    if credentials is None:
        return None
    try:
        return str(decode_access_token(credentials.credentials).get("sub"))
    except Exception:
        return None


@router.post("/checkout", response_model=PaymentStatusResponse, status_code=status.HTTP_201_CREATED)
def create_checkout(payload: PaymentCheckoutRequest, user_id: str | None = Depends(optional_user_id)):
    try:
        payment = create_payment_contract(payload.plan_id, str(payload.guest_email) if payload.guest_email else None, user_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return PaymentStatusResponse(**payment)


@router.get("/status/{payment_id}", response_model=PaymentStatusResponse)
def payment_status(payment_id: str):
    payment = get_payment(payment_id)
    if payment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment not found")
    return PaymentStatusResponse(
        id=payment["id"],
        plan_id=payment["plan_id"],
        status=payment["status"],
        provider=payment["provider"],
        amount_minor=payment["amount_minor"],
        currency=payment["currency"],
        message="Payment provider is not connected in MVP. Status is persisted server-side.",
    )
