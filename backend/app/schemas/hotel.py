"""Hotel schemas."""

from typing import Optional, List
from pydantic import Field, EmailStr

from .base import BaseSchema, IDSchema


class HotelBase(BaseSchema):
    """Base hotel schema."""

    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    address: str
    city: str = Field(..., max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    country: str = Field(..., max_length=100)
    postal_code: Optional[str] = Field(None, max_length=20)
    phone: Optional[str] = Field(None, max_length=20)
    email: Optional[EmailStr] = None
    website: Optional[str] = None


class HotelCreate(HotelBase):
    """Schema for creating a hotel."""

    total_floors: int = Field(default=1, ge=1)
    amenities: List[str] = []
    check_in_time: str = "14:00"
    check_out_time: str = "11:00"
    tax_rate: int = Field(default=18, ge=0, le=100)
    gst_number: Optional[str] = None
    logo_url: Optional[str] = None
    primary_color: str = "#2563eb"


class HotelUpdate(BaseSchema):
    """Schema for updating a hotel."""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    country: Optional[str] = Field(None, max_length=100)
    postal_code: Optional[str] = Field(None, max_length=20)
    phone: Optional[str] = Field(None, max_length=20)
    email: Optional[EmailStr] = None
    website: Optional[str] = None
    total_floors: Optional[int] = Field(None, ge=1)
    amenities: Optional[List[str]] = None
    check_in_time: Optional[str] = None
    check_out_time: Optional[str] = None
    tax_rate: Optional[int] = Field(None, ge=0, le=100)
    gst_number: Optional[str] = None
    logo_url: Optional[str] = None
    primary_color: Optional[str] = None
    is_active: Optional[bool] = None


class HotelResponse(IDSchema):
    """Schema for hotel response."""

    name: str
    description: Optional[str] = None
    address: str
    city: str
    state: Optional[str] = None
    country: str
    postal_code: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    total_floors: int
    total_rooms: int
    amenities: List[str]
    check_in_time: str
    check_out_time: str
    tax_rate: int
    gst_number: Optional[str] = None
    logo_url: Optional[str] = None
    primary_color: str
    is_active: bool
