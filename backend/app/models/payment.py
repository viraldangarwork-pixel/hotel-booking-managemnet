"""Payment model."""

from sqlalchemy import Column, String, Text, Integer, ForeignKey, Enum, Numeric, DateTime
from sqlalchemy.orm import relationship
import enum
from datetime import datetime

from .base import BaseModel


class PaymentStatus(str, enum.Enum):
    """Payment status enum."""

    pending = "pending"
    completed = "completed"
    failed = "failed"
    refunded = "refunded"
    partially_refunded = "partially_refunded"


class PaymentMethod(str, enum.Enum):
    """Payment method enum."""

    cash = "cash"
    card = "card"
    upi = "upi"
    bank_transfer = "bank_transfer"
    cheque = "cheque"
    online = "online"
    wallet = "wallet"


class Payment(BaseModel):
    """Payment model for tracking transactions."""

    __tablename__ = "payments"

    # Generate payment reference
    payment_ref = Column(String(20), unique=True, nullable=False, index=True)

    booking_id = Column(Integer, ForeignKey("bookings.id"), nullable=False)

    # Payment details
    amount = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(3), default="INR", nullable=False)

    method = Column(
        Enum(PaymentMethod), default=PaymentMethod.cash, nullable=False
    )
    status = Column(
        Enum(PaymentStatus), default=PaymentStatus.pending, nullable=False
    )

    # Transaction details
    transaction_id = Column(String(100), nullable=True)  # External payment gateway ID
    gateway = Column(String(50), nullable=True)  # Razorpay, Stripe, etc.

    # For refunds
    refund_amount = Column(Numeric(10, 2), default=0)
    refund_reason = Column(Text, nullable=True)
    refunded_at = Column(DateTime, nullable=True)

    # Notes
    notes = Column(Text, nullable=True)

    # Processed by (staff member)
    processed_by = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Timestamps for payment processing
    paid_at = Column(DateTime, nullable=True)

    # Relationships
    booking = relationship("Booking", back_populates="payments")

    def __repr__(self):
        return f"<Payment {self.payment_ref}>"

    @staticmethod
    def generate_payment_ref():
        """Generate unique payment reference."""
        import random
        import string
        timestamp = datetime.now().strftime("%y%m%d%H%M")
        random_str = "".join(random.choices(string.digits, k=4))
        return f"PAY{timestamp}{random_str}"
