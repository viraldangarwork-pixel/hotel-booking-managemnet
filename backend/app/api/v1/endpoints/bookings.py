"""Booking management endpoints."""

from typing import List, Optional
from datetime import date, datetime
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.core.database import get_db
from app.core.security import get_current_user, require_roles
from app.models.user import User
from app.models.room import Room, RoomType, RoomStatus
from app.models.booking import Booking, BookingStatus, BookingSource
from app.models.guest import Guest
from app.models.hotel import Hotel
from app.schemas.booking import (
    BookingCreate,
    BookingUpdate,
    BookingResponse,
    BookingCheckIn,
    BookingCheckOut,
)

router = APIRouter()


def calculate_booking_totals(
    room_rate: Decimal,
    nights: int,
    extra_beds: int,
    extra_bed_price: Decimal,
    tax_rate: int,
    discount_percent: int = 0,
) -> dict:
    """Calculate booking totals."""
    room_total = room_rate * nights
    extra_bed_charge = extra_bed_price * extra_beds * nights
    subtotal = room_total + extra_bed_charge
    discount_amount = subtotal * (Decimal(discount_percent) / 100)
    taxable_amount = subtotal - discount_amount
    tax_amount = taxable_amount * (Decimal(tax_rate) / 100)
    total_amount = taxable_amount + tax_amount

    return {
        "room_rate": room_rate,
        "extra_bed_charge": extra_bed_charge,
        "subtotal": subtotal,
        "discount_amount": discount_amount,
        "tax_amount": tax_amount,
        "total_amount": total_amount,
    }


