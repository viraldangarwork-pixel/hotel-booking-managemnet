"""Hotel management endpoints."""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user, require_roles
from app.models.user import User
from app.models.hotel import Hotel
from app.models.settings import ThemeSettings, HotelSettings
from app.schemas.hotel import HotelCreate, HotelUpdate, HotelResponse

router = APIRouter()


@router.get("/", response_model=List[HotelResponse])
def list_hotels(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    is_active: bool = True,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all hotels."""
    query = db.query(Hotel).filter(Hotel.is_active == is_active)

    # Non-superusers can only see their hotel
    if not current_user.is_superuser and current_user.hotel_id:
        query = query.filter(Hotel.id == current_user.hotel_id)

    return query.offset(skip).limit(limit).all()


@router.get("/{hotel_id}", response_model=HotelResponse)
def get_hotel(
    hotel_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get hotel by ID."""
    hotel = db.query(Hotel).filter(Hotel.id == hotel_id).first()
    if not hotel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hotel not found",
        )

    # Check permissions
    if not current_user.is_superuser and current_user.hotel_id != hotel_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )

    return hotel


@router.post("/", response_model=HotelResponse, status_code=status.HTTP_201_CREATED)
def create_hotel(
    hotel_data: HotelCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("superadmin")),
):
    """Create a new hotel (superadmin only)."""
    hotel = Hotel(**hotel_data.model_dump())
    db.add(hotel)
    db.flush()

    # Create default theme settings
    theme_settings = ThemeSettings(
        hotel_id=hotel.id,
        brand_name=hotel.name,
    )
    db.add(theme_settings)

    # Create default hotel settings
    hotel_settings = HotelSettings(hotel_id=hotel.id)
    db.add(hotel_settings)

    db.commit()
    db.refresh(hotel)

    return hotel


@router.put("/{hotel_id}", response_model=HotelResponse)
def update_hotel(
    hotel_id: int,
    hotel_data: HotelUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "superadmin")),
):
    """Update hotel."""
    hotel = db.query(Hotel).filter(Hotel.id == hotel_id).first()
    if not hotel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hotel not found",
        )

    # Check permissions
    if not current_user.is_superuser and current_user.hotel_id != hotel_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )

    update_data = hotel_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(hotel, key, value)

    db.commit()
    db.refresh(hotel)

    return hotel


@router.delete("/{hotel_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_hotel(
    hotel_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("superadmin")),
):
    """Delete hotel (superadmin only)."""
    hotel = db.query(Hotel).filter(Hotel.id == hotel_id).first()
    if not hotel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hotel not found",
        )

    # Soft delete by setting is_active to False
    hotel.is_active = False
    db.commit()

    return None
