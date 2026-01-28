"""Guest service for CRM operations."""

from typing import Optional, List
from datetime import date
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.models.guest import Guest
from app.models.booking import Booking


class GuestService:
    """Service class for guest CRM operations."""

    def __init__(self, db: Session):
        self.db = db

    def search_guests(
        self,
        hotel_id: int,
        query: str,
        limit: int = 10,
    ) -> List[Guest]:
        """Search guests by name, email, or phone."""
        search_term = f"%{query}%"
        return self.db.query(Guest).filter(
            Guest.hotel_id == hotel_id,
            Guest.is_blacklisted == False,
            or_(
                Guest.first_name.ilike(search_term),
                Guest.last_name.ilike(search_term),
                Guest.email.ilike(search_term),
                Guest.phone.ilike(search_term),
            ),
        ).limit(limit).all()

    def find_or_create_guest(
        self,
        hotel_id: int,
        first_name: str,
        last_name: str,
        phone: str,
        email: Optional[str] = None,
        **kwargs,
    ) -> Guest:
        """Find existing guest by phone or create new one."""
        existing = self.db.query(Guest).filter(
            Guest.hotel_id == hotel_id,
            Guest.phone == phone,
        ).first()

        if existing:
            return existing

        guest = Guest(
            hotel_id=hotel_id,
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            email=email,
            **kwargs,
        )

        self.db.add(guest)
        self.db.commit()
        self.db.refresh(guest)

        return guest

    def get_guest_by_phone(
        self,
        hotel_id: int,
        phone: str,
    ) -> Optional[Guest]:
        """Get guest by phone number."""
        return self.db.query(Guest).filter(
            Guest.hotel_id == hotel_id,
            or_(Guest.phone == phone, Guest.whatsapp_number == phone),
        ).first()

    def get_vip_guests(self, hotel_id: int) -> List[Guest]:
        """Get all VIP guests."""
        return self.db.query(Guest).filter(
            Guest.hotel_id == hotel_id,
            Guest.is_vip == True,
            Guest.is_blacklisted == False,
        ).all()

    def get_repeat_guests(
        self,
        hotel_id: int,
        min_stays: int = 2,
    ) -> List[Guest]:
        """Get guests with multiple stays."""
        return self.db.query(Guest).filter(
            Guest.hotel_id == hotel_id,
            Guest.total_stays >= min_stays,
            Guest.is_blacklisted == False,
        ).order_by(Guest.total_stays.desc()).all()

    def toggle_vip_status(self, guest_id: int, is_vip: bool) -> Guest:
        """Toggle guest VIP status."""
        guest = self.db.query(Guest).filter(Guest.id == guest_id).first()
        if not guest:
            raise ValueError("Guest not found")

        guest.is_vip = is_vip

        # Update tags
        tags = guest.tags or []
        if is_vip and "VIP" not in tags:
            tags.append("VIP")
        elif not is_vip and "VIP" in tags:
            tags.remove("VIP")
        guest.tags = tags

        self.db.commit()
        self.db.refresh(guest)

        return guest

    def blacklist_guest(
        self,
        guest_id: int,
        reason: Optional[str] = None,
    ) -> Guest:
        """Blacklist a guest."""
        guest = self.db.query(Guest).filter(Guest.id == guest_id).first()
        if not guest:
            raise ValueError("Guest not found")

        guest.is_blacklisted = True
        if reason:
            guest.notes = (guest.notes or "") + f"\nBlacklisted: {reason}"

        self.db.commit()
        self.db.refresh(guest)

        return guest

    def get_guest_booking_history(self, guest_id: int) -> List[Booking]:
        """Get guest's booking history."""
        return self.db.query(Booking).filter(
            Booking.guest_id == guest_id,
        ).order_by(Booking.created_at.desc()).all()

    def update_guest_preferences(
        self,
        guest_id: int,
        preferences: dict,
    ) -> Guest:
        """Update guest preferences."""
        guest = self.db.query(Guest).filter(Guest.id == guest_id).first()
        if not guest:
            raise ValueError("Guest not found")

        current_prefs = guest.preferences or {}
        current_prefs.update(preferences)
        guest.preferences = current_prefs

        self.db.commit()
        self.db.refresh(guest)

        return guest

    def add_guest_tag(self, guest_id: int, tag: str) -> Guest:
        """Add a tag to guest."""
        guest = self.db.query(Guest).filter(Guest.id == guest_id).first()
        if not guest:
            raise ValueError("Guest not found")

        tags = guest.tags or []
        if tag not in tags:
            tags.append(tag)
            guest.tags = tags
            self.db.commit()
            self.db.refresh(guest)

        return guest

    def remove_guest_tag(self, guest_id: int, tag: str) -> Guest:
        """Remove a tag from guest."""
        guest = self.db.query(Guest).filter(Guest.id == guest_id).first()
        if not guest:
            raise ValueError("Guest not found")

        tags = guest.tags or []
        if tag in tags:
            tags.remove(tag)
            guest.tags = tags
            self.db.commit()
            self.db.refresh(guest)

        return guest

    def get_guests_with_upcoming_bookings(
        self,
        hotel_id: int,
        days: int = 7,
    ) -> List[Guest]:
        """Get guests with upcoming bookings."""
        from datetime import timedelta
        today = date.today()
        end_date = today + timedelta(days=days)

        guest_ids = self.db.query(Booking.guest_id).filter(
            Booking.hotel_id == hotel_id,
            Booking.check_in_date >= today,
            Booking.check_in_date <= end_date,
        ).distinct().all()

        guest_ids = [g[0] for g in guest_ids]

        return self.db.query(Guest).filter(
            Guest.id.in_(guest_ids),
        ).all()
