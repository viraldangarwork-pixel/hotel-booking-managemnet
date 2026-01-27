"""User schemas."""

from typing import Optional
from pydantic import EmailStr, Field

from .base import BaseSchema, IDSchema
from app.models.user import UserRole


class UserBase(BaseSchema):
    """Base user schema."""

    email: EmailStr
    full_name: str = Field(..., min_length=1, max_length=255)
    phone: Optional[str] = None
    role: UserRole = UserRole.STAFF
    hotel_id: Optional[int] = None


class UserCreate(UserBase):
    """Schema for creating a user."""

    password: str = Field(..., min_length=8)


class UserUpdate(BaseSchema):
    """Schema for updating a user."""

    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(None, min_length=1, max_length=255)
    phone: Optional[str] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None
    hotel_id: Optional[int] = None
    password: Optional[str] = Field(None, min_length=8)


class UserResponse(IDSchema):
    """Schema for user response."""

    email: EmailStr
    full_name: str
    phone: Optional[str] = None
    role: UserRole
    is_active: bool
    is_superuser: bool
    hotel_id: Optional[int] = None


class UserLogin(BaseSchema):
    """Schema for user login."""

    email: EmailStr
    password: str


class Token(BaseSchema):
    """Schema for JWT token response."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenPayload(BaseSchema):
    """Schema for token payload."""

    sub: Optional[str] = None
    exp: Optional[int] = None
    type: Optional[str] = None
