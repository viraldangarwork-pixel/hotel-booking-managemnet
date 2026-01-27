"""Settings models for theme and hotel configuration."""

from sqlalchemy import Column, String, Text, Integer, ForeignKey, Boolean, JSON
from sqlalchemy.orm import relationship

from .base import BaseModel


class ThemeSettings(BaseModel):
    """Theme configuration for hotels."""

    __tablename__ = "theme_settings"

    hotel_id = Column(Integer, ForeignKey("hotels.id"), nullable=False, unique=True)

    # Colors
    primary_color = Column(String(7), default="#2563eb")
    secondary_color = Column(String(7), default="#64748b")
    accent_color = Column(String(7), default="#f59e0b")
    success_color = Column(String(7), default="#10b981")
    warning_color = Column(String(7), default="#f59e0b")
    error_color = Column(String(7), default="#ef4444")

    # Background colors
    background_color = Column(String(7), default="#ffffff")
    surface_color = Column(String(7), default="#f8fafc")
    card_color = Column(String(7), default="#ffffff")

    # Text colors
    text_primary = Column(String(7), default="#1e293b")
    text_secondary = Column(String(7), default="#64748b")

    # Dark mode colors
    dark_background = Column(String(7), default="#0f172a")
    dark_surface = Column(String(7), default="#1e293b")
    dark_card = Column(String(7), default="#334155")
    dark_text_primary = Column(String(7), default="#f8fafc")
    dark_text_secondary = Column(String(7), default="#94a3b8")

    # Typography
    font_family = Column(String(100), default="Inter, sans-serif")
    font_size_base = Column(String(10), default="16px")
    font_weight_normal = Column(String(10), default="400")
    font_weight_medium = Column(String(10), default="500")
    font_weight_bold = Column(String(10), default="700")

    # Spacing & Layout
    border_radius_sm = Column(String(10), default="4px")
    border_radius_md = Column(String(10), default="8px")
    border_radius_lg = Column(String(10), default="12px")
    border_radius_xl = Column(String(10), default="16px")

    spacing_unit = Column(String(10), default="4px")

    # Shadows
    shadow_sm = Column(String(100), default="0 1px 2px rgba(0,0,0,0.05)")
    shadow_md = Column(String(100), default="0 4px 6px rgba(0,0,0,0.1)")
    shadow_lg = Column(String(100), default="0 10px 15px rgba(0,0,0,0.1)")

    # Branding
    logo_url = Column(String(500), nullable=True)
    logo_dark_url = Column(String(500), nullable=True)
    favicon_url = Column(String(500), nullable=True)
    brand_name = Column(String(255), nullable=True)

    # Custom CSS (advanced)
    custom_css = Column(Text, nullable=True)

    # Relationships
    hotel = relationship("Hotel", back_populates="theme_settings")

    def __repr__(self):
        return f"<ThemeSettings hotel_id={self.hotel_id}>"

    def to_css_variables(self, dark_mode: bool = False):
        """Convert to CSS variables dictionary."""
        if dark_mode:
            return {
                "--color-primary": self.primary_color,
                "--color-secondary": self.secondary_color,
                "--color-accent": self.accent_color,
                "--color-success": self.success_color,
                "--color-warning": self.warning_color,
                "--color-error": self.error_color,
                "--color-background": self.dark_background,
                "--color-surface": self.dark_surface,
                "--color-card": self.dark_card,
                "--color-text-primary": self.dark_text_primary,
                "--color-text-secondary": self.dark_text_secondary,
                "--font-family": self.font_family,
                "--font-size-base": self.font_size_base,
                "--border-radius-sm": self.border_radius_sm,
                "--border-radius-md": self.border_radius_md,
                "--border-radius-lg": self.border_radius_lg,
                "--border-radius-xl": self.border_radius_xl,
                "--spacing-unit": self.spacing_unit,
                "--shadow-sm": self.shadow_sm,
                "--shadow-md": self.shadow_md,
                "--shadow-lg": self.shadow_lg,
            }
        return {
            "--color-primary": self.primary_color,
            "--color-secondary": self.secondary_color,
            "--color-accent": self.accent_color,
            "--color-success": self.success_color,
            "--color-warning": self.warning_color,
            "--color-error": self.error_color,
            "--color-background": self.background_color,
            "--color-surface": self.surface_color,
            "--color-card": self.card_color,
            "--color-text-primary": self.text_primary,
            "--color-text-secondary": self.text_secondary,
            "--font-family": self.font_family,
            "--font-size-base": self.font_size_base,
            "--border-radius-sm": self.border_radius_sm,
            "--border-radius-md": self.border_radius_md,
            "--border-radius-lg": self.border_radius_lg,
            "--border-radius-xl": self.border_radius_xl,
            "--spacing-unit": self.spacing_unit,
            "--shadow-sm": self.shadow_sm,
            "--shadow-md": self.shadow_md,
            "--shadow-lg": self.shadow_lg,
        }


class HotelSettings(BaseModel):
    """General hotel settings and configuration."""

    __tablename__ = "hotel_settings"

    hotel_id = Column(Integer, ForeignKey("hotels.id"), nullable=False, unique=True)

    # Booking settings
    allow_same_day_booking = Column(Boolean, default=True)
    min_advance_booking_days = Column(Integer, default=0)
    max_advance_booking_days = Column(Integer, default=365)
    booking_confirmation_required = Column(Boolean, default=False)

    # Cancellation policy
    free_cancellation_hours = Column(Integer, default=24)
    cancellation_fee_percent = Column(Integer, default=0)

    # Check-in/out
    early_check_in_charge = Column(Integer, default=0)  # Per hour
    late_check_out_charge = Column(Integer, default=0)  # Per hour

    # Payment settings
    require_advance_payment = Column(Boolean, default=False)
    advance_payment_percent = Column(Integer, default=0)
    accepted_payment_methods = Column(JSON, default=["cash", "card", "upi"])

    # Notification settings
    send_booking_confirmation_email = Column(Boolean, default=True)
    send_booking_confirmation_whatsapp = Column(Boolean, default=True)
    send_check_in_reminder = Column(Boolean, default=True)
    reminder_hours_before = Column(Integer, default=24)

    # WhatsApp bot settings
    whatsapp_bot_enabled = Column(Boolean, default=True)
    whatsapp_bot_languages = Column(JSON, default=["en"])
    whatsapp_auto_reply_enabled = Column(Boolean, default=True)
    whatsapp_working_hours = Column(JSON, default={"start": "09:00", "end": "21:00"})

    # AI settings
    ai_assistant_enabled = Column(Boolean, default=True)
    ai_auto_suggestions = Column(Boolean, default=True)

    # Seasonal pricing rules
    seasonal_pricing = Column(JSON, default=list)

    # Relationships
    hotel = relationship("Hotel", back_populates="settings")

    def __repr__(self):
        return f"<HotelSettings hotel_id={self.hotel_id}>"
