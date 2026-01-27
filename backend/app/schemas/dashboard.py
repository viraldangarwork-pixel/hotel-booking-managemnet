"""Dashboard schemas."""

from typing import List, Optional
from datetime import date
from decimal import Decimal

from .base import BaseSchema
from .booking import BookingResponse


class RoomStatusCount(BaseSchema):
    """Room status count."""

    available: int
    booked: int
    checked_in: int
    maintenance: int
    cleaning: int


class DashboardStats(BaseSchema):
    """Dashboard statistics."""

    total_rooms: int
    rooms_status: RoomStatusCount
    occupancy_rate: float
    today_check_ins: int
    today_check_outs: int
    pending_bookings: int
    total_guests: int
    revenue_today: Decimal
    revenue_month: Decimal
    unread_messages: int


class OccupancyData(BaseSchema):
    """Occupancy data for charts."""

    date: date
    total_rooms: int
    occupied_rooms: int
    occupancy_rate: float


class RevenueData(BaseSchema):
    """Revenue data for charts."""

    date: date
    revenue: Decimal
    bookings_count: int


class RoomTypeOccupancy(BaseSchema):
    """Room type occupancy."""

    room_type_id: int
    room_type_name: str
    total_rooms: int
    occupied_rooms: int
    occupancy_rate: float


class UpcomingBooking(BaseSchema):
    """Upcoming booking summary."""

    id: int
    booking_ref: str
    guest_name: str
    room_number: str
    check_in_date: date
    check_out_date: date
    status: str
    is_vip: bool


class DashboardOverview(BaseSchema):
    """Complete dashboard overview."""

    stats: DashboardStats
    today_check_ins: List[UpcomingBooking]
    today_check_outs: List[UpcomingBooking]
    upcoming_arrivals: List[UpcomingBooking]
    occupancy_trend: List[OccupancyData]
    revenue_trend: List[RevenueData]
    room_type_occupancy: List[RoomTypeOccupancy]


class AIInsight(BaseSchema):
    """AI-generated insight."""

    type: str  # warning, suggestion, alert
    title: str
    message: str
    priority: int  # 1-5
    action: Optional[str] = None
    data: Optional[dict] = None
