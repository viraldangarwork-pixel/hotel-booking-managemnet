"""Room and RoomType models."""

from sqlalchemy import Column, String, Text, Integer, ForeignKey, Enum, Numeric, JSON, Boolean
from sqlalchemy.orm import relationship
import enum

from .base import BaseModel


class RoomStatus(str, enum.Enum):
    """Room status enum."""

    available = "available"
    booked = "booked"
    checked_in = "checked_in"
    checked_out = "checked_out"
    maintenance = "maintenance"
    cleaning = "cleaning"


class RoomType(BaseModel):
    """Room type model (Single, Deluxe, Suite, etc.)."""

    __tablename__ = "room_types"

    hotel_id = Column(Integer, ForeignKey("hotels.id"), nullable=False)

    name = Column(String(100), nullable=False)  # e.g., "Deluxe", "Suite"
    description = Column(Text, nullable=True)

    # Pricing
    base_price = Column(Numeric(10, 2), nullable=False)
    extra_bed_price = Column(Numeric(10, 2), default=0)

    # Capacity
    max_occupancy = Column(Integer, default=2, nullable=False)
    max_adults = Column(Integer, default=2, nullable=False)
    max_children = Column(Integer, default=1, nullable=False)

    # Room features
    bed_type = Column(String(50), nullable=True)  # Single, Double, King, Twin
    room_size = Column(Integer, nullable=True)  # Square feet/meters
    amenities = Column(JSON, default=list)  # ["WiFi", "AC", "TV", etc.]
    images = Column(JSON, default=list)  # Array of image URLs

    is_active = Column(Boolean, default=True, nullable=False)

    # Relationships
    hotel = relationship("Hotel", back_populates="room_types")
    rooms = relationship("Room", back_populates="room_type")

    def __repr__(self):
        return f"<RoomType {self.name}>"


class Room(BaseModel):
    """Individual room model."""

    __tablename__ = "rooms"

    hotel_id = Column(Integer, ForeignKey("hotels.id"), nullable=False)
    room_type_id = Column(Integer, ForeignKey("room_types.id"), nullable=False)

    room_number = Column(String(20), nullable=False)
    floor = Column(Integer, default=1, nullable=False)

    status = Column(
        Enum(RoomStatus), default=RoomStatus.available, nullable=False
    )

    # Room-specific notes
    notes = Column(Text, nullable=True)

    # Override pricing (if different from room type)
    custom_price = Column(Numeric(10, 2), nullable=True)

    is_active = Column(Boolean, default=True, nullable=False)

    # Relationships
    hotel = relationship("Hotel", back_populates="rooms")
    room_type = relationship("RoomType", back_populates="rooms")
    bookings = relationship("Booking", back_populates="room")

    def __repr__(self):
        return f"<Room {self.room_number}>"

    @property
    def current_price(self):
        """Get current room price (custom or from room type)."""
        return self.custom_price or self.room_type.base_price
