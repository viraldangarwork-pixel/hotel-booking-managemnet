"""Validation utility functions."""

import re
from datetime import date, datetime
from typing import Optional, Tuple
from decimal import Decimal, InvalidOperation


def validate_email(email: str) -> Tuple[bool, Optional[str]]:
    """Validate email address format."""
    if not email:
        return False, "Email is required"

    # Basic email regex pattern
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"

    if not re.match(pattern, email):
        return False, "Invalid email format"

    return True, None


def validate_phone(phone: str, country_code: str = "91") -> Tuple[bool, Optional[str]]:
    """Validate phone number format."""
    if not phone:
        return False, "Phone number is required"

    # Remove all non-numeric characters except +
    cleaned = re.sub(r"[^\d+]", "", phone)

    # Check if it starts with + followed by country code
    if cleaned.startswith("+"):
        # International format: +91XXXXXXXXXX
        if cleaned.startswith(f"+{country_code}"):
            number_part = cleaned[len(country_code) + 1:]
        else:
            number_part = cleaned[1:]
    else:
        number_part = cleaned

    # Indian phone numbers should be 10 digits
    if country_code == "91" and len(number_part) != 10:
        return False, "Phone number must be 10 digits"

    # General validation: at least 7 digits
    if len(number_part) < 7:
        return False, "Phone number too short"

    if len(number_part) > 15:
        return False, "Phone number too long"

    return True, None


def validate_date(
    date_value: date | str,
    min_date: Optional[date] = None,
    max_date: Optional[date] = None,
    allow_past: bool = True,
    allow_future: bool = True,
) -> Tuple[bool, Optional[str]]:
    """Validate date value."""
    if isinstance(date_value, str):
        try:
            date_value = datetime.fromisoformat(date_value).date()
        except ValueError:
            return False, "Invalid date format"

    today = date.today()

    if not allow_past and date_value < today:
        return False, "Date cannot be in the past"

    if not allow_future and date_value > today:
        return False, "Date cannot be in the future"

    if min_date and date_value < min_date:
        return False, f"Date must be on or after {min_date}"

    if max_date and date_value > max_date:
        return False, f"Date must be on or before {max_date}"

    return True, None


def validate_price(
    price: float | Decimal | str,
    min_value: float = 0,
    max_value: Optional[float] = None,
) -> Tuple[bool, Optional[str]]:
    """Validate price/amount value."""
    try:
        if isinstance(price, str):
            price = Decimal(price)
        elif isinstance(price, float):
            price = Decimal(str(price))
    except (InvalidOperation, ValueError):
        return False, "Invalid price format"

    if price < min_value:
        return False, f"Price must be at least {min_value}"

    if max_value is not None and price > max_value:
        return False, f"Price cannot exceed {max_value}"

    return True, None


def validate_string_length(
    value: str,
    min_length: int = 0,
    max_length: int = 255,
    field_name: str = "Value",
) -> Tuple[bool, Optional[str]]:
    """Validate string length."""
    if not value and min_length > 0:
        return False, f"{field_name} is required"

    if len(value) < min_length:
        return False, f"{field_name} must be at least {min_length} characters"

    if len(value) > max_length:
        return False, f"{field_name} cannot exceed {max_length} characters"

    return True, None


def validate_id_number(
    id_type: str,
    id_number: str,
) -> Tuple[bool, Optional[str]]:
    """Validate ID document number based on type."""
    if not id_number:
        return False, "ID number is required"

    id_type_lower = id_type.lower()

    # Aadhar card - 12 digits
    if id_type_lower in ["aadhar", "aadhaar"]:
        cleaned = re.sub(r"\D", "", id_number)
        if len(cleaned) != 12:
            return False, "Aadhar number must be 12 digits"

    # PAN card - 10 alphanumeric
    elif id_type_lower == "pan":
        cleaned = id_number.upper().replace(" ", "")
        if not re.match(r"^[A-Z]{5}[0-9]{4}[A-Z]$", cleaned):
            return False, "Invalid PAN number format"

    # Passport - alphanumeric, 8-9 characters
    elif id_type_lower == "passport":
        cleaned = id_number.upper().replace(" ", "")
        if not re.match(r"^[A-Z][0-9]{7,8}$", cleaned):
            return False, "Invalid passport number format"

    # Driving license - varies by state, just basic validation
    elif id_type_lower in ["driving license", "driving_license", "dl"]:
        if len(id_number) < 10:
            return False, "Invalid driving license number"

    return True, None


def validate_gst_number(gst_number: str) -> Tuple[bool, Optional[str]]:
    """Validate GST number format."""
    if not gst_number:
        return True, None  # GST is optional

    cleaned = gst_number.upper().replace(" ", "")

    # GST format: 2 digits state code + 10 char PAN + 1 digit + Z + 1 check digit
    pattern = r"^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z][0-9][Z][0-9A-Z]$"

    if not re.match(pattern, cleaned):
        return False, "Invalid GST number format"

    return True, None


def validate_booking_dates(
    check_in: date,
    check_out: date,
    allow_same_day: bool = False,
    max_advance_days: int = 365,
) -> Tuple[bool, Optional[str]]:
    """Validate booking date range."""
    today = date.today()

    if check_in < today:
        return False, "Check-in date cannot be in the past"

    if (check_in - today).days > max_advance_days:
        return False, f"Cannot book more than {max_advance_days} days in advance"

    if allow_same_day:
        if check_out < check_in:
            return False, "Check-out date cannot be before check-in date"
    else:
        if check_out <= check_in:
            return False, "Check-out date must be after check-in date"

    return True, None
