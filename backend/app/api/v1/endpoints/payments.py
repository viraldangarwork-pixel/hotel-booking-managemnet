"""Payment management endpoints."""

from typing import List, Optional
from datetime import datetime
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.payment import Payment, PaymentStatus, PaymentMethod
from app.models.booking import Booking
from app.schemas.payment import PaymentCreate, PaymentResponse, PaymentRefund

router = APIRouter()


@router.get("/", response_model=List[PaymentResponse])
def list_payments(
    booking_id: Optional[int] = None,
    status: Optional[PaymentStatus] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List payments."""
    query = db.query(Payment)

    if booking_id:
        query = query.filter(Payment.booking_id == booking_id)
    if status:
        query = query.filter(Payment.status == status)

    return query.order_by(Payment.created_at.desc()).offset(skip).limit(limit).all()


@router.get("/{payment_id}", response_model=PaymentResponse)
def get_payment(
    payment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get payment by ID."""
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found",
        )
    return payment


@router.get("/ref/{payment_ref}", response_model=PaymentResponse)
def get_payment_by_ref(
    payment_ref: str,
    db: Session = Depends(get_db),
):
    """Get payment by reference number."""
    payment = db.query(Payment).filter(Payment.payment_ref == payment_ref).first()
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found",
        )
    return payment


@router.post("/", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
def create_payment(
    payment_data: PaymentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Record a new payment."""
    # Verify booking exists
    booking = db.query(Booking).filter(Booking.id == payment_data.booking_id).first()
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found",
        )

    # Create payment
    payment = Payment(
        payment_ref=Payment.generate_payment_ref(),
        booking_id=payment_data.booking_id,
        amount=payment_data.amount,
        method=payment_data.method,
        status=PaymentStatus.COMPLETED,
        transaction_id=payment_data.transaction_id,
        gateway=payment_data.gateway,
        notes=payment_data.notes,
        processed_by=current_user.id,
        paid_at=datetime.now(),
    )

    db.add(payment)

    # Update booking payment status
    booking.amount_paid = Decimal(str(booking.amount_paid)) + payment_data.amount
    if booking.amount_paid >= booking.total_amount:
        booking.is_paid = True

    db.commit()
    db.refresh(payment)

    return payment


@router.post("/{payment_id}/refund", response_model=PaymentResponse)
def refund_payment(
    payment_id: int,
    refund_data: PaymentRefund,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Process payment refund."""
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found",
        )

    if payment.status != PaymentStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Payment cannot be refunded",
        )

    if refund_data.refund_amount > payment.amount:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Refund amount exceeds payment amount",
        )

    # Update payment
    payment.refund_amount = refund_data.refund_amount
    payment.refund_reason = refund_data.refund_reason
    payment.refunded_at = datetime.now()

    if refund_data.refund_amount == payment.amount:
        payment.status = PaymentStatus.REFUNDED
    else:
        payment.status = PaymentStatus.PARTIALLY_REFUNDED

    # Update booking
    booking = db.query(Booking).filter(Booking.id == payment.booking_id).first()
    booking.amount_paid = Decimal(str(booking.amount_paid)) - refund_data.refund_amount
    if booking.amount_paid < booking.total_amount:
        booking.is_paid = False

    db.commit()
    db.refresh(payment)

    return payment


@router.get("/booking/{booking_id}/summary")
def get_booking_payment_summary(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get payment summary for a booking."""
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found",
        )

    payments = db.query(Payment).filter(
        Payment.booking_id == booking_id,
        Payment.status.in_([PaymentStatus.COMPLETED, PaymentStatus.PARTIALLY_REFUNDED]),
    ).all()

    total_paid = sum(p.amount - (p.refund_amount or 0) for p in payments)
    balance_due = float(booking.total_amount) - float(total_paid)

    return {
        "booking_id": booking_id,
        "total_amount": float(booking.total_amount),
        "total_paid": float(total_paid),
        "balance_due": balance_due,
        "is_paid": booking.is_paid,
        "payments": payments,
    }