@router.get("/", response_model=List[BookingResponse])
def list_bookings(
    hotel_id: int,
    status: Optional[BookingStatus] = None,
    check_in_date: Optional[date] = None,
    check_out_date: Optional[date] = None,
    guest_id: Optional[int] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List bookings for a hotel."""
    query = db.query(Booking).filter(Booking.hotel_id == hotel_id)

    if status:
        query = query.filter(Booking.status == status)
    if check_in_date:
        query = query.filter(Booking.check_in_date == check_in_date)
    if check_out_date:
        query = query.filter(Booking.check_out_date == check_out_date)
    if guest_id:
        query = query.filter(Booking.guest_id == guest_id)

    bookings = query.order_by(Booking.created_at.desc()).offset(skip).limit(limit).all()

    # Load related objects
    for booking in bookings:
        booking.guest = db.query(Guest).filter(Guest.id == booking.guest_id).first()
        booking.room = db.query(Room).filter(Room.id == booking.room_id).first()
        if booking.room:
            booking.room.room_type = db.query(RoomType).filter(
                RoomType.id == booking.room.room_type_id
            ).first()

    return bookings


@router.get("/today", response_model=dict)
def get_today_bookings(
    hotel_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get today's check-ins and check-outs."""
    today = date.today()

    check_ins = db.query(Booking).filter(
        Booking.hotel_id == hotel_id,
        Booking.check_in_date == today,
        Booking.status.in_([BookingStatus.CONFIRMED, BookingStatus.PENDING]),
    ).all()

    check_outs = db.query(Booking).filter(
        Booking.hotel_id == hotel_id,
        Booking.check_out_date == today,
        Booking.status == BookingStatus.CHECKED_IN,
    ).all()

    # Load related objects
    for booking in check_ins + check_outs:
        booking.guest = db.query(Guest).filter(Guest.id == booking.guest_id).first()
        booking.room = db.query(Room).filter(Room.id == booking.room_id).first()

    return {
        "check_ins": check_ins,
        "check_outs": check_outs,
    }


@router.get("/{booking_id}", response_model=BookingResponse)
def get_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get booking by ID."""
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found",
        )

    booking.guest = db.query(Guest).filter(Guest.id == booking.guest_id).first()
    booking.room = db.query(Room).filter(Room.id == booking.room_id).first()
    if booking.room:
        booking.room.room_type = db.query(RoomType).filter(
            RoomType.id == booking.room.room_type_id
        ).first()

    return booking


@router.get("/ref/{booking_ref}", response_model=BookingResponse)
def get_booking_by_ref(
    booking_ref: str,
    db: Session = Depends(get_db),
):
    """Get booking by reference number (public)."""
    booking = db.query(Booking).filter(Booking.booking_ref == booking_ref).first()
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found",
        )

    booking.guest = db.query(Guest).filter(Guest.id == booking.guest_id).first()
    booking.room = db.query(Room).filter(Room.id == booking.room_id).first()

    return booking


@router.post("/", response_model=BookingResponse, status_code=status.HTTP_201_CREATED)
def create_booking(
    booking_data: BookingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new booking."""
    # Validate dates
    if booking_data.check_out_date <= booking_data.check_in_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Check-out date must be after check-in date",
        )

    # Check room availability
    room = db.query(Room).filter(Room.id == booking_data.room_id).first()
    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room not found",
        )

    # Check for overlapping bookings
    overlapping = db.query(Booking).filter(
        Booking.room_id == booking_data.room_id,
        Booking.status.in_([
            BookingStatus.CONFIRMED,
            BookingStatus.CHECKED_IN,
            BookingStatus.PENDING,
        ]),
        and_(
            Booking.check_in_date < booking_data.check_out_date,
            Booking.check_out_date > booking_data.check_in_date,
        ),
    ).first()

    if overlapping:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Room is not available for selected dates",
        )

    # Get hotel and room type for pricing
    hotel = db.query(Hotel).filter(Hotel.id == booking_data.hotel_id).first()
    room_type = db.query(RoomType).filter(RoomType.id == room.room_type_id).first()

    if not hotel or not room_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hotel or room type not found",
        )

    # Calculate totals
    nights = (booking_data.check_out_date - booking_data.check_in_date).days
    room_rate = room.custom_price or room_type.base_price

    totals = calculate_booking_totals(
        room_rate=room_rate,
        nights=nights,
        extra_beds=booking_data.extra_beds,
        extra_bed_price=room_type.extra_bed_price,
        tax_rate=hotel.tax_rate,
        discount_percent=0,  # TODO: Apply discount code
    )

    # Create booking
    booking = Booking(
        booking_ref=Booking.generate_booking_ref(),
        hotel_id=booking_data.hotel_id,
        room_id=booking_data.room_id,
        guest_id=booking_data.guest_id,
        check_in_date=booking_data.check_in_date,
        check_out_date=booking_data.check_out_date,
        adults=booking_data.adults,
        children=booking_data.children,
        extra_beds=booking_data.extra_beds,
        source=booking_data.source,
        special_requests=booking_data.special_requests,
        **totals,
    )

    db.add(booking)
    db.commit()
    db.refresh(booking)

    # Update room status
    if booking.check_in_date == date.today():
        room.status = RoomStatus.BOOKED
        db.commit()

    booking.guest = db.query(Guest).filter(Guest.id == booking.guest_id).first()
    booking.room = room
    booking.room.room_type = room_type

    return booking


