from __future__ import annotations

from pydantic import BaseModel, EmailStr, Field


class RoleRequestPublic(BaseModel):
    id: str
    requested_role: str
    status: str
    created_at: str
    decided_at: str | None = None


class UserPublic(BaseModel):
    id: str
    email: EmailStr
    roles: list[str]
    plan: str
    status: str = "active"
    pending_roles: list[str] = Field(default_factory=list)
    role_requests: list[RoleRequestPublic] = Field(default_factory=list)


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=10, max_length=72)
    requested_role: str = "buyer"


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=72)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserPublic


class AccessCheckRequest(BaseModel):
    resource: str
    context: dict = Field(default_factory=dict)


class AccessCheckResponse(BaseModel):
    resource: str
    allowed: bool
    reason: str
    user_plan: str
    user_roles: list[str]
    pending_roles: list[str] = Field(default_factory=list)


class RoleRequestResponse(BaseModel):
    items: list[RoleRequestPublic]


class PaymentCheckoutRequest(BaseModel):
    plan_id: str
    guest_email: EmailStr | None = None


class PaymentStatusResponse(BaseModel):
    id: str
    plan_id: str
    status: str
    provider: str
    amount_minor: int
    currency: str
    message: str | None = None


class CollectionCreateRequest(BaseModel):
    title: str = Field(min_length=1, max_length=160)
    client_name: str | None = Field(default=None, max_length=160)
    notes: str | None = Field(default=None, max_length=2000)


class CollectionPublic(BaseModel):
    id: str
    owner_user_id: str
    title: str
    client_name: str | None = None
    notes: str | None = None
    status: str = "draft"


class CollectionListResponse(BaseModel):
    items: list[CollectionPublic]
    owner: str
    status: str = "ok"
