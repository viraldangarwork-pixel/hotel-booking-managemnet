"""Payment schemas."""

from typing import Optional
from datetime import datetime
from decimal import Decimal
from pydantic import Field

from .base import BaseSchema, IDSchema
from app.models.payment import PaymentStatus, PaymentMethod


class PaymentBase(BaseSchema):
    """Base payment schema."""

    amount: Decimal = Field(..., ge=0)
    method: PaymentMethod = PaymentMethod.cash
    notes: Optional[str] = None


class PaymentCreate(PaymentBase):
    """Schema for creating a payment."""

    booking_id: int
    transaction_id: Optional[str] = None
    gateway: Optional[str] = None


class PaymentRefund(BaseSchema):
    """Schema for refunding a payment."""

    refund_amount: Decimal = Field(..., ge=0)
    refund_reason: Optional[str] = None


class PaymentResponse(IDSchema):
    """Schema for payment response."""

    payment_ref: str
    booking_id: int
    amount: Decimal
    currency: str
    method: PaymentMethod
    status: PaymentStatus
    transaction_id: Optional[str] = None
    gateway: Optional[str] = None
    refund_amount: Decimal
    refund_reason: Optional[str] = None
    refunded_at: Optional[datetime] = None
    notes: Optional[str] = None
    processed_by: Optional[int] = None
    paid_at: Optional[datetime] = None
