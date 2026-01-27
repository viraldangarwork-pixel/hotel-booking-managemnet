"""Guest model for CRM."""

from sqlalchemy import Column, String, Text, Integer, ForeignKey, Boolean, JSON, Date
from sqlalchemy.orm import relationship

from .base import BaseModel


class Guest(BaseModel):
    """Guest model for CRM and booking management."""

    __tablename__ = "guests"

    hotel_id = Column(Integer, ForeignKey("hotels.id"), nullable=False)

    # Personal Information
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), nullable=True, index=True)
    phone = Column(String(20), nullable=False, index=True)
    whatsapp_number = Column(String(20), nullable=True, index=True)

    # Identity
    id_type = Column(String(50), nullable=True)  # Passport, Aadhar, Driving License, etc.
    id_number = Column(String(100), nullable=True)
    nationality = Column(String(100), nullable=True)

    # Address
    address = Column(Text, nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    country = Column(String(100), nullable=True)
    postal_code = Column(String(20), nullable=True)

    # Date of birth
    date_of_birth = Column(Date, nullable=True)

    # Guest classification
    is_vip = Column(Boolean, default=False, nullable=False)
    is_blacklisted = Column(Boolean, default=False, nullable=False)

    # Preferences and notes (JSON for flexibility)
    preferences = Column(JSON, default=dict)
    notes = Column(Text, nullable=True)
    tags = Column(JSON, default=list)  # ["VIP", "Corporate", "Repeat", etc.]

    # Stats
    total_stays = Column(Integer, default=0, nullable=False)
    total_spent = Column(Integer, default=0, nullable=False)  # In cents/paise
    last_visit = Column(Date, nullable=True)

    # Relationships
    hotel = relationship("Hotel", back_populates="guests")
    bookings = relationship("Booking", back_populates="guest")
    whatsapp_chats = relationship("WhatsAppChat", back_populates="guest")

    def __repr__(self):
        return f"<Guest {self.first_name} {self.last_name}>"

    @property
    def full_name(self):
        """Get full name."""
        return f"{self.first_name} {self.last_name}"