@router.put("/{booking_id}", response_model=BookingResponse)
def update_booking(
    booking_id: int,
    booking_data: BookingUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update booking."""
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found",
        )

    update_data = booking_data.model_dump(exclude_unset=True)

    # Recalculate totals if dates or extras changed
    if any(k in update_data for k in ["check_in_date", "check_out_date", "extra_beds", "room_id"]):
        room = db.query(Room).filter(
            Room.id == update_data.get("room_id", booking.room_id)
        ).first()
        room_type = db.query(RoomType).filter(RoomType.id == room.room_type_id).first()
        hotel = db.query(Hotel).filter(Hotel.id == booking.hotel_id).first()

        check_in = update_data.get("check_in_date", booking.check_in_date)
        check_out = update_data.get("check_out_date", booking.check_out_date)
        nights = (check_out - check_in).days

        totals = calculate_booking_totals(
            room_rate=room.custom_price or room_type.base_price,
            nights=nights,
            extra_beds=update_data.get("extra_beds", booking.extra_beds),
            extra_bed_price=room_type.extra_bed_price,
            tax_rate=hotel.tax_rate,
            discount_percent=booking.discount_percent,
        )
        update_data.update(totals)

    for key, value in update_data.items():
        setattr(booking, key, value)

    db.commit()
    db.refresh(booking)

    booking.guest = db.query(Guest).filter(Guest.id == booking.guest_id).first()
    booking.room = db.query(Room).filter(Room.id == booking.room_id).first()

    return booking


@router.post("/{booking_id}/check-in", response_model=BookingResponse)
def check_in(
    booking_id: int,
    check_in_data: BookingCheckIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Process guest check-in."""
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found",
        )

    if booking.status not in [BookingStatus.CONFIRMED, BookingStatus.PENDING]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Booking cannot be checked in",
        )

    # Update booking
    booking.status = BookingStatus.CHECKED_IN
    booking.actual_check_in = datetime.now()
    if check_in_data.notes:
        booking.internal_notes = check_in_data.notes

    # Update room status
    room = db.query(Room).filter(Room.id == booking.room_id).first()
    room.status = RoomStatus.CHECKED_IN

    # Update guest ID if provided
    if check_in_data.id_type and check_in_data.id_number:
        guest = db.query(Guest).filter(Guest.id == booking.guest_id).first()
        guest.id_type = check_in_data.id_type
        guest.id_number = check_in_data.id_number

    db.commit()
    db.refresh(booking)

    booking.guest = db.query(Guest).filter(Guest.id == booking.guest_id).first()
    booking.room = room

    return booking


@router.post("/{booking_id}/check-out", response_model=BookingResponse)
def check_out(
    booking_id: int,
    check_out_data: BookingCheckOut,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Process guest check-out."""
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found",
        )

    if booking.status != BookingStatus.CHECKED_IN:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Guest is not checked in",
        )

    # Add additional charges if any
    if check_out_data.additional_charges:
        booking.additional_charges = (
            booking.additional_charges or []
        ) + check_out_data.additional_charges
        # Recalculate total
        additional_total = sum(c.get("amount", 0) for c in check_out_data.additional_charges)
        booking.total_amount = Decimal(str(booking.total_amount)) + Decimal(str(additional_total))

    # Update booking
    booking.status = BookingStatus.CHECKED_OUT
    booking.actual_check_out = datetime.now()
    if check_out_data.notes:
        booking.internal_notes = (booking.internal_notes or "") + f"\nCheckout: {check_out_data.notes}"

    # Update room status
    room = db.query(Room).filter(Room.id == booking.room_id).first()
    room.status = RoomStatus.CLEANING

    # Update guest stats
    guest = db.query(Guest).filter(Guest.id == booking.guest_id).first()
    guest.total_stays += 1
    guest.total_spent += int(booking.total_amount * 100)  # Store in paise/cents
    guest.last_visit = date.today()

    db.commit()
    db.refresh(booking)

    booking.guest = guest
    booking.room = room

    return booking


@router.post("/{booking_id}/cancel", response_model=BookingResponse)
def cancel_booking(
    booking_id: int,
    reason: str = "",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Cancel a booking."""
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found",
        )

    if booking.status in [BookingStatus.CHECKED_OUT, BookingStatus.CANCELLED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Booking cannot be cancelled",
        )

    booking.status = BookingStatus.CANCELLED
    booking.cancelled_at = datetime.now()
    booking.cancellation_reason = reason

    # Update room status if it was booked
    room = db.query(Room).filter(Room.id == booking.room_id).first()
    if room.status == RoomStatus.BOOKED:
        room.status = RoomStatus.AVAILABLE

    db.commit()
    db.refresh(booking)

    return booking
