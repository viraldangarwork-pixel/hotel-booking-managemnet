"""Payment service for billing operations."""

from typing import Optional, List
from datetime import datetime, date
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.payment import Payment, PaymentStatus, PaymentMethod
from app.models.booking import Booking


class PaymentService:
    """Service class for payment operations."""

    def __init__(self, db: Session):
        self.db = db

    def record_payment(
        self,
        booking_id: int,
        amount: Decimal,
        method: PaymentMethod = PaymentMethod.CASH,
        transaction_id: Optional[str] = None,
        gateway: Optional[str] = None,
        notes: Optional[str] = None,
        processed_by: Optional[int] = None,
    ) -> Payment:
        """Record a payment for a booking."""
        booking = self.db.query(Booking).filter(Booking.id == booking_id).first()
        if not booking:
            raise ValueError("Booking not found")

        payment = Payment(
            payment_ref=Payment.generate_payment_ref(),
            booking_id=booking_id,
            amount=amount,
            method=method,
            status=PaymentStatus.COMPLETED,
            transaction_id=transaction_id,
            gateway=gateway,
            notes=notes,
            processed_by=processed_by,
            paid_at=datetime.now(),
        )

        self.db.add(payment)

        # Update booking payment status
        booking.amount_paid = Decimal(str(booking.amount_paid)) + amount
        if booking.amount_paid >= booking.total_amount:
            booking.is_paid = True

        self.db.commit()
        self.db.refresh(payment)

        return payment

    def process_refund(
        self,
        payment_id: int,
        refund_amount: Decimal,
        reason: Optional[str] = None,
    ) -> Payment:
        """Process a refund for a payment."""
        payment = self.db.query(Payment).filter(Payment.id == payment_id).first()
        if not payment:
            raise ValueError("Payment not found")

        if payment.status != PaymentStatus.COMPLETED:
            raise ValueError("Payment cannot be refunded")

        if refund_amount > payment.amount:
            raise ValueError("Refund amount exceeds payment amount")

        payment.refund_amount = refund_amount
        payment.refund_reason = reason
        payment.refunded_at = datetime.now()

        if refund_amount == payment.amount:
            payment.status = PaymentStatus.REFUNDED
        else:
            payment.status = PaymentStatus.PARTIALLY_REFUNDED

        # Update booking
        booking = self.db.query(Booking).filter(Booking.id == payment.booking_id).first()
        booking.amount_paid = Decimal(str(booking.amount_paid)) - refund_amount
        if booking.amount_paid < booking.total_amount:
            booking.is_paid = False

        self.db.commit()
        self.db.refresh(payment)

        return payment

    def get_booking_payment_summary(self, booking_id: int) -> dict:
        """Get payment summary for a booking."""
        booking = self.db.query(Booking).filter(Booking.id == booking_id).first()
        if not booking:
            raise ValueError("Booking not found")

        payments = self.db.query(Payment).filter(
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

    def get_daily_revenue(self, hotel_id: int, target_date: date = None) -> Decimal:
        """Get total revenue for a day."""
        if target_date is None:
            target_date = date.today()

        result = self.db.query(func.sum(Payment.amount)).join(
            Booking, Payment.booking_id == Booking.id
        ).filter(
            Booking.hotel_id == hotel_id,
            func.date(Payment.paid_at) == target_date,
            Payment.status == PaymentStatus.COMPLETED,
        ).scalar()

        return result or Decimal(0)

    def get_monthly_revenue(self, hotel_id: int, year: int, month: int) -> Decimal:
        """Get total revenue for a month."""
        from sqlalchemy import extract

        result = self.db.query(func.sum(Payment.amount)).join(
            Booking, Payment.booking_id == Booking.id
        ).filter(
            Booking.hotel_id == hotel_id,
            extract('year', Payment.paid_at) == year,
            extract('month', Payment.paid_at) == month,
            Payment.status == PaymentStatus.COMPLETED,
        ).scalar()

        return result or Decimal(0)

    def get_pending_payments(self, hotel_id: int) -> List[Booking]:
        """Get bookings with pending payments."""
        return self.db.query(Booking).filter(
            Booking.hotel_id == hotel_id,
            Booking.is_paid == False,
            Booking.status.notin_(["cancelled", "no_show"]),
        ).all()

    def get_revenue_by_payment_method(
        self,
        hotel_id: int,
        start_date: date,
        end_date: date,
    ) -> dict:
        """Get revenue breakdown by payment method."""
        results = self.db.query(
            Payment.method,
            func.sum(Payment.amount),
        ).join(
            Booking, Payment.booking_id == Booking.id
        ).filter(
            Booking.hotel_id == hotel_id,
            func.date(Payment.paid_at) >= start_date,
            func.date(Payment.paid_at) <= end_date,
            Payment.status == PaymentStatus.COMPLETED,
        ).group_by(Payment.method).all()

        return {method.value: float(amount) for method, amount in results}

    def generate_invoice(self, booking_id: int) -> dict:
        """Generate invoice data for a booking."""
        booking = self.db.query(Booking).filter(Booking.id == booking_id).first()
        if not booking:
            raise ValueError("Booking not found")

        from app.models.guest import Guest
        from app.models.room import Room, RoomType
        from app.models.hotel import Hotel

        guest = self.db.query(Guest).filter(Guest.id == booking.guest_id).first()
        room = self.db.query(Room).filter(Room.id == booking.room_id).first()
        room_type = self.db.query(RoomType).filter(RoomType.id == room.room_type_id).first()
        hotel = self.db.query(Hotel).filter(Hotel.id == booking.hotel_id).first()

        payments = self.db.query(Payment).filter(
            Payment.booking_id == booking_id,
            Payment.status.in_([PaymentStatus.COMPLETED, PaymentStatus.PARTIALLY_REFUNDED]),
        ).all()

        nights = (booking.check_out_date - booking.check_in_date).days

        return {
            "invoice_number": f"INV-{booking.booking_ref}",
            "booking_ref": booking.booking_ref,
            "hotel": {
                "name": hotel.name,
                "address": hotel.address,
                "city": hotel.city,
                "phone": hotel.phone,
                "email": hotel.email,
                "gst_number": hotel.gst_number,
            },
            "guest": {
                "name": f"{guest.first_name} {guest.last_name}",
                "email": guest.email,
                "phone": guest.phone,
                "address": guest.address,
            },
            "room": {
                "number": room.room_number,
                "type": room_type.name,
            },
            "stay": {
                "check_in": str(booking.check_in_date),
                "check_out": str(booking.check_out_date),
                "nights": nights,
                "adults": booking.adults,
                "children": booking.children,
            },
            "charges": {
                "room_rate": float(booking.room_rate),
                "room_total": float(booking.room_rate * nights),
                "extra_bed_charge": float(booking.extra_bed_charge),
                "subtotal": float(booking.subtotal),
                "discount": float(booking.discount_amount),
                "tax": float(booking.tax_amount),
                "additional_charges": booking.additional_charges or [],
                "total": float(booking.total_amount),
            },
            "payments": [
                {
                    "ref": p.payment_ref,
                    "amount": float(p.amount),
                    "method": p.method.value,
                    "date": str(p.paid_at),
                }
                for p in payments
            ],
            "balance_due": float(booking.total_amount) - float(booking.amount_paid),
            "is_paid": booking.is_paid,
        }
