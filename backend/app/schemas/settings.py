"""Settings schemas for theme and hotel configuration."""

from typing import Optional, List, Dict, Any

from .base import BaseSchema, IDSchema


class ThemeSettingsUpdate(BaseSchema):
    """Schema for updating theme settings."""

    # Colors
    primary_color: Optional[str] = None
    secondary_color: Optional[str] = None
    accent_color: Optional[str] = None
    success_color: Optional[str] = None
    warning_color: Optional[str] = None
    error_color: Optional[str] = None

    # Background colors
    background_color: Optional[str] = None
    surface_color: Optional[str] = None
    card_color: Optional[str] = None

    # Text colors
    text_primary: Optional[str] = None
    text_secondary: Optional[str] = None

    # Dark mode colors
    dark_background: Optional[str] = None
    dark_surface: Optional[str] = None
    dark_card: Optional[str] = None
    dark_text_primary: Optional[str] = None
    dark_text_secondary: Optional[str] = None

    # Typography
    font_family: Optional[str] = None
    font_size_base: Optional[str] = None
    font_weight_normal: Optional[str] = None
    font_weight_medium: Optional[str] = None
    font_weight_bold: Optional[str] = None

    # Spacing & Layout
    border_radius_sm: Optional[str] = None
    border_radius_md: Optional[str] = None
    border_radius_lg: Optional[str] = None
    border_radius_xl: Optional[str] = None
    spacing_unit: Optional[str] = None

    # Shadows
    shadow_sm: Optional[str] = None
    shadow_md: Optional[str] = None
    shadow_lg: Optional[str] = None

    # Branding
    logo_url: Optional[str] = None
    logo_dark_url: Optional[str] = None
    favicon_url: Optional[str] = None
    brand_name: Optional[str] = None

    # Custom CSS
    custom_css: Optional[str] = None


class ThemeSettingsResponse(IDSchema):
    """Schema for theme settings response."""

    hotel_id: int
    primary_color: str
    secondary_color: str
    accent_color: str
    success_color: str
    warning_color: str
    error_color: str
    background_color: str
    surface_color: str
    card_color: str
    text_primary: str
    text_secondary: str
    dark_background: str
    dark_surface: str
    dark_card: str
    dark_text_primary: str
    dark_text_secondary: str
    font_family: str
    font_size_base: str
    font_weight_normal: str
    font_weight_medium: str
    font_weight_bold: str
    border_radius_sm: str
    border_radius_md: str
    border_radius_lg: str
    border_radius_xl: str
    spacing_unit: str
    shadow_sm: str
    shadow_md: str
    shadow_lg: str
    logo_url: Optional[str] = None
    logo_dark_url: Optional[str] = None
    favicon_url: Optional[str] = None
    brand_name: Optional[str] = None
    custom_css: Optional[str] = None


class HotelSettingsUpdate(BaseSchema):
    """Schema for updating hotel settings."""

    # Booking settings
    allow_same_day_booking: Optional[bool] = None
    min_advance_booking_days: Optional[int] = None
    max_advance_booking_days: Optional[int] = None
    booking_confirmation_required: Optional[bool] = None

    # Cancellation policy
    free_cancellation_hours: Optional[int] = None
    cancellation_fee_percent: Optional[int] = None

    # Check-in/out
    early_check_in_charge: Optional[int] = None
    late_check_out_charge: Optional[int] = None

    # Payment settings
    require_advance_payment: Optional[bool] = None
    advance_payment_percent: Optional[int] = None
    accepted_payment_methods: Optional[List[str]] = None

    # Notification settings
    send_booking_confirmation_email: Optional[bool] = None
    send_booking_confirmation_whatsapp: Optional[bool] = None
    send_check_in_reminder: Optional[bool] = None
    reminder_hours_before: Optional[int] = None

    # WhatsApp bot settings
    whatsapp_bot_enabled: Optional[bool] = None
    whatsapp_bot_languages: Optional[List[str]] = None
    whatsapp_auto_reply_enabled: Optional[bool] = None
    whatsapp_working_hours: Optional[Dict[str, str]] = None

    # AI settings
    ai_assistant_enabled: Optional[bool] = None
    ai_auto_suggestions: Optional[bool] = None

    # Seasonal pricing
    seasonal_pricing: Optional[List[Dict[str, Any]]] = None


class HotelSettingsResponse(IDSchema):
    """Schema for hotel settings response."""

    hotel_id: int
    allow_same_day_booking: bool
    min_advance_booking_days: int
    max_advance_booking_days: int
    booking_confirmation_required: bool
    free_cancellation_hours: int
    cancellation_fee_percent: int
    early_check_in_charge: int
    late_check_out_charge: int
    require_advance_payment: bool
    advance_payment_percent: int
    accepted_payment_methods: List[str]
    send_booking_confirmation_email: bool
    send_booking_confirmation_whatsapp: bool
    send_check_in_reminder: bool
    reminder_hours_before: int
    whatsapp_bot_enabled: bool
    whatsapp_bot_languages: List[str]
    whatsapp_auto_reply_enabled: bool
    whatsapp_working_hours: Dict[str, str]
    ai_assistant_enabled: bool
    ai_auto_suggestions: bool
    seasonal_pricing: List[Dict[str, Any]]
