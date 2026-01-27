"""Settings endpoints for theme and hotel configuration."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user, require_roles
from app.models.user import User
from app.models.settings import ThemeSettings, HotelSettings
from app.schemas.settings import (
    ThemeSettingsUpdate,
    ThemeSettingsResponse,
    HotelSettingsUpdate,
    HotelSettingsResponse,
)

router = APIRouter()


# ============ Theme Settings ============

@router.get("/theme/{hotel_id}", response_model=ThemeSettingsResponse)
def get_theme_settings(
    hotel_id: int,
    db: Session = Depends(get_db),
):
    """Get theme settings for a hotel (public endpoint for frontend)."""
    settings = db.query(ThemeSettings).filter(
        ThemeSettings.hotel_id == hotel_id
    ).first()

    if not settings:
        # Create default settings if not exists
        settings = ThemeSettings(hotel_id=hotel_id)
        db.add(settings)
        db.commit()
        db.refresh(settings)

    return settings


@router.put("/theme/{hotel_id}", response_model=ThemeSettingsResponse)
def update_theme_settings(
    hotel_id: int,
    theme_data: ThemeSettingsUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "superadmin")),
):
    """Update theme settings for a hotel."""
    settings = db.query(ThemeSettings).filter(
        ThemeSettings.hotel_id == hotel_id
    ).first()

    if not settings:
        settings = ThemeSettings(hotel_id=hotel_id)
        db.add(settings)

    update_data = theme_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(settings, key, value)

    db.commit()
    db.refresh(settings)

    return settings


@router.get("/theme/{hotel_id}/css-variables")
def get_css_variables(
    hotel_id: int,
    dark_mode: bool = False,
    db: Session = Depends(get_db),
):
    """Get CSS variables for frontend theming."""
    settings = db.query(ThemeSettings).filter(
        ThemeSettings.hotel_id == hotel_id
    ).first()

    if not settings:
        settings = ThemeSettings(hotel_id=hotel_id)

    return settings.to_css_variables(dark_mode=dark_mode)


@router.post("/theme/{hotel_id}/reset", response_model=ThemeSettingsResponse)
def reset_theme_settings(
    hotel_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "superadmin")),
):
    """Reset theme settings to defaults."""
    settings = db.query(ThemeSettings).filter(
        ThemeSettings.hotel_id == hotel_id
    ).first()

    if settings:
        db.delete(settings)

    # Create new with defaults
    settings = ThemeSettings(hotel_id=hotel_id)
    db.add(settings)
    db.commit()
    db.refresh(settings)

    return settings


# ============ Hotel Settings ============

@router.get("/hotel/{hotel_id}", response_model=HotelSettingsResponse)
def get_hotel_settings(
    hotel_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get hotel settings."""
    settings = db.query(HotelSettings).filter(
        HotelSettings.hotel_id == hotel_id
    ).first()

    if not settings:
        settings = HotelSettings(hotel_id=hotel_id)
        db.add(settings)
        db.commit()
        db.refresh(settings)

    return settings


@router.put("/hotel/{hotel_id}", response_model=HotelSettingsResponse)
def update_hotel_settings(
    hotel_id: int,
    settings_data: HotelSettingsUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "manager", "superadmin")),
):
    """Update hotel settings."""
    settings = db.query(HotelSettings).filter(
        HotelSettings.hotel_id == hotel_id
    ).first()

    if not settings:
        settings = HotelSettings(hotel_id=hotel_id)
        db.add(settings)

    update_data = settings_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(settings, key, value)

    db.commit()
    db.refresh(settings)

    return settings


@router.get("/hotel/{hotel_id}/whatsapp", response_model=dict)
def get_whatsapp_settings(
    hotel_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get WhatsApp bot settings."""
    settings = db.query(HotelSettings).filter(
        HotelSettings.hotel_id == hotel_id
    ).first()

    if not settings:
        settings = HotelSettings(hotel_id=hotel_id)

    return {
        "whatsapp_bot_enabled": settings.whatsapp_bot_enabled,
        "whatsapp_bot_languages": settings.whatsapp_bot_languages,
        "whatsapp_auto_reply_enabled": settings.whatsapp_auto_reply_enabled,
        "whatsapp_working_hours": settings.whatsapp_working_hours,
    }


@router.put("/hotel/{hotel_id}/whatsapp", response_model=dict)
def update_whatsapp_settings(
    hotel_id: int,
    whatsapp_bot_enabled: bool = None,
    whatsapp_bot_languages: list = None,
    whatsapp_auto_reply_enabled: bool = None,
    whatsapp_working_hours: dict = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "superadmin")),
):
    """Update WhatsApp bot settings."""
    settings = db.query(HotelSettings).filter(
        HotelSettings.hotel_id == hotel_id
    ).first()

    if not settings:
        settings = HotelSettings(hotel_id=hotel_id)
        db.add(settings)

    if whatsapp_bot_enabled is not None:
        settings.whatsapp_bot_enabled = whatsapp_bot_enabled
    if whatsapp_bot_languages is not None:
        settings.whatsapp_bot_languages = whatsapp_bot_languages
    if whatsapp_auto_reply_enabled is not None:
        settings.whatsapp_auto_reply_enabled = whatsapp_auto_reply_enabled
    if whatsapp_working_hours is not None:
        settings.whatsapp_working_hours = whatsapp_working_hours

    db.commit()
    db.refresh(settings)

    return {
        "whatsapp_bot_enabled": settings.whatsapp_bot_enabled,
        "whatsapp_bot_languages": settings.whatsapp_bot_languages,
        "whatsapp_auto_reply_enabled": settings.whatsapp_auto_reply_enabled,
        "whatsapp_working_hours": settings.whatsapp_working_hours,
    }


@router.get("/hotel/{hotel_id}/ai", response_model=dict)
def get_ai_settings(
    hotel_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get AI assistant settings."""
    settings = db.query(HotelSettings).filter(
        HotelSettings.hotel_id == hotel_id
    ).first()

    if not settings:
        settings = HotelSettings(hotel_id=hotel_id)

    return {
        "ai_assistant_enabled": settings.ai_assistant_enabled,
        "ai_auto_suggestions": settings.ai_auto_suggestions,
    }


@router.put("/hotel/{hotel_id}/ai", response_model=dict)
def update_ai_settings(
    hotel_id: int,
    ai_assistant_enabled: bool = None,
    ai_auto_suggestions: bool = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "superadmin")),
):
    """Update AI assistant settings."""
    settings = db.query(HotelSettings).filter(
        HotelSettings.hotel_id == hotel_id
    ).first()

    if not settings:
        settings = HotelSettings(hotel_id=hotel_id)
        db.add(settings)

    if ai_assistant_enabled is not None:
        settings.ai_assistant_enabled = ai_assistant_enabled
    if ai_auto_suggestions is not None:
        settings.ai_auto_suggestions = ai_auto_suggestions

    db.commit()
    db.refresh(settings)

    return {
        "ai_assistant_enabled": settings.ai_assistant_enabled,
        "ai_auto_suggestions": settings.ai_auto_suggestions,
    }
