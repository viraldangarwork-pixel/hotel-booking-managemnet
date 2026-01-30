"""Dashboard endpoints."""

from typing import List
from datetime import date, timedelta
from decimal import Decimal
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.hotel import Hotel
from app.models.room import Room, RoomStatus
from app.models.booking import Booking, BookingStatus
from app.models.guest import Guest
from app.models.payment import Payment, PaymentStatus
from app.models.chat import WhatsAppChat
from app.schemas.dashboard import (
    DashboardStats,
    RoomStatusCount,
    OccupancyData,
    RevenueData,
    DashboardOverview,
    UpcomingBooking,
    RoomTypeOccupancy,
    AIInsight,
)

router = APIRouter()


@router.get("/stats", response_model=DashboardStats)
def get_dashboard_stats(
    hotel_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get dashboard statistics."""
    today = date.today()

    # Room counts by status
    room_counts = db.query(
        Room.status, func.count(Room.id)
    ).filter(
        Room.hotel_id == hotel_id,
        Room.is_active == True,
    ).group_by(Room.status).all()

    status_map = {s.value: 0 for s in RoomStatus}
    for status, count in room_counts:
        status_map[status.value] = count

    total_rooms = sum(status_map.values())

    # Today's check-ins/outs
    today_check_ins = db.query(func.count(Booking.id)).filter(
        Booking.hotel_id == hotel_id,
        Booking.check_in_date == today,
        Booking.status.in_([BookingStatus.confirmed, BookingStatus.pending]),
    ).scalar()

    today_check_outs = db.query(func.count(Booking.id)).filter(
        Booking.hotel_id == hotel_id,
        Booking.check_out_date == today,
        Booking.status == BookingStatus.checked_in,
    ).scalar()

    # Pending bookings
    pending_bookings = db.query(func.count(Booking.id)).filter(
        Booking.hotel_id == hotel_id,
        Booking.status == BookingStatus.pending,
    ).scalar()

    # Total guests
    total_guests = db.query(func.count(Guest.id)).filter(
        Guest.hotel_id == hotel_id,
        Guest.is_blacklisted == False,
    ).scalar()

    # Revenue today
    revenue_today = db.query(func.sum(Payment.amount)).join(
        Booking, Payment.booking_id == Booking.id
    ).filter(
        Booking.hotel_id == hotel_id,
        func.date(Payment.paid_at) == today,
        Payment.status == PaymentStatus.completed,
    ).scalar() or Decimal(0)

    # Revenue this month
    first_of_month = today.replace(day=1)
    revenue_month = db.query(func.sum(Payment.amount)).join(
        Booking, Payment.booking_id == Booking.id
    ).filter(
        Booking.hotel_id == hotel_id,
        func.date(Payment.paid_at) >= first_of_month,
        Payment.status == PaymentStatus.completed,
    ).scalar() or Decimal(0)

    # Unread messages
    unread_messages = db.query(func.sum(WhatsAppChat.unread_count)).scalar() or 0

    # Calculate occupancy rate
    occupied_rooms = status_map.get("checked_in", 0) + status_map.get("booked", 0)
    occupancy_rate = (occupied_rooms / total_rooms * 100) if total_rooms > 0 else 0

    return DashboardStats(
        total_rooms=total_rooms,
        rooms_status=RoomStatusCount(
            available=status_map.get("available", 0),
            booked=status_map.get("booked", 0),
            checked_in=status_map.get("checked_in", 0),
            maintenance=status_map.get("maintenance", 0),
            cleaning=status_map.get("cleaning", 0),
        ),
        occupancy_rate=round(occupancy_rate, 1),
        today_check_ins=today_check_ins,
        today_check_outs=today_check_outs,
        pending_bookings=pending_bookings,
        total_guests=total_guests,
        revenue_today=revenue_today,
        revenue_month=revenue_month,
        unread_messages=unread_messages,
    )


@router.get("/occupancy", response_model=List[OccupancyData])
def get_occupancy_trend(
    hotel_id: int,
    days: int = Query(30, ge=7, le=90),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get occupancy trend for the past N days."""
    today = date.today()
    total_rooms = db.query(func.count(Room.id)).filter(
        Room.hotel_id == hotel_id,
        Room.is_active == True,
    ).scalar()

    result = []
    for i in range(days - 1, -1, -1):
        check_date = today - timedelta(days=i)

        # Count bookings that were active on this date
        occupied = db.query(func.count(Booking.id)).filter(
            Booking.hotel_id == hotel_id,
            Booking.check_in_date <= check_date,
            Booking.check_out_date > check_date,
            Booking.status.in_([
                BookingStatus.confirmed,
                BookingStatus.checked_in,
                BookingStatus.checked_out,
            ]),
        ).scalar()

        occupancy_rate = (occupied / total_rooms * 100) if total_rooms > 0 else 0

        result.append(OccupancyData(
            date=check_date,
            total_rooms=total_rooms,
            occupied_rooms=occupied,
            occupancy_rate=round(occupancy_rate, 1),
        ))

    return result


@router.get("/revenue", response_model=List[RevenueData])
def get_revenue_trend(
    hotel_id: int,
    days: int = Query(30, ge=7, le=90),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get revenue trend for the past N days."""
    today = date.today()
    result = []

    for i in range(days - 1, -1, -1):
        check_date = today - timedelta(days=i)

        # Get revenue and booking count for this date
        revenue_data = db.query(
            func.sum(Payment.amount),
            func.count(Payment.id),
        ).join(
            Booking, Payment.booking_id == Booking.id
        ).filter(
            Booking.hotel_id == hotel_id,
            func.date(Payment.paid_at) == check_date,
            Payment.status == PaymentStatus.completed,
        ).first()

        result.append(RevenueData(
            date=check_date,
            revenue=revenue_data[0] or Decimal(0),
            bookings_count=revenue_data[1] or 0,
        ))

    return result


@router.get("/upcoming-arrivals", response_model=List[UpcomingBooking])
def get_upcoming_arrivals(
    hotel_id: int,
    days: int = Query(7, ge=1, le=30),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get upcoming arrivals for the next N days."""
    today = date.today()
    end_date = today + timedelta(days=days)

    bookings = db.query(Booking).filter(
        Booking.hotel_id == hotel_id,
        Booking.check_in_date >= today,
        Booking.check_in_date <= end_date,
        Booking.status.in_([BookingStatus.confirmed, BookingStatus.pending]),
    ).order_by(Booking.check_in_date).all()

    result = []
    for booking in bookings:
        guest = db.query(Guest).filter(Guest.id == booking.guest_id).first()
        room = db.query(Room).filter(Room.id == booking.room_id).first()

        result.append(UpcomingBooking(
            id=booking.id,
            booking_ref=booking.booking_ref,
            guest_name=f"{guest.first_name} {guest.last_name}" if guest else "Unknown",
            room_number=room.room_number if room else "N/A",
            check_in_date=booking.check_in_date,
            check_out_date=booking.check_out_date,
            status=booking.status.value,
            is_vip=guest.is_vip if guest else False,
        ))

    return result


@router.get("/insights", response_model=List[AIInsight])
def get_ai_insights(
    hotel_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get AI-generated insights and suggestions."""
    insights = []
    today = date.today()

    # Check for low occupancy
    total_rooms = db.query(func.count(Room.id)).filter(
        Room.hotel_id == hotel_id,
        Room.is_active == True,
    ).scalar()

    occupied = db.query(func.count(Room.id)).filter(
        Room.hotel_id == hotel_id,
        Room.status.in_([RoomStatus.checked_in, RoomStatus.booked]),
    ).scalar()

    occupancy_rate = (occupied / total_rooms * 100) if total_rooms > 0 else 0

    if occupancy_rate < 50:
        insights.append(AIInsight(
            type="warning",
            title="Low Occupancy Alert",
            message=f"Current occupancy is {occupancy_rate:.1f}%. Consider running promotions.",
            priority=2,
            action="Create a discount campaign",
        ))

    # Check for pending bookings
    pending = db.query(func.count(Booking.id)).filter(
        Booking.hotel_id == hotel_id,
        Booking.status == BookingStatus.pending,
    ).scalar()

    if pending > 5:
        insights.append(AIInsight(
            type="alert",
            title="Pending Bookings",
            message=f"You have {pending} bookings waiting for confirmation.",
            priority=1,
            action="Review pending bookings",
        ))

    # VIP arrivals today
    vip_arrivals = db.query(Booking).join(Guest).filter(
        Booking.hotel_id == hotel_id,
        Booking.check_in_date == today,
        Guest.is_vip == True,
        Booking.status.in_([BookingStatus.confirmed, BookingStatus.pending]),
    ).count()

    if vip_arrivals > 0:
        insights.append(AIInsight(
            type="suggestion",
            title="VIP Arrivals Today",
            message=f"{vip_arrivals} VIP guest(s) arriving today. Ensure special arrangements.",
            priority=1,
        ))

    # Rooms needing maintenance
    maintenance_rooms = db.query(func.count(Room.id)).filter(
        Room.hotel_id == hotel_id,
        Room.status == RoomStatus.maintenance,
    ).scalar()

    if maintenance_rooms > 0:
        insights.append(AIInsight(
            type="warning",
            title="Rooms Under Maintenance",
            message=f"{maintenance_rooms} room(s) are currently under maintenance.",
            priority=3,
        ))

    return sorted(insights, key=lambda x: x.priority)


@router.get("/overview", response_model=DashboardOverview)
def get_dashboard_overview(
    hotel_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get complete dashboard overview."""
    stats = get_dashboard_stats(hotel_id, db, current_user)
    today_data = get_today_bookings_internal(hotel_id, db)
    upcoming = get_upcoming_arrivals(hotel_id, 7, db, current_user)
    occupancy_trend = get_occupancy_trend(hotel_id, 14, db, current_user)
    revenue_trend = get_revenue_trend(hotel_id, 14, db, current_user)

    # Room type occupancy
    room_type_occupancy = get_room_type_occupancy(hotel_id, db)

    return DashboardOverview(
        stats=stats,
        today_check_ins=today_data["check_ins"],
        today_check_outs=today_data["check_outs"],
        upcoming_arrivals=upcoming,
        occupancy_trend=occupancy_trend,
        revenue_trend=revenue_trend,
        room_type_occupancy=room_type_occupancy,
    )


def get_today_bookings_internal(hotel_id: int, db: Session) -> dict:
    """Internal function to get today's bookings."""
    today = date.today()

    check_ins = db.query(Booking).filter(
        Booking.hotel_id == hotel_id,
        Booking.check_in_date == today,
        Booking.status.in_([BookingStatus.confirmed, BookingStatus.pending]),
    ).all()

    check_outs = db.query(Booking).filter(
        Booking.hotel_id == hotel_id,
        Booking.check_out_date == today,
        Booking.status == BookingStatus.checked_in,
    ).all()

    result_check_ins = []
    result_check_outs = []

    for booking in check_ins:
        guest = db.query(Guest).filter(Guest.id == booking.guest_id).first()
        room = db.query(Room).filter(Room.id == booking.room_id).first()
        result_check_ins.append(UpcomingBooking(
            id=booking.id,
            booking_ref=booking.booking_ref,
            guest_name=f"{guest.first_name} {guest.last_name}" if guest else "Unknown",
            room_number=room.room_number if room else "N/A",
            check_in_date=booking.check_in_date,
            check_out_date=booking.check_out_date,
            status=booking.status.value,
            is_vip=guest.is_vip if guest else False,
        ))

    for booking in check_outs:
        guest = db.query(Guest).filter(Guest.id == booking.guest_id).first()
        room = db.query(Room).filter(Room.id == booking.room_id).first()
        result_check_outs.append(UpcomingBooking(
            id=booking.id,
            booking_ref=booking.booking_ref,
            guest_name=f"{guest.first_name} {guest.last_name}" if guest else "Unknown",
            room_number=room.room_number if room else "N/A",
            check_in_date=booking.check_in_date,
            check_out_date=booking.check_out_date,
            status=booking.status.value,
            is_vip=guest.is_vip if guest else False,
        ))

    return {"check_ins": result_check_ins, "check_outs": result_check_outs}


def get_room_type_occupancy(hotel_id: int, db: Session) -> List[RoomTypeOccupancy]:
    """Get occupancy by room type."""
    from app.models.room import RoomType

    room_types = db.query(RoomType).filter(
        RoomType.hotel_id == hotel_id,
        RoomType.is_active == True,
    ).all()

    result = []
    for rt in room_types:
        total = db.query(func.count(Room.id)).filter(
            Room.room_type_id == rt.id,
            Room.is_active == True,
        ).scalar()

        occupied = db.query(func.count(Room.id)).filter(
            Room.room_type_id == rt.id,
            Room.is_active == True,
            Room.status.in_([RoomStatus.checked_in, RoomStatus.booked]),
        ).scalar()

        occupancy_rate = (occupied / total * 100) if total > 0 else 0

        result.append(RoomTypeOccupancy(
            room_type_id=rt.id,
            room_type_name=rt.name,
            total_rooms=total,
            occupied_rooms=occupied,
            occupancy_rate=round(occupancy_rate, 1),
        ))

    return result
