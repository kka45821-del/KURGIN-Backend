from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from ..db import create_payment, get_payment
from ..models import PaymentCheckoutRequest, PaymentStatusResponse
from ..security import get_optional_current_user

router = APIRouter()


@router.post("/checkout", status_code=status.HTTP_201_CREATED, response_model=PaymentStatusResponse)
def create_checkout(payload: PaymentCheckoutRequest, user: dict | None = Depends(get_optional_current_user)):
    """Create a payment contract record.

    This does not connect a real payment provider. It creates a server-side
    payment status object so frontend/Analyzer/Admin can integrate safely later.
    """

    try:
        payment = create_payment(
            plan_id=payload.plan_id,
            guest_email=str(payload.guest_email) if payload.guest_email else None,
            user_id=user["id"] if user else None,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plan not found") from exc

    return PaymentStatusResponse(
        id=payment["id"],
        status=payment["status"],
        provider=payment["provider"],
        plan_id=payment["plan_id"],
        amount_minor=payment["amount_minor"],
        currency=payment["currency"],
        checkout_url=None,
        message="Payment provider is not connected. This is a backend contract record only.",
    )


@router.get("/{payment_id}", response_model=PaymentStatusResponse)
def get_payment_status(payment_id: str):
    payment = get_payment(payment_id)
    if payment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment not found")

    return PaymentStatusResponse(
        id=payment["id"],
        status=payment["status"],
        provider=payment["provider"],
        plan_id=payment["plan_id"],
        amount_minor=payment["amount_minor"],
        currency=payment["currency"],
        checkout_url=None,
        message="Payment status is stored server-side. Real provider sync is not connected in MVP.",
    )
