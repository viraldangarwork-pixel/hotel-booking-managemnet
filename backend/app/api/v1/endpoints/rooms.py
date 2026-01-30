"""Room management endpoints."""

from typing import List, Optional
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.core.database import get_db
from app.core.security import get_current_user, require_roles
from app.models.user import User
from app.models.room import Room, RoomType, RoomStatus
from app.models.booking import Booking, BookingStatus
from app.schemas.room import (
    RoomCreate,
    RoomUpdate,
    RoomResponse,
    RoomTypeCreate,
    RoomTypeUpdate,
    RoomTypeResponse,
)

router = APIRouter()


# ============ Room Types ============

@router.get("/types", response_model=List[RoomTypeResponse])
def list_room_types(
    hotel_id: int,
    is_active: bool = True,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all room types for a hotel."""
    query = db.query(RoomType).filter(
        RoomType.hotel_id == hotel_id,
        RoomType.is_active == is_active,
    )
    return query.all()


@router.get("/types/{room_type_id}", response_model=RoomTypeResponse)
def get_room_type(
    room_type_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get room type by ID."""
    room_type = db.query(RoomType).filter(RoomType.id == room_type_id).first()
    if not room_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room type not found",
        )
    return room_type


@router.post("/types", response_model=RoomTypeResponse, status_code=status.HTTP_201_CREATED)
def create_room_type(
    room_type_data: RoomTypeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "manager", "superadmin")),
):
    """Create a new room type."""
    room_type = RoomType(**room_type_data.model_dump())
    db.add(room_type)
    db.commit()
    db.refresh(room_type)
    return room_type


@router.put("/types/{room_type_id}", response_model=RoomTypeResponse)
def update_room_type(
    room_type_id: int,
    room_type_data: RoomTypeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "manager", "superadmin")),
):
    """Update room type."""
    room_type = db.query(RoomType).filter(RoomType.id == room_type_id).first()
    if not room_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room type not found",
        )

    update_data = room_type_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(room_type, key, value)

    db.commit()
    db.refresh(room_type)
    return room_type


@router.delete("/types/{room_type_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_room_type(
    room_type_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "superadmin")),
):
    """Delete room type (soft delete)."""
    room_type = db.query(RoomType).filter(RoomType.id == room_type_id).first()
    if not room_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room type not found",
        )

    room_type.is_active = False
    db.commit()
    return None


# ============ Rooms ============

@router.get("/", response_model=List[RoomResponse])
def list_rooms(
    hotel_id: int,
    room_type_id: Optional[int] = None,
    floor: Optional[int] = None,
    status: Optional[RoomStatus] = None,
    is_active: bool = True,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all rooms for a hotel."""
    query = db.query(Room).filter(
        Room.hotel_id == hotel_id,
        Room.is_active == is_active,
    )

    if room_type_id:
        query = query.filter(Room.room_type_id == room_type_id)
    if floor:
        query = query.filter(Room.floor == floor)
    if status:
        query = query.filter(Room.status == status)

    rooms = query.all()

    # Load room types
    for room in rooms:
        room.room_type = db.query(RoomType).filter(RoomType.id == room.room_type_id).first()

    return rooms


@router.get("/availability", response_model=List[RoomResponse])
def check_availability(
    hotel_id: int,
    check_in_date: date,
    check_out_date: date,
    room_type_id: Optional[int] = None,
    adults: int = 1,
    children: int = 0,
    db: Session = Depends(get_db),
):
    """Check room availability for given dates."""
    # Get all active rooms
    query = db.query(Room).filter(
        Room.hotel_id == hotel_id,
        Room.is_active == True,
        Room.status != RoomStatus.maintenance,
    )

    if room_type_id:
        query = query.filter(Room.room_type_id == room_type_id)

    rooms = query.all()

    # Get bookings that overlap with the requested dates
    booked_room_ids = db.query(Booking.room_id).filter(
        Booking.hotel_id == hotel_id,
        Booking.status.in_([
            BookingStatus.confirmed,
            BookingStatus.checked_in,
            BookingStatus.pending,
        ]),
        and_(
            Booking.check_in_date < check_out_date,
            Booking.check_out_date > check_in_date,
        ),
    ).all()
    booked_room_ids = [r[0] for r in booked_room_ids]

    # Filter out booked rooms
    available_rooms = [r for r in rooms if r.id not in booked_room_ids]

    # Filter by capacity
    result = []
    for room in available_rooms:
        room_type = db.query(RoomType).filter(RoomType.id == room.room_type_id).first()
        if room_type and room_type.max_occupancy >= (adults + children):
            room.room_type = room_type
            result.append(room)

    return result


@router.get("/{room_id}", response_model=RoomResponse)
def get_room(
    room_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get room by ID."""
    room = db.query(Room).filter(Room.id == room_id).first()
    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room not found",
        )

    room.room_type = db.query(RoomType).filter(RoomType.id == room.room_type_id).first()
    return room


@router.post("/", response_model=RoomResponse, status_code=status.HTTP_201_CREATED)
def create_room(
    room_data: RoomCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "manager", "superadmin")),
):
    """Create a new room."""
    # Check if room number already exists in hotel
    existing = db.query(Room).filter(
        Room.hotel_id == room_data.hotel_id,
        Room.room_number == room_data.room_number,
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Room number already exists",
        )

    room = Room(**room_data.model_dump())
    db.add(room)
    db.commit()
    db.refresh(room)

    # Update hotel total rooms
    from app.models.hotel import Hotel
    hotel = db.query(Hotel).filter(Hotel.id == room.hotel_id).first()
    if hotel:
        hotel.total_rooms = db.query(Room).filter(
            Room.hotel_id == hotel.id,
            Room.is_active == True,
        ).count()
        db.commit()

    room.room_type = db.query(RoomType).filter(RoomType.id == room.room_type_id).first()
    return room


@router.put("/{room_id}", response_model=RoomResponse)
def update_room(
    room_id: int,
    room_data: RoomUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "manager", "receptionist", "superadmin")),
):
    """Update room."""
    room = db.query(Room).filter(Room.id == room_id).first()
    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room not found",
        )

    update_data = room_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(room, key, value)

    db.commit()
    db.refresh(room)

    room.room_type = db.query(RoomType).filter(RoomType.id == room.room_type_id).first()
    return room


@router.put("/{room_id}/status", response_model=RoomResponse)
def update_room_status(
    room_id: int,
    status: RoomStatus,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Quick update room status."""
    room = db.query(Room).filter(Room.id == room_id).first()
    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room not found",
        )

    room.status = status
    db.commit()
    db.refresh(room)

    room.room_type = db.query(RoomType).filter(RoomType.id == room.room_type_id).first()
    return room


@router.delete("/{room_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_room(
    room_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "superadmin")),
):
    """Delete room (soft delete)."""
    room = db.query(Room).filter(Room.id == room_id).first()
    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room not found",
        )

    room.is_active = False
    db.commit()

    # Update hotel total rooms
    from app.models.hotel import Hotel
    hotel = db.query(Hotel).filter(Hotel.id == room.hotel_id).first()
    if hotel:
        hotel.total_rooms = db.query(Room).filter(
            Room.hotel_id == hotel.id,
            Room.is_active == True,
        ).count()
        db.commit()

    return None
