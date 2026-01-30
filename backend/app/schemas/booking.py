"""Booking schemas."""

from typing import Optional, List, Dict, Any
from datetime import date, datetime
from decimal import Decimal
from pydantic import Field

from .base import BaseSchema, IDSchema
from .guest import GuestResponse
from .room import RoomResponse
from app.models.booking import BookingStatus, BookingSource


class BookingBase(BaseSchema):
    """Base booking schema."""

    check_in_date: date
    check_out_date: date
    adults: int = Field(default=1, ge=1)
    children: int = Field(default=0, ge=0)
    extra_beds: int = Field(default=0, ge=0)
    special_requests: Optional[str] = None


class BookingCreate(BookingBase):
    """Schema for creating a booking."""

    hotel_id: int
    room_id: int
    guest_id: int
    source: BookingSource = BookingSource.direct
    discount_code: Optional[str] = None


class BookingUpdate(BaseSchema):
    """Schema for updating a booking."""

    room_id: Optional[int] = None
    check_in_date: Optional[date] = None
    check_out_date: Optional[date] = None
    adults: Optional[int] = Field(None, ge=1)
    children: Optional[int] = Field(None, ge=0)
    extra_beds: Optional[int] = Field(None, ge=0)
    status: Optional[BookingStatus] = None
    special_requests: Optional[str] = None
    internal_notes: Optional[str] = None
    discount_code: Optional[str] = None
    additional_charges: Optional[List[Dict[str, Any]]] = None


class BookingCheckIn(BaseSchema):
    """Schema for check-in."""

    id_type: Optional[str] = None
    id_number: Optional[str] = None
    notes: Optional[str] = None


class BookingCheckOut(BaseSchema):
    """Schema for check-out."""

    additional_charges: Optional[List[Dict[str, Any]]] = None
    notes: Optional[str] = None


class BookingResponse(IDSchema):
    """Schema for booking response."""

    booking_ref: str
    hotel_id: int
    room_id: int
    guest_id: int
    check_in_date: date
    check_out_date: date
    actual_check_in: Optional[datetime] = None
    actual_check_out: Optional[datetime] = None
    adults: int
    children: int
    extra_beds: int
    status: BookingStatus
    source: BookingSource
    room_rate: Decimal
    extra_bed_charge: Decimal
    subtotal: Decimal
    tax_amount: Decimal
    discount_amount: Decimal
    total_amount: Decimal
    discount_code: Optional[str] = None
    discount_percent: int
    amount_paid: Decimal
    is_paid: bool
    special_requests: Optional[str] = None
    internal_notes: Optional[str] = None
    additional_charges: List[Dict[str, Any]]
    cancelled_at: Optional[datetime] = None
    cancellation_reason: Optional[str] = None

    # Related objects
    guest: Optional[GuestResponse] = None
    room: Optional[RoomResponse] = None


class BookingListResponse(BaseSchema):
    """Schema for booking list response."""

    items: List[BookingResponse]
    total: int
    page: int
    size: int
    pages: int
