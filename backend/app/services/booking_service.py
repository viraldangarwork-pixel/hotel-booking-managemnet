"""Booking service for business logic."""

from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models.booking import Booking, BookingStatus, BookingSource
from app.models.room import Room, RoomType, RoomStatus
from app.models.guest import Guest
from app.models.hotel import Hotel
from app.models.payment import Payment, PaymentStatus


class BookingService:
    """Service class for booking operations."""

    def __init__(self, db: Session):
        self.db = db

    def calculate_booking_totals(
        self,
        room_rate: Decimal,
        nights: int,
        extra_beds: int,
        extra_bed_price: Decimal,
        tax_rate: int,
        discount_percent: int = 0,
    ) -> Dict[str, Decimal]:
        """Calculate booking totals including taxes and discounts."""
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

    def check_room_availability(
        self,
        room_id: int,
        check_in_date: date,
        check_out_date: date,
        exclude_booking_id: Optional[int] = None,
    ) -> bool:
        """Check if a room is available for given dates."""
        query = self.db.query(Booking).filter(
            Booking.room_id == room_id,
            Booking.status.in_([
                BookingStatus.CONFIRMED,
                BookingStatus.CHECKED_IN,
                BookingStatus.PENDING,
            ]),
            and_(
                Booking.check_in_date < check_out_date,
                Booking.check_out_date > check_in_date,
            ),
        )

        if exclude_booking_id:
            query = query.filter(Booking.id != exclude_booking_id)

        return query.first() is None

    def get_available_rooms(
        self,
        hotel_id: int,
        check_in_date: date,
        check_out_date: date,
        room_type_id: Optional[int] = None,
        adults: int = 1,
        children: int = 0,
    ) -> List[Room]:
        """Get all available rooms for given dates and criteria."""
        # Get all active rooms
        query = self.db.query(Room).filter(
            Room.hotel_id == hotel_id,
            Room.is_active == True,
            Room.status != RoomStatus.MAINTENANCE,
        )

        if room_type_id:
            query = query.filter(Room.room_type_id == room_type_id)

        rooms = query.all()

        # Get booked room IDs
        booked_room_ids = self.db.query(Booking.room_id).filter(
            Booking.hotel_id == hotel_id,
            Booking.status.in_([
                BookingStatus.CONFIRMED,
                BookingStatus.CHECKED_IN,
                BookingStatus.PENDING,
            ]),
            and_(
                Booking.check_in_date < check_out_date,
                Booking.check_out_date > check_in_date,
            ),
        ).all()
        booked_room_ids = [r[0] for r in booked_room_ids]

        # Filter available rooms
        available_rooms = []
        for room in rooms:
            if room.id not in booked_room_ids:
                room_type = self.db.query(RoomType).filter(
                    RoomType.id == room.room_type_id
                ).first()
                if room_type and room_type.max_occupancy >= (adults + children):
                    room.room_type = room_type
                    available_rooms.append(room)

        return available_rooms

    def create_booking(
        self,
        hotel_id: int,
        room_id: int,
        guest_id: int,
        check_in_date: date,
        check_out_date: date,
        adults: int = 1,
        children: int = 0,
        extra_beds: int = 0,
        source: BookingSource = BookingSource.DIRECT,
        special_requests: Optional[str] = None,
        discount_code: Optional[str] = None,
    ) -> Booking:
        """Create a new booking with calculated totals."""
        # Validate dates
        if check_out_date <= check_in_date:
            raise ValueError("Check-out date must be after check-in date")

        # Check availability
        if not self.check_room_availability(room_id, check_in_date, check_out_date):
            raise ValueError("Room is not available for selected dates")

        # Get room and hotel info
        room = self.db.query(Room).filter(Room.id == room_id).first()
        if not room:
            raise ValueError("Room not found")

        hotel = self.db.query(Hotel).filter(Hotel.id == hotel_id).first()
        room_type = self.db.query(RoomType).filter(RoomType.id == room.room_type_id).first()

        if not hotel or not room_type:
            raise ValueError("Hotel or room type not found")

        # Calculate totals
        nights = (check_out_date - check_in_date).days
        room_rate = room.custom_price or room_type.base_price
        discount_percent = 0  # TODO: Apply discount code logic

        totals = self.calculate_booking_totals(
            room_rate=room_rate,
            nights=nights,
            extra_beds=extra_beds,
            extra_bed_price=room_type.extra_bed_price,
            tax_rate=hotel.tax_rate,
            discount_percent=discount_percent,
        )

        # Create booking
        booking = Booking(
            booking_ref=Booking.generate_booking_ref(),
            hotel_id=hotel_id,
            room_id=room_id,
            guest_id=guest_id,
            check_in_date=check_in_date,
            check_out_date=check_out_date,
            adults=adults,
            children=children,
            extra_beds=extra_beds,
            source=source,
            special_requests=special_requests,
            discount_code=discount_code,
            discount_percent=discount_percent,
            **totals,
        )

        self.db.add(booking)
        self.db.commit()
        self.db.refresh(booking)

        # Update room status if check-in is today
        if check_in_date == date.today():
            room.status = RoomStatus.BOOKED
            self.db.commit()

        return booking

    def process_check_in(
        self,
        booking_id: int,
        id_type: Optional[str] = None,
        id_number: Optional[str] = None,
        notes: Optional[str] = None,
    ) -> Booking:
        """Process guest check-in."""
        booking = self.db.query(Booking).filter(Booking.id == booking_id).first()
        if not booking:
            raise ValueError("Booking not found")

        if booking.status not in [BookingStatus.CONFIRMED, BookingStatus.PENDING]:
            raise ValueError("Booking cannot be checked in")

        # Update booking
        booking.status = BookingStatus.CHECKED_IN
        booking.actual_check_in = datetime.now()
        if notes:
            booking.internal_notes = notes

        # Update room status
        room = self.db.query(Room).filter(Room.id == booking.room_id).first()
        room.status = RoomStatus.CHECKED_IN

        # Update guest ID if provided
        if id_type and id_number:
            guest = self.db.query(Guest).filter(Guest.id == booking.guest_id).first()
            guest.id_type = id_type
            guest.id_number = id_number

        self.db.commit()
        self.db.refresh(booking)

        return booking

    def process_check_out(
        self,
        booking_id: int,
        additional_charges: Optional[List[Dict[str, Any]]] = None,
        notes: Optional[str] = None,
    ) -> Booking:
        """Process guest check-out."""
        booking = self.db.query(Booking).filter(Booking.id == booking_id).first()
        if not booking:
            raise ValueError("Booking not found")

        if booking.status != BookingStatus.CHECKED_IN:
            raise ValueError("Guest is not checked in")

        # Add additional charges
        if additional_charges:
            booking.additional_charges = (
                booking.additional_charges or []
            ) + additional_charges
            additional_total = sum(c.get("amount", 0) for c in additional_charges)
            booking.total_amount = Decimal(str(booking.total_amount)) + Decimal(str(additional_total))

        # Update booking
        booking.status = BookingStatus.CHECKED_OUT
        booking.actual_check_out = datetime.now()
        if notes:
            booking.internal_notes = (booking.internal_notes or "") + f"\nCheckout: {notes}"

        # Update room status
        room = self.db.query(Room).filter(Room.id == booking.room_id).first()
        room.status = RoomStatus.CLEANING

        # Update guest stats
        guest = self.db.query(Guest).filter(Guest.id == booking.guest_id).first()
        guest.total_stays += 1
        guest.total_spent += int(booking.total_amount * 100)
        guest.last_visit = date.today()

        self.db.commit()
        self.db.refresh(booking)

        return booking

    def cancel_booking(
        self,
        booking_id: int,
        reason: str = "",
    ) -> Booking:
        """Cancel a booking."""
        booking = self.db.query(Booking).filter(Booking.id == booking_id).first()
        if not booking:
            raise ValueError("Booking not found")

        if booking.status in [BookingStatus.CHECKED_OUT, BookingStatus.CANCELLED]:
            raise ValueError("Booking cannot be cancelled")

        booking.status = BookingStatus.CANCELLED
        booking.cancelled_at = datetime.now()
        booking.cancellation_reason = reason

        # Update room status if it was booked
        room = self.db.query(Room).filter(Room.id == booking.room_id).first()
        if room.status == RoomStatus.BOOKED:
            room.status = RoomStatus.AVAILABLE

        self.db.commit()
        self.db.refresh(booking)

        return booking

    def get_today_arrivals(self, hotel_id: int) -> List[Booking]:
        """Get today's expected arrivals."""
        return self.db.query(Booking).filter(
            Booking.hotel_id == hotel_id,
            Booking.check_in_date == date.today(),
            Booking.status.in_([BookingStatus.CONFIRMED, BookingStatus.PENDING]),
        ).all()

    def get_today_departures(self, hotel_id: int) -> List[Booking]:
        """Get today's expected departures."""
        return self.db.query(Booking).filter(
            Booking.hotel_id == hotel_id,
            Booking.check_out_date == date.today(),
            Booking.status == BookingStatus.CHECKED_IN,
        ).all()

    def get_occupancy_rate(self, hotel_id: int, target_date: date = None) -> float:
        """Calculate occupancy rate for a given date."""
        if target_date is None:
            target_date = date.today()

        total_rooms = self.db.query(Room).filter(
            Room.hotel_id == hotel_id,
            Room.is_active == True,
        ).count()

        if total_rooms == 0:
            return 0.0

        occupied = self.db.query(Booking).filter(
            Booking.hotel_id == hotel_id,
            Booking.check_in_date <= target_date,
            Booking.check_out_date > target_date,
            Booking.status.in_([
                BookingStatus.CONFIRMED,
                BookingStatus.CHECKED_IN,
            ]),
        ).count()

        return (occupied / total_rooms) * 100
