"""Room service for business logic."""

from typing import Optional, List, Dict
from datetime import date
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.room import Room, RoomType, RoomStatus
from app.models.booking import Booking, BookingStatus
from app.models.hotel import Hotel


class RoomService:
    """Service class for room operations."""

    def __init__(self, db: Session):
        self.db = db

    def get_rooms_by_floor(self, hotel_id: int) -> Dict[int, List[Room]]:
        """Get rooms grouped by floor."""
        rooms = self.db.query(Room).filter(
            Room.hotel_id == hotel_id,
            Room.is_active == True,
        ).order_by(Room.floor, Room.room_number).all()

        grouped = {}
        for room in rooms:
            if room.floor not in grouped:
                grouped[room.floor] = []
            grouped[room.floor].append(room)

        return grouped

    def get_room_status_counts(self, hotel_id: int) -> Dict[str, int]:
        """Get count of rooms by status."""
        counts = self.db.query(
            Room.status, func.count(Room.id)
        ).filter(
            Room.hotel_id == hotel_id,
            Room.is_active == True,
        ).group_by(Room.status).all()

        result = {status.value: 0 for status in RoomStatus}
        for status, count in counts:
            result[status.value] = count

        return result

    def update_room_status(self, room_id: int, status: RoomStatus) -> Room:
        """Update room status."""
        room = self.db.query(Room).filter(Room.id == room_id).first()
        if not room:
            raise ValueError("Room not found")

        room.status = status
        self.db.commit()
        self.db.refresh(room)

        return room

    def bulk_update_cleaning_status(self, hotel_id: int) -> int:
        """Mark all cleaning rooms as available (after housekeeping completes)."""
        result = self.db.query(Room).filter(
            Room.hotel_id == hotel_id,
            Room.status == RoomStatus.CLEANING,
        ).update({Room.status: RoomStatus.AVAILABLE})

        self.db.commit()
        return result

    def get_room_type_availability(
        self,
        hotel_id: int,
        check_in_date: date,
        check_out_date: date,
    ) -> List[Dict]:
        """Get availability count by room type."""
        room_types = self.db.query(RoomType).filter(
            RoomType.hotel_id == hotel_id,
            RoomType.is_active == True,
        ).all()

        result = []
        for rt in room_types:
            # Total rooms of this type
            total = self.db.query(Room).filter(
                Room.room_type_id == rt.id,
                Room.is_active == True,
                Room.status != RoomStatus.MAINTENANCE,
            ).count()

            # Booked rooms for these dates
            booked = self.db.query(Booking).join(Room).filter(
                Room.room_type_id == rt.id,
                Booking.status.in_([
                    BookingStatus.CONFIRMED,
                    BookingStatus.CHECKED_IN,
                    BookingStatus.PENDING,
                ]),
                Booking.check_in_date < check_out_date,
                Booking.check_out_date > check_in_date,
            ).count()

            result.append({
                "room_type_id": rt.id,
                "room_type_name": rt.name,
                "total_rooms": total,
                "available_rooms": total - booked,
                "base_price": float(rt.base_price),
            })

        return result

    def create_room(
        self,
        hotel_id: int,
        room_type_id: int,
        room_number: str,
        floor: int = 1,
        notes: Optional[str] = None,
        custom_price: Optional[float] = None,
    ) -> Room:
        """Create a new room."""
        # Check if room number exists
        existing = self.db.query(Room).filter(
            Room.hotel_id == hotel_id,
            Room.room_number == room_number,
        ).first()

        if existing:
            raise ValueError("Room number already exists")

        room = Room(
            hotel_id=hotel_id,
            room_type_id=room_type_id,
            room_number=room_number,
            floor=floor,
            notes=notes,
            custom_price=custom_price,
            status=RoomStatus.AVAILABLE,
        )

        self.db.add(room)
        self.db.commit()
        self.db.refresh(room)

        # Update hotel total rooms
        self._update_hotel_room_count(hotel_id)

        return room

    def create_room_type(
        self,
        hotel_id: int,
        name: str,
        base_price: float,
        max_occupancy: int = 2,
        description: Optional[str] = None,
        amenities: Optional[List[str]] = None,
    ) -> RoomType:
        """Create a new room type."""
        room_type = RoomType(
            hotel_id=hotel_id,
            name=name,
            base_price=base_price,
            max_occupancy=max_occupancy,
            description=description,
            amenities=amenities or [],
        )

        self.db.add(room_type)
        self.db.commit()
        self.db.refresh(room_type)

        return room_type

    def _update_hotel_room_count(self, hotel_id: int):
        """Update hotel's total room count."""
        count = self.db.query(Room).filter(
            Room.hotel_id == hotel_id,
            Room.is_active == True,
        ).count()

        hotel = self.db.query(Hotel).filter(Hotel.id == hotel_id).first()
        if hotel:
            hotel.total_rooms = count
            self.db.commit()

    def get_maintenance_rooms(self, hotel_id: int) -> List[Room]:
        """Get all rooms under maintenance."""
        return self.db.query(Room).filter(
            Room.hotel_id == hotel_id,
            Room.status == RoomStatus.MAINTENANCE,
        ).all()

    def set_room_maintenance(
        self,
        room_id: int,
        notes: Optional[str] = None,
    ) -> Room:
        """Set room to maintenance status."""
        room = self.db.query(Room).filter(Room.id == room_id).first()
        if not room:
            raise ValueError("Room not found")

        room.status = RoomStatus.MAINTENANCE
        if notes:
            room.notes = notes

        self.db.commit()
        self.db.refresh(room)

        return room
