"""Helper utility functions."""

import random
import string
import re
from datetime import date, datetime
from typing import Optional, Tuple
from decimal import Decimal


def generate_ref_code(prefix: str = "", length: int = 8) -> str:
    """Generate a unique reference code."""
    timestamp = datetime.now().strftime("%y%m%d")
    random_str = "".join(random.choices(string.ascii_uppercase + string.digits, k=length - 6))
    return f"{prefix}{timestamp}{random_str}"


def format_currency(
    amount: Decimal | float,
    currency: str = "INR",
    symbol: str = "₹",
) -> str:
    """Format amount as currency string."""
    if isinstance(amount, Decimal):
        amount = float(amount)
    return f"{symbol}{amount:,.2f}"


def format_date(d: date | datetime | str, format_str: str = "%d %b %Y") -> str:
    """Format date to string."""
    if isinstance(d, str):
        d = datetime.fromisoformat(d)
    if isinstance(d, datetime):
        d = d.date()
    return d.strftime(format_str)


def format_datetime(
    dt: datetime | str,
    format_str: str = "%d %b %Y, %I:%M %p",
) -> str:
    """Format datetime to string."""
    if isinstance(dt, str):
        dt = datetime.fromisoformat(dt)
    return dt.strftime(format_str)


def calculate_nights(check_in: date, check_out: date) -> int:
    """Calculate number of nights between dates."""
    return (check_out - check_in).days


def validate_date_range(
    check_in: date,
    check_out: date,
    allow_same_day: bool = False,
) -> Tuple[bool, Optional[str]]:
    """Validate check-in and check-out date range."""
    today = date.today()

    if check_in < today:
        return False, "Check-in date cannot be in the past"

    if allow_same_day:
        if check_out < check_in:
            return False, "Check-out date cannot be before check-in date"
    else:
        if check_out <= check_in:
            return False, "Check-out date must be after check-in date"

    return True, None


def sanitize_phone(phone: str) -> str:
    """Sanitize phone number - remove non-numeric characters."""
    # Remove all non-numeric characters except +
    cleaned = re.sub(r"[^\d+]", "", phone)

    # If starts with +, keep it
    if cleaned.startswith("+"):
        return cleaned

    # If it's an Indian number without country code
    if len(cleaned) == 10:
        return f"+91{cleaned}"

    return cleaned


def mask_email(email: str) -> str:
    """Mask email address for privacy."""
    if not email or "@" not in email:
        return email

    local, domain = email.split("@")

    if len(local) <= 2:
        masked_local = local[0] + "*"
    else:
        masked_local = local[0] + "*" * (len(local) - 2) + local[-1]

    return f"{masked_local}@{domain}"


def mask_phone(phone: str) -> str:
    """Mask phone number for privacy."""
    if not phone:
        return phone

    # Keep first 4 and last 2 digits
    if len(phone) >= 6:
        return phone[:4] + "*" * (len(phone) - 6) + phone[-2:]

    return phone


def parse_date(date_str: str) -> Optional[date]:
    """Parse date string to date object."""
    formats = [
        "%Y-%m-%d",
        "%d-%m-%Y",
        "%d/%m/%Y",
        "%Y/%m/%d",
        "%d %b %Y",
        "%d %B %Y",
    ]

    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt).date()
        except ValueError:
            continue

    return None


def truncate_string(s: str, max_length: int = 50, suffix: str = "...") -> str:
    """Truncate string to max length."""
    if len(s) <= max_length:
        return s
    return s[: max_length - len(suffix)] + suffix


def slugify(text: str) -> str:
    """Convert text to URL-safe slug."""
    # Convert to lowercase
    text = text.lower()
    # Replace spaces with hyphens
    text = re.sub(r"\s+", "-", text)
    # Remove non-alphanumeric characters except hyphens
    text = re.sub(r"[^a-z0-9-]", "", text)
    # Remove multiple consecutive hyphens
    text = re.sub(r"-+", "-", text)
    # Remove leading/trailing hyphens
    text = text.strip("-")
    return text


def calculate_age(birth_date: date) -> int:
    """Calculate age from birth date."""
    today = date.today()
    age = today.year - birth_date.year
    if (today.month, today.day) < (birth_date.month, birth_date.day):
        age -= 1
    return age
