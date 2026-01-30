"""Booking model."""

from sqlalchemy import Column, String, Text, Integer, ForeignKey, Enum, Numeric, Date, DateTime, JSON, Boolean
from sqlalchemy.orm import relationship
import enum
from datetime import datetime

from .base import BaseModel


class BookingStatus(str, enum.Enum):
    """Booking status enum."""

    inquiry = "inquiry"
    pending = "pending"
    confirmed = "confirmed"
    checked_in = "checked_in"
    checked_out = "checked_out"
    cancelled = "cancelled"
    no_show = "no_show"


class BookingSource(str, enum.Enum):
    """Booking source enum."""

    direct = "direct"
    website = "website"
    whatsapp = "whatsapp"
    phone = "phone"
    walk_in = "walk_in"
    ota = "ota"  # Online Travel Agency
    corporate = "corporate"


class Booking(BaseModel):
    """Booking model for reservations."""

    __tablename__ = "bookings"

    # Generate booking reference
    booking_ref = Column(String(20), unique=True, nullable=False, index=True)

    hotel_id = Column(Integer, ForeignKey("hotels.id"), nullable=False)
    room_id = Column(Integer, ForeignKey("rooms.id"), nullable=False)
    guest_id = Column(Integer, ForeignKey("guests.id"), nullable=False)

    # Dates
    check_in_date = Column(Date, nullable=False)
    check_out_date = Column(Date, nullable=False)
    actual_check_in = Column(DateTime, nullable=True)
    actual_check_out = Column(DateTime, nullable=True)

    # Occupancy
    adults = Column(Integer, default=1, nullable=False)
    children = Column(Integer, default=0, nullable=False)
    extra_beds = Column(Integer, default=0, nullable=False)

    # Status and source
    status = Column(
        Enum(BookingStatus), default=BookingStatus.pending, nullable=False
    )
    source = Column(
        Enum(BookingSource), default=BookingSource.direct, nullable=False
    )

    # Pricing
    room_rate = Column(Numeric(10, 2), nullable=False)  # Per night
    extra_bed_charge = Column(Numeric(10, 2), default=0)
    subtotal = Column(Numeric(10, 2), nullable=False)
    tax_amount = Column(Numeric(10, 2), default=0)
    discount_amount = Column(Numeric(10, 2), default=0)
    total_amount = Column(Numeric(10, 2), nullable=False)

    # Discount info
    discount_code = Column(String(50), nullable=True)
    discount_percent = Column(Integer, default=0)

    # Payment status
    amount_paid = Column(Numeric(10, 2), default=0)
    is_paid = Column(Boolean, default=False, nullable=False)

    # Special requests
    special_requests = Column(Text, nullable=True)
    internal_notes = Column(Text, nullable=True)

    # Additional charges (JSON for flexibility)
    additional_charges = Column(JSON, default=list)  # [{"description": "...", "amount": 100}]

    # Cancellation
    cancelled_at = Column(DateTime, nullable=True)
    cancellation_reason = Column(Text, nullable=True)

    # Relationships
    hotel = relationship("Hotel", back_populates="bookings")
    room = relationship("Room", back_populates="bookings")
    guest = relationship("Guest", back_populates="bookings")
    payments = relationship("Payment", back_populates="booking")

    def __repr__(self):
        return f"<Booking {self.booking_ref}>"

    @property
    def nights(self):
        """Calculate number of nights."""
        return (self.check_out_date - self.check_in_date).days

    @property
    def balance_due(self):
        """Calculate remaining balance."""
        return float(self.total_amount) - float(self.amount_paid)

    @staticmethod
    def generate_booking_ref():
        """Generate unique booking reference."""
        import random
        import string
        timestamp = datetime.now().strftime("%y%m%d")
        random_str = "".join(random.choices(string.ascii_uppercase + string.digits, k=4))
        return f"BK{timestamp}{random_str}"
