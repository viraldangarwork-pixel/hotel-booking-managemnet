"""Pydantic schemas for request/response validation."""

from .user import UserCreate, UserUpdate, UserResponse, UserLogin, Token
from .hotel import HotelCreate, HotelUpdate, HotelResponse
from .room import RoomCreate, RoomUpdate, RoomResponse, RoomTypeCreate, RoomTypeUpdate, RoomTypeResponse
from .booking import BookingCreate, BookingUpdate, BookingResponse
from .guest import GuestCreate, GuestUpdate, GuestResponse
from .payment import PaymentCreate, PaymentResponse
from .chat import WhatsAppMessageCreate, WhatsAppChatResponse, AIChatMessageCreate, AIChatResponse
from .settings import ThemeSettingsUpdate, ThemeSettingsResponse, HotelSettingsUpdate, HotelSettingsResponse
from .dashboard import DashboardStats, OccupancyData, RevenueData

__all__ = [
    # User
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    "UserLogin",
    "Token",
    # Hotel
    "HotelCreate",
    "HotelUpdate",
    "HotelResponse",
    # Room
    "RoomCreate",
    "RoomUpdate",
    "RoomResponse",
    "RoomTypeCreate",
    "RoomTypeUpdate",
    "RoomTypeResponse",
    # Booking
    "BookingCreate",
    "BookingUpdate",
    "BookingResponse",
    # Guest
    "GuestCreate",
    "GuestUpdate",
    "GuestResponse",
    # Payment
    "PaymentCreate",
    "PaymentResponse",
    # Chat
    "WhatsAppMessageCreate",
    "WhatsAppChatResponse",
    "AIChatMessageCreate",
    "AIChatResponse",
    # Settings
    "ThemeSettingsUpdate",
    "ThemeSettingsResponse",
    "HotelSettingsUpdate",
    "HotelSettingsResponse",
    # Dashboard
    "DashboardStats",
    "OccupancyData",
    "RevenueData",
]
