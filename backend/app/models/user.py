"""User model for authentication and staff management."""

from sqlalchemy import Column, String, Boolean, Integer, ForeignKey, Enum
from sqlalchemy.orm import relationship
import enum

from .base import BaseModel


class UserRole(str, enum.Enum):
    """User roles for role-based access control."""

    SUPERADMIN = "superadmin"
    ADMIN = "admin"
    MANAGER = "manager"
    RECEPTIONIST = "receptionist"
    STAFF = "staff"


class User(BaseModel):
    """User model for authentication and authorization."""

    __tablename__ = "users"

    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    phone = Column(String(20), nullable=True)

    role = Column(
        Enum(UserRole), default=UserRole.STAFF, nullable=False
    )
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)

    # Hotel association (for multi-hotel support)
    hotel_id = Column(Integer, ForeignKey("hotels.id"), nullable=True)

    # Relationships
    hotel = relationship("Hotel", back_populates="staff")

    def __repr__(self):
        return f"<User {self.email}>"
