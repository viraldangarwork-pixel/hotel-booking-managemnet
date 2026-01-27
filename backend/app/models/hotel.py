"""Hotel model."""

from sqlalchemy import Column, String, Text, Integer, Boolean, JSON
from sqlalchemy.orm import relationship

from .base import BaseModel


class Hotel(BaseModel):
    """Hotel model representing a hotel property."""

    __tablename__ = "hotels"

    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    address = Column(Text, nullable=False)
    city = Column(String(100), nullable=False)
    state = Column(String(100), nullable=True)
    country = Column(String(100), nullable=False)
    postal_code = Column(String(20), nullable=True)

    phone = Column(String(20), nullable=True)
    email = Column(String(255), nullable=True)
    website = Column(String(255), nullable=True)

    # Total floors and rooms
    total_floors = Column(Integer, default=1, nullable=False)
    total_rooms = Column(Integer, default=0, nullable=False)

    # Hotel amenities (JSON array)
    amenities = Column(JSON, default=list)

    # Check-in/out times
    check_in_time = Column(String(10), default="14:00", nullable=False)
    check_out_time = Column(String(10), default="11:00", nullable=False)

    # Tax settings
    tax_rate = Column(Integer, default=18)  # Percentage
    gst_number = Column(String(50), nullable=True)

    # Branding
    logo_url = Column(String(500), nullable=True)
    primary_color = Column(String(7), default="#2563eb")

    is_active = Column(Boolean, default=True, nullable=False)

    # Relationships
    rooms = relationship("Room", back_populates="hotel", cascade="all, delete-orphan")
    room_types = relationship("RoomType", back_populates="hotel", cascade="all, delete-orphan")
    bookings = relationship("Booking", back_populates="hotel", cascade="all, delete-orphan")
    guests = relationship("Guest", back_populates="hotel", cascade="all, delete-orphan")
    staff = relationship("User", back_populates="hotel")
    settings = relationship("HotelSettings", back_populates="hotel", uselist=False)
    theme_settings = relationship("ThemeSettings", back_populates="hotel", uselist=False)

    def __repr__(self):
        return f"<Hotel {self.name}>"
