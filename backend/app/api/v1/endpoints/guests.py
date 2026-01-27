"""Guest CRM endpoints."""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.guest import Guest
from app.schemas.guest import GuestCreate, GuestUpdate, GuestResponse

router = APIRouter()


@router.get("/", response_model=List[GuestResponse])
def list_guests(
    hotel_id: int,
    search: Optional[str] = None,
    is_vip: Optional[bool] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List guests for a hotel."""
    query = db.query(Guest).filter(
        Guest.hotel_id == hotel_id,
        Guest.is_blacklisted == False,
    )

    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                Guest.first_name.ilike(search_term),
                Guest.last_name.ilike(search_term),
                Guest.email.ilike(search_term),
                Guest.phone.ilike(search_term),
            )
        )

    if is_vip is not None:
        query = query.filter(Guest.is_vip == is_vip)

    return query.order_by(Guest.created_at.desc()).offset(skip).limit(limit).all()


@router.get("/search", response_model=List[GuestResponse])
def search_guests(
    hotel_id: int,
    q: str = Query(..., min_length=2),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Search guests by name, email, or phone."""
    search_term = f"%{q}%"
    guests = db.query(Guest).filter(
        Guest.hotel_id == hotel_id,
        or_(
            Guest.first_name.ilike(search_term),
            Guest.last_name.ilike(search_term),
            Guest.email.ilike(search_term),
            Guest.phone.ilike(search_term),
        ),
    ).limit(10).all()

    return guests


@router.get("/vip", response_model=List[GuestResponse])
def list_vip_guests(
    hotel_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List VIP guests."""
    return db.query(Guest).filter(
        Guest.hotel_id == hotel_id,
        Guest.is_vip == True,
    ).all()


@router.get("/{guest_id}", response_model=GuestResponse)
def get_guest(
    guest_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get guest by ID."""
    guest = db.query(Guest).filter(Guest.id == guest_id).first()
    if not guest:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Guest not found",
        )
    return guest


@router.get("/phone/{phone}", response_model=GuestResponse)
def get_guest_by_phone(
    phone: str,
    hotel_id: int,
    db: Session = Depends(get_db),
):
    """Get guest by phone number (for WhatsApp integration)."""
    guest = db.query(Guest).filter(
        Guest.hotel_id == hotel_id,
        or_(Guest.phone == phone, Guest.whatsapp_number == phone),
    ).first()

    if not guest:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Guest not found",
        )
    return guest


@router.post("/", response_model=GuestResponse, status_code=status.HTTP_201_CREATED)
def create_guest(
    guest_data: GuestCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new guest."""
    # Check for existing guest with same phone
    existing = db.query(Guest).filter(
        Guest.hotel_id == guest_data.hotel_id,
        Guest.phone == guest_data.phone,
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Guest with this phone number already exists",
        )

    guest = Guest(**guest_data.model_dump())
    db.add(guest)
    db.commit()
    db.refresh(guest)

    return guest


@router.post("/find-or-create", response_model=GuestResponse)
def find_or_create_guest(
    guest_data: GuestCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Find existing guest by phone or create new one."""
    existing = db.query(Guest).filter(
        Guest.hotel_id == guest_data.hotel_id,
        Guest.phone == guest_data.phone,
    ).first()

    if existing:
        return existing

    guest = Guest(**guest_data.model_dump())
    db.add(guest)
    db.commit()
    db.refresh(guest)

    return guest


@router.put("/{guest_id}", response_model=GuestResponse)
def update_guest(
    guest_id: int,
    guest_data: GuestUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update guest."""
    guest = db.query(Guest).filter(Guest.id == guest_id).first()
    if not guest:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Guest not found",
        )

    update_data = guest_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(guest, key, value)

    db.commit()
    db.refresh(guest)

    return guest


@router.put("/{guest_id}/vip", response_model=GuestResponse)
def toggle_vip_status(
    guest_id: int,
    is_vip: bool,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Toggle guest VIP status."""
    guest = db.query(Guest).filter(Guest.id == guest_id).first()
    if not guest:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Guest not found",
        )

    guest.is_vip = is_vip

    # Update tags
    if is_vip and "VIP" not in (guest.tags or []):
        guest.tags = (guest.tags or []) + ["VIP"]
    elif not is_vip and "VIP" in (guest.tags or []):
        guest.tags = [t for t in guest.tags if t != "VIP"]

    db.commit()
    db.refresh(guest)

    return guest


@router.put("/{guest_id}/blacklist", response_model=GuestResponse)
def toggle_blacklist(
    guest_id: int,
    is_blacklisted: bool,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Toggle guest blacklist status."""
    guest = db.query(Guest).filter(Guest.id == guest_id).first()
    if not guest:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Guest not found",
        )

    guest.is_blacklisted = is_blacklisted
    db.commit()
    db.refresh(guest)

    return guest


@router.delete("/{guest_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_guest(
    guest_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete guest (soft delete by blacklisting)."""
    guest = db.query(Guest).filter(Guest.id == guest_id).first()
    if not guest:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Guest not found",
        )

    # Soft delete
    guest.is_blacklisted = True
    db.commit()

    return None
