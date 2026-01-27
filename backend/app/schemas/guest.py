"""Guest schemas."""

from typing import Optional, List, Dict, Any
from datetime import date
from pydantic import Field, EmailStr

from .base import BaseSchema, IDSchema


class GuestBase(BaseSchema):
    """Base guest schema."""

    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    phone: str = Field(..., max_length=20)
    whatsapp_number: Optional[str] = Field(None, max_length=20)


class GuestCreate(GuestBase):
    """Schema for creating a guest."""

    hotel_id: int
    id_type: Optional[str] = None
    id_number: Optional[str] = None
    nationality: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    postal_code: Optional[str] = None
    date_of_birth: Optional[date] = None
    preferences: Dict[str, Any] = {}
    notes: Optional[str] = None
    tags: List[str] = []


class GuestUpdate(BaseSchema):
    """Schema for updating a guest."""

    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=20)
    whatsapp_number: Optional[str] = Field(None, max_length=20)
    id_type: Optional[str] = None
    id_number: Optional[str] = None
    nationality: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    postal_code: Optional[str] = None
    date_of_birth: Optional[date] = None
    is_vip: Optional[bool] = None
    is_blacklisted: Optional[bool] = None
    preferences: Optional[Dict[str, Any]] = None
    notes: Optional[str] = None
    tags: Optional[List[str]] = None


class GuestResponse(IDSchema):
    """Schema for guest response."""

    hotel_id: int
    first_name: str
    last_name: str
    email: Optional[str] = None
    phone: str
    whatsapp_number: Optional[str] = None
    id_type: Optional[str] = None
    id_number: Optional[str] = None
    nationality: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    postal_code: Optional[str] = None
    date_of_birth: Optional[date] = None
    is_vip: bool
    is_blacklisted: bool
    preferences: Dict[str, Any]
    notes: Optional[str] = None
    tags: List[str]
    total_stays: int
    total_spent: int
    last_visit: Optional[date] = None

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"
