"""Room and RoomType schemas."""

from typing import Optional, List
from decimal import Decimal
from pydantic import Field

from .base import BaseSchema, IDSchema
from app.models.room import RoomStatus


class RoomTypeBase(BaseSchema):
    """Base room type schema."""

    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    base_price: Decimal = Field(..., ge=0)
    extra_bed_price: Decimal = Field(default=0, ge=0)
    max_occupancy: int = Field(default=2, ge=1)
    max_adults: int = Field(default=2, ge=1)
    max_children: int = Field(default=1, ge=0)
    bed_type: Optional[str] = None
    room_size: Optional[int] = None
    amenities: List[str] = []
    images: List[str] = []


class RoomTypeCreate(RoomTypeBase):
    """Schema for creating a room type."""

    hotel_id: int


class RoomTypeUpdate(BaseSchema):
    """Schema for updating a room type."""

    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    base_price: Optional[Decimal] = Field(None, ge=0)
    extra_bed_price: Optional[Decimal] = Field(None, ge=0)
    max_occupancy: Optional[int] = Field(None, ge=1)
    max_adults: Optional[int] = Field(None, ge=1)
    max_children: Optional[int] = Field(None, ge=0)
    bed_type: Optional[str] = None
    room_size: Optional[int] = None
    amenities: Optional[List[str]] = None
    images: Optional[List[str]] = None
    is_active: Optional[bool] = None


class RoomTypeResponse(IDSchema):
    """Schema for room type response."""

    hotel_id: int
    name: str
    description: Optional[str] = None
    base_price: Decimal
    extra_bed_price: Decimal
    max_occupancy: int
    max_adults: int
    max_children: int
    bed_type: Optional[str] = None
    room_size: Optional[int] = None
    amenities: List[str]
    images: List[str]
    is_active: bool


class RoomBase(BaseSchema):
    """Base room schema."""

    room_number: str = Field(..., min_length=1, max_length=20)
    floor: int = Field(default=1, ge=1)
    notes: Optional[str] = None
    custom_price: Optional[Decimal] = Field(None, ge=0)


class RoomCreate(RoomBase):
    """Schema for creating a room."""

    hotel_id: int
    room_type_id: int


class RoomUpdate(BaseSchema):
    """Schema for updating a room."""

    room_number: Optional[str] = Field(None, min_length=1, max_length=20)
    floor: Optional[int] = Field(None, ge=1)
    room_type_id: Optional[int] = None
    status: Optional[RoomStatus] = None
    notes: Optional[str] = None
    custom_price: Optional[Decimal] = Field(None, ge=0)
    is_active: Optional[bool] = None


class RoomResponse(IDSchema):
    """Schema for room response."""

    hotel_id: int
    room_type_id: int
    room_number: str
    floor: int
    status: RoomStatus
    notes: Optional[str] = None
    custom_price: Optional[Decimal] = None
    is_active: bool
    room_type: Optional[RoomTypeResponse] = None


class RoomAvailabilityQuery(BaseSchema):
    """Schema for room availability query."""

    check_in_date: str
    check_out_date: str
    adults: int = 1
    children: int = 0
    room_type_id: Optional[int] = None
