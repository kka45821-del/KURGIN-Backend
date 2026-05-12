from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, EmailStr, Field


class UserPublic(BaseModel):
    id: str
    email: EmailStr
    roles: List[str]
    plan: str
    status: str = "active"


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=10, max_length=256)
    requested_role: str = "buyer"


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=256)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserPublic


class AccessCheckRequest(BaseModel):
    resource: str
    context: Dict[str, Any] = Field(default_factory=dict)


class AccessCheckResponse(BaseModel):
    resource: str
    allowed: bool
    reason: str
    roles: List[str]
    plan: str


class PlanPublic(BaseModel):
    id: str
    name: str
    price_minor: int
    currency: str
    features: List[str]


class PaymentCheckoutRequest(BaseModel):
    plan_id: str
    guest_email: Optional[EmailStr] = None


class PaymentStatusResponse(BaseModel):
    id: str
    status: str
    provider: str
    plan_id: str
    amount_minor: int
    currency: str
    checkout_url: Optional[str] = None
    message: str


class CollectionCreateRequest(BaseModel):
    title: str = Field(min_length=1, max_length=160)
    client_name: Optional[str] = Field(default=None, max_length=160)
    notes: Optional[str] = Field(default=None, max_length=2000)


class CollectionPublic(BaseModel):
    id: str
    title: str
    client_name: Optional[str] = None
    notes: Optional[str] = None
    owner_user_id: str
    status: str = "draft"


class ScoreRequest(BaseModel):
    shape: str
    crownAngle: Optional[float] = None
    pavilionAngle: Optional[float] = None
    tablePercent: Optional[float] = None
    depthPercent: Optional[float] = None
    crownPercent: Optional[float] = None
    pavilionPercent: Optional[float] = None
    girdlePercent: Optional[float] = None
