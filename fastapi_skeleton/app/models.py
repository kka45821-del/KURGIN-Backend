from pydantic import BaseModel, EmailStr, Field


class UserPublic(BaseModel):
    id: str
    email: EmailStr
    roles: list[str]
    plan: str
    status: str = "active"


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
